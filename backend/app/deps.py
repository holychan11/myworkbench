"""FastAPI 依赖：数据库会话、当前用户、管理员校验。"""
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from . import models, security
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(default=""),
                     db: Session = Depends(get_db)) -> models.User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    payload = security.decode_token(authorization[7:])
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    user = db.get(models.User, payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已停用")
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
