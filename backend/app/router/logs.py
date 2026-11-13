"""当前用户执行/审计日志。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
def my_logs(user: models.User = Depends(get_current_user),
            db: Session = Depends(get_db), limit: int = 200):
    rows = (db.query(models.TaskLog)
            .filter_by(user_id=user.id)
            .order_by(models.TaskLog.id.desc()).limit(min(limit, 500)).all())
    return [{"id": r.id, "kind": r.kind, "cmd": r.cmd, "risk": r.risk,
             "status": r.status, "result": r.result, "created_at": str(r.created_at)}
            for r in rows]
