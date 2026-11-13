"""管理端：用户列表 / 全量审计日志（仅 admin）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def users(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(models.User).order_by(models.User.created_at).all()
    return [{"id": u.id, "username": u.username, "role": u.role,
             "is_active": u.is_active, "created_at": str(u.created_at)} for u in rows]


@router.get("/logs")
def logs(admin: models.User = Depends(require_admin), db: Session = Depends(get_db),
         limit: int = 100):
    rows = (db.query(models.TaskLog)
            .order_by(models.TaskLog.id.desc()).limit(min(limit, 500)).all())
    return [{"id": r.id, "user_id": r.user_id, "kind": r.kind, "cmd": r.cmd,
             "risk": r.risk, "status": r.status, "result": r.result,
             "created_at": str(r.created_at)} for r in rows]
