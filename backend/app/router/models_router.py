"""用户模型配置：动态添加/删除 LLM + 连通性测试。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..llm.manager import ModelManager

router = APIRouter(prefix="/api/models", tags=["models"])

mm = ModelManager()


@router.get("")
def list_models(user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return mm.list_models(db, user.id)


@router.post("")
def add_model(data: schemas.ModelIn, user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    m = mm.add_model(db, user.id, data)
    return mm._to_out(m)


@router.delete("/{model_id}")
def delete_model(model_id: str, user: models.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    if not mm.delete_model(db, user.id, model_id):
        raise HTTPException(status_code=404, detail="模型不存在")
    return {"ok": True}


@router.post("/{model_id}/default")
def set_default(model_id: str, user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    if not mm.set_default(db, user.id, model_id):
        raise HTTPException(status_code=404, detail="模型不存在")
    return {"ok": True}


@router.post("/{model_id}/test", response_model=schemas.ModelTestOut)
def test_model(model_id: str, user: models.User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    ok, reply = mm.test(db, user.id, model_id)
    return schemas.ModelTestOut(ok=ok, reply=reply)
