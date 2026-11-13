"""认证：注册 / 登录 / 当前用户。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_out(user: models.User) -> schemas.TokenOut:
    return schemas.TokenOut(
        access_token=security.create_access_token(user.id, user.role),
        role=user.role, username=user.username, user_id=user.id)


@router.post("/register", response_model=schemas.TokenOut)
def register(data: schemas.RegisterIn, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(username=data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models.User(
        username=data.username,
        password_hash=security.hash_password(data.password),
        role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_out(user)


@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=data.username).first()
    if not user or not security.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")
    return _token_out(user)


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
