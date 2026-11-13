"""微信绑定：生成绑定码 / 状态 / 解绑。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core import binding
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/api/bind", tags=["bind"])


@router.post("/code", response_model=schemas.BindCodeOut)
def gen_code(user: models.User = Depends(get_current_user)):
    return schemas.BindCodeOut(bind_code=binding.issue(user.id))


@router.get("/status")
def status(user: models.User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    b = binding.get_binding(db, user.id)
    return {"bound": bool(b), "wx_id": b.wx_id if b else None,
            "wx_nick": b.wx_nick if b else ""}


@router.post("/unbind")
def unbind(user: models.User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    b = db.get(models.WechatBinding, user.id)
    if b:
        db.delete(b)
        db.commit()
    return {"ok": True}
