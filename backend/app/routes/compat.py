from __future__ import annotations

"""
Compatibility routes — exact paths from the existing OpenAPI contract
so the generated @workspace/api-client-react hooks work without changes.
"""
import bson
from fastapi import APIRouter, Depends, Query, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.connection import get_db, check_db_health
from app.analytics.skill_demand import get_skill_demand
from app.analytics.forecasting import get_skill_forecast
from app.analytics.district_intelligence import list_districts, get_district

router = APIRouter(tags=["Compatibility"])


# ── Health ─────────────────────────────────────────────────────────────────────
@router.get("/healthz")
async def health_check():
    db_ok = await check_db_health()
    return {
        "status": "ok",
        "database": "connected" if db_ok else "disconnected",
        "service": "kaushalya-api",
    }


# ── Government dashboard ───────────────────────────────────────────────────────
@router.get("/dashboard/government")
async def govt_dashboard_compat(
    district: str = Query(default="All districts"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.dashboard import government_dashboard
    return await government_dashboard(district=district, db=db)


# ── Trainee dashboard ─────────────────────────────────────────────────────────
@router.get("/dashboard/trainee/{trainee_id}")
async def trainee_dashboard_compat(
    trainee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.dashboard import trainee_dashboard
    return await trainee_dashboard(trainee_id=trainee_id, db=db)


# ── Districts ─────────────────────────────────────────────────────────────────
@router.get("/districts")
async def list_districts_compat(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await list_districts(db)


@router.get("/districts/{district}")
async def get_district_compat(district: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    from fastapi import HTTPException
    result = await get_district(district, db)
    if not result:
        raise HTTPException(status_code=404, detail="District not found")
    return result


# ── Skill demand & forecast ────────────────────────────────────────────────────
@router.get("/skill-demand")
async def skill_demand_compat(
    industry: str = Query(default=""),
    district: str = Query(default=""),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await get_skill_demand(db, industry or None, district or None)


@router.get("/forecast")
async def forecast_compat(db: AsyncIOMotorDatabase = Depends(get_db)):
    return await get_skill_forecast(db)


# ── Trainees ───────────────────────────────────────────────────────────────────
@router.get("/trainees/{trainee_id}")
async def get_trainee_compat(
    trainee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.trainees import get_trainee
    return await get_trainee(trainee_id, db)


@router.patch("/trainees/{trainee_id}")
async def patch_trainee_compat(
    trainee_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from fastapi import HTTPException
    from app.schemas.trainee import TraineeProfileUpdate
    from app.routes.trainees import _get_trainee_skills, _build_trainee_response
    from app.services.employability import calculate_employability
    from app.models.base import utcnow

    body_data = await request.json()
    body = TraineeProfileUpdate(**body_data)
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    await db.trainee_profiles.update_one({"user_id": trainee_id}, {"$set": update})
    profile = await db.trainee_profiles.find_one({"user_id": trainee_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Trainee not found")
    skills = await _get_trainee_skills(trainee_id, db)
    emp = await calculate_employability(trainee_id, db)
    return _build_trainee_response(profile, skills, emp)


# ── Skills ─────────────────────────────────────────────────────────────────────
@router.get("/skills")
async def list_skills_compat(
    search: str = Query(default=""),
    category: str = Query(default=""),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.skills import list_skills
    return await list_skills(search=search, category=category, industry="", skip=0, limit=100, db=db)


# ── Training programs ──────────────────────────────────────────────────────────
@router.get("/training-programs")
async def list_programs_compat(db: AsyncIOMotorDatabase = Depends(get_db)):
    from app.routes.training import list_programs
    return await list_programs(industry="", location="", db=db)


@router.post("/training-programs", status_code=201)
async def create_program_compat(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.training import create_program
    from app.schemas.training import TrainingProgramCreate
    body_data = await request.json()
    valid_fields = TrainingProgramCreate.model_fields.keys()
    body = TrainingProgramCreate(**{k: v for k, v in body_data.items() if k in valid_fields})
    # Try to get authenticated user from Authorization header
    auth_header = request.headers.get("authorization", "")
    user = None
    if auth_header.startswith("Bearer "):
        try:
            from app.auth.jwt import decode_token
            payload = decode_token(auth_header.split(" ", 1)[1])
            uid = payload.get("user_id")
            if uid:
                user = await db.users.find_one({"_id": bson.ObjectId(uid)})
        except Exception:
            pass
    if user is None:
        user = {"_id": bson.ObjectId(), "role": "TRAINING_INSTITUTE"}
    return await create_program(body, user, db)


# ── Jobs ───────────────────────────────────────────────────────────────────────
@router.get("/jobs")
async def list_jobs_compat(
    search: str = Query(default=""),
    location: str = Query(default=""),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.jobs import list_jobs
    return await list_jobs(search=search, location=location, industry="", status="open", skip=0, limit=50, db=db)


@router.post("/jobs", status_code=201)
async def create_job_compat(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.jobs import create_job
    from app.schemas.job import JobCreate
    from app.auth.dependencies import get_optional_user
    body_data = await request.json()
    valid_fields = JobCreate.model_fields.keys()
    body = JobCreate(**{k: v for k, v in body_data.items() if k in valid_fields})
    # Try to get authenticated user from Authorization header
    auth_header = request.headers.get("authorization", "")
    user = None
    if auth_header.startswith("Bearer "):
        try:
            from app.auth.jwt import decode_token
            payload = decode_token(auth_header.split(" ", 1)[1])
            uid = payload.get("user_id")
            if uid:
                user = await db.users.find_one({"_id": bson.ObjectId(uid)})
        except Exception:
            pass
    if user is None:
        user = {"_id": bson.ObjectId(), "role": "EMPLOYER"}
    return await create_job(body, user, db)


@router.post("/jobs/{job_id}/apply", status_code=201)
async def apply_job_compat(
    job_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.jobs import apply_to_job
    from app.schemas.job import JobApplicationCreate
    body_data = await request.json()
    trainee_id = body_data.get("traineeId", body_data.get("trainee_id", ""))
    note = body_data.get("note", "")
    # Try to get authenticated user — use their ID if no traineeId supplied
    if not trainee_id:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.auth.jwt import decode_token
                payload = decode_token(auth_header.split(" ", 1)[1])
                trainee_id = payload.get("user_id", "demo")
            except Exception:
                trainee_id = "demo"
    body = JobApplicationCreate(trainee_id=trainee_id or "demo", note=note)
    fake_user = {"_id": bson.ObjectId(), "role": "TRAINEE"}
    return await apply_to_job(job_id, body, fake_user, db)


@router.get("/job-matches/{trainee_id}")
async def job_matches_compat(
    trainee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.jobs import job_matches
    return await job_matches(trainee_id, db)


# ── Recommendations ────────────────────────────────────────────────────────────
@router.get("/recommendations/{trainee_id}")
async def recommendations_compat(
    trainee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    from app.routes.recommendations import get_recommendations
    return await get_recommendations(trainee_id, db)


# ── Career advice (original OpenAPI path) ─────────────────────────────────────
@router.post("/assistant/career-advice")
async def career_advice_compat(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Exact path the frontend's generated hook calls — now backed by Gemini."""
    from app.routes.ai_routes import LegacyCareerRequest, legacy_career_advice
    body_data = await request.json()
    trainee_id = body_data.get("traineeId", body_data.get("trainee_id", ""))
    question = body_data.get("question", "")
    body = LegacyCareerRequest(traineeId=trainee_id, question=question)
    return await legacy_career_advice(body, db)
