from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, get_optional_user
from app.database.connection import get_db
from app.schemas.job import JobCreate, JobUpdate, JobApplicationCreate
from app.services.job_matching import get_job_matches
from app.services.email_service import email_service
from app.utils.serializer import serialize_doc, serialize_docs
from app.models.base import utcnow

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Jobs"])

_AGO = {0: "Today", 1: "1 day ago", 2: "2 days ago", 3: "3 days ago", 4: "4 days ago", 5: "5 days ago", 6: "6 days ago"}

class ApplicationStatusUpdate(BaseModel):
    status: str

def _fmt_posted(dt) -> str:
    if not dt:
        return "Recently"
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if hasattr(dt, "tzinfo") and dt.tzinfo:
        delta = (now - dt).days
    else:
        delta = 0
    return _AGO.get(delta, f"{delta} days ago") if delta <= 6 else f"{delta} days ago"

def _job_doc(doc: dict) -> dict:
    s = serialize_doc(doc) or {}
    return {
        "id": s.get("id", ""),
        "title": s.get("title", ""),
        "company": s.get("company", ""),
        "industry": s.get("industry", ""),
        "location": s.get("location", ""),
        "jobType": s.get("job_type", "Full-time"),
        "experience": s.get("experience", ""),
        "salary": s.get("salary", ""),
        "requiredSkills": s.get("required_skills", []),
        "posted": _fmt_posted(doc.get("posted_at")),
        "deadline": s.get("deadline", ""),
        "applicants": s.get("applicants", 0),
        "match": s.get("match", 0),
        "status": s.get("status", "open"),
    }

@router.get("/jobs")
async def list_jobs(
    search: str = Query(default=""),
    location: str = Query(default=""),
    industry: str = Query(default=""),
    status: str = Query(default="open"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    q: dict = {}
    if status:
        q["status"] = status
    if search:
        q["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}},
        ]
    if location:
        q["location"] = {"$regex": location, "$options": "i"}
    if industry:
        q["industry"] = {"$regex": industry, "$options": "i"}

    cursor = db.jobs.find(q).sort("posted_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_job_doc(d) for d in docs]

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_doc(doc)

@router.post("/jobs", status_code=201)
async def create_job(
    body: JobCreate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    now = utcnow()
    doc = {
        **body.model_dump(),
        "employer_id": str(user["_id"]),
        "applicants": 0,
        "match": 0,
        "status": "open",
        "posted_at": now,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.jobs.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _job_doc(doc)

@router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    body: JobUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("employer_id") != str(user["_id"]) and user.get("role") not in ("SUPER_ADMIN",):
        raise HTTPException(status_code=403, detail="Forbidden")
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    result = await db.jobs.find_one_and_update(
        {"_id": ObjectId(job_id)}, {"$set": update}, return_document=True
    )
    return _job_doc(result)

@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(
    job_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("employer_id") != str(user["_id"]) and user.get("role") not in ("SUPER_ADMIN",):
        raise HTTPException(status_code=403, detail="Forbidden")
    await db.jobs.delete_one({"_id": ObjectId(job_id)})

@router.post("/jobs/{job_id}/apply", status_code=201)
async def apply_to_job(
    job_id: str,
    body: JobApplicationCreate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    trainee_id = body.trainee_id or str(user["_id"])
    trainee = await db.users.find_one({"_id": ObjectId(trainee_id)})
    
    existing = await db.job_applications.find_one({"job_id": job_id, "trainee_id": trainee_id})
    if existing:
        return serialize_doc(existing)

    now = utcnow()
    doc = {
        "job_id": job_id,
        "trainee_id": trainee_id,
        "status": "submitted",
        "note": body.note,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.job_applications.insert_one(doc)
    doc["_id"] = result.inserted_id
    await db.jobs.update_one({"_id": ObjectId(job_id)}, {"$inc": {"applicants": 1}})
    
    # Send email notification to trainee
    if trainee:
        email_service.send_job_application_email(background_tasks, trainee.get("email"), trainee.get("name"),
            {"Job Title": job.get("title"), "Company": job.get("company"), "Status": "Application submitted"}, str(trainee["_id"]))
        
    employer = await db.users.find_one({"_id": ObjectId(job.get("employer_id"))})
    if employer:
        email_service.send_job_application_email(background_tasks, employer.get("email"), employer.get("name"),
            {"Job Title": job.get("title"), "Applicant": trainee.get("name") if trainee else "Unknown"}, str(employer["_id"]))
        
    return serialize_doc(doc)

@router.get("/jobs/{job_id}/applications")
async def get_job_applications(
    job_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("employer_id") != str(user["_id"]) and user.get("role") not in ("SUPER_ADMIN", "GOVERNMENT_ADMIN"):
        raise HTTPException(status_code=403, detail="Forbidden")
    cursor = db.job_applications.find({"job_id": job_id})
    docs = await cursor.to_list(length=200)
    return serialize_docs(docs)

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    body: ApplicationStatusUpdate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    app_doc = await db.job_applications.find_one({"_id": ObjectId(application_id)})
    if not app_doc:
        raise HTTPException(status_code=404, detail="Application not found")
        
    job = await db.jobs.find_one({"_id": ObjectId(app_doc["job_id"])})
    if job.get("employer_id") != str(user["_id"]) and user.get("role") not in ("SUPER_ADMIN",):
        raise HTTPException(status_code=403, detail="Forbidden")
        
    await db.job_applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": body.status, "updated_at": utcnow()}}
    )
    
    trainee = await db.users.find_one({"_id": ObjectId(app_doc["trainee_id"])})
    if trainee:
        details = {"Job Title": job.get("title"), "Company": job.get("company"), "Next Steps": "Check your KAUSHALYA dashboard."}
        if body.status.lower() in ("selected", "accepted", "shortlisted"):
            email_service.send_job_selection_email(background_tasks, trainee.get("email"), trainee.get("name"), details, str(trainee["_id"]))
        elif body.status.lower() in ("rejected", "declined"):
            email_service.send_job_rejection_email(background_tasks, trainee.get("email"), trainee.get("name"), details, str(trainee["_id"]))
        
    return {"message": "Status updated successfully"}

@router.get("/job-matches/{trainee_id}")
async def job_matches(
    trainee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    matches = await get_job_matches(trainee_id, db)
    result = []
    for m in matches:
        result.append({
            "id": m["id"],
            "title": m["title"],
            "company": m["company"],
            "industry": m["industry"],
            "location": m["location"],
            "jobType": m["job_type"],
            "experience": m["experience"],
            "salary": m["salary"],
            "requiredSkills": m["required_skills"],
            "posted": m["posted"],
            "deadline": m["deadline"],
            "applicants": m["applicants"],
            "match": m["match"],
            "matchingSkills": m["matching_skills"],
            "missingSkills": m["missing_skills"],
            "matchReason": m["match_reason"],
        })
    return result
