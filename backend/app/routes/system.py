from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.connection import get_db
from app.services.email_service import email_service
from app.auth.dependencies import require_super_admin
from app.config.settings import get_settings
from pydantic import EmailStr, BaseModel

router = APIRouter(prefix="/system", tags=["System"])

class TestEmailRequest(BaseModel):
    email: EmailStr

@router.post("/test-email")
async def test_email(body: TestEmailRequest, background_tasks: BackgroundTasks, user: dict = Depends(require_super_admin())):
    if not get_settings().smtp_configured:
        raise HTTPException(status_code=503, detail="SMTP is not configured")
    email_service.send_test_email(background_tasks, body.email, str(user["_id"]))
    return {"success": True, "message": "Test email queued successfully."}

@router.get("/email-status")
async def email_status(db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(require_super_admin())):
    settings = get_settings()
    logs_cursor = db.email_logs.find({}, {"metadata": 0}).sort("sent_at", -1).limit(50)
    logs = await logs_cursor.to_list(length=50)
    
    total = await db.email_logs.count_documents({})
    failed = await db.email_logs.count_documents({"status": "FAILED"})
    success = await db.email_logs.count_documents({"status": "SENT"})
    
    # Format logs for response
    formatted_logs = []
    for log in logs:
        log["_id"] = str(log["_id"])
        formatted_logs.append(log)
        
    return {
        "configured": settings.smtp_configured,
        "host": settings.SMTP_HOST if settings.smtp_configured else None,
        "port": settings.SMTP_PORT if settings.smtp_configured else None,
        "tls": settings.SMTP_USE_TLS,
        "status": "ready" if settings.smtp_configured else "not_configured",
        "metrics": {
            "total": total,
            "success": success,
            "failed": failed
        },
        "logs": formatted_logs
    }
