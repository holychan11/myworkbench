"""危险操作二次确认状态机（SQLite 实现，expires_at 模拟 TTL）。"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import models
from ..core.audit import log

CONFIRM_TTL_SECONDS = 120


def create(db: Session, user_id: str, cmd: str, risk: str) -> models.PendingConfirmation:
    now = datetime.utcnow()
    c = models.PendingConfirmation(
        user_id=user_id, cmd=cmd, risk=risk,
        created_at=now, expires_at=now + timedelta(seconds=CONFIRM_TTL_SECONDS))
    db.add(c)
    db.commit()
    db.refresh(c)
    log(db, user_id, "confirm", cmd=cmd, risk=risk, status="pending")
    return c


def latest_pending(db: Session, user_id: str) -> models.PendingConfirmation | None:
    now = datetime.utcnow()
    c = (db.query(models.PendingConfirmation)
         .filter_by(user_id=user_id, status="pending")
         .order_by(models.PendingConfirmation.created_at.desc())
         .first())
    if c and c.expires_at < now:
        c.status = "expired"
        db.commit()
        return None
    return c


def resolve(db: Session, user_id: str, confirm_id: str, approve: bool):
    """返回 (确认对象 | None, 提示 | None)。一次性令牌，用后即失效。"""
    now = datetime.utcnow()
    c = (db.query(models.PendingConfirmation)
         .filter_by(id=confirm_id, user_id=user_id, status="pending").first())
    if not c:
        return None, "确认请求不存在或已处理"
    if c.expires_at < now:
        c.status = "expired"
        db.commit()
        return None, "确认请求已过期（120 秒）"
    c.status = "approved" if approve else "rejected"
    db.commit()
    log(db, user_id, "confirm", cmd=c.cmd, risk=c.risk,
        status="approved" if approve else "rejected")
    return c, None


def expire_stale(db: Session) -> int:
    now = datetime.utcnow()
    n = (db.query(models.PendingConfirmation)
         .filter(models.PendingConfirmation.status == "pending",
                 models.PendingConfirmation.expires_at < now)
         .update({"status": "expired"}))
    db.commit()
    return n
