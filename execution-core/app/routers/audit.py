from fastapi import APIRouter, Query
from app.models.audit_log import get_audit_log

router = APIRouter()


@router.get("/logs")
async def get_audit_logs(limit: int = Query(50, ge=1, le=500)):
    log = get_audit_log()
    return {"logs": log.recent(limit)}
