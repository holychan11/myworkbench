"""审计日志：所有操作留痕。"""
from sqlalchemy.orm import Session

from .. import models


def log(db: Session, user_id: str, kind: str, cmd: str = "",
        risk: str = "", status: str = "ok", result: str = "") -> None:
    db.add(models.TaskLog(
        user_id=user_id, kind=kind, cmd=(cmd or "")[:2000],
        risk=risk, status=status, result=(result or "")[:4000]))
    db.commit()
