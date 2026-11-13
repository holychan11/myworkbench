"""模型管理器：动态增删模型 + OpenAI 兼容调用 + 密钥加密。"""
from sqlalchemy.orm import Session

from .. import models, schemas
from ..security import KeyVault, mask_key, vault
from ..core.audit import log


class ModelManager:
    def __init__(self, kv: KeyVault = vault):
        self._kv = kv

    # ---------- CRUD ----------
    def add_model(self, db: Session, user_id: str, data: schemas.ModelIn) -> models.UserModel:
        if data.is_default:
            self._clear_default(db, user_id)
        m = models.UserModel(
            user_id=user_id,
            display_name=data.display_name,
            provider=data.provider,
            base_url=data.base_url.rstrip("/"),
            api_key_enc=self._kv.encrypt(data.api_key),   # 落库前加密
            default_model=data.default_model,
            temperature=data.temperature,
            is_default=data.is_default,
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        log(db, user_id, "llm", cmd=f"add_model {data.provider}/{data.default_model}",
            status="ok")
        return m

    def list_models(self, db: Session, user_id: str) -> list[dict]:
        rows = (db.query(models.UserModel)
                .filter_by(user_id=user_id)
                .order_by(models.UserModel.is_default.desc(), models.UserModel.created_at)
                .all())
        return [self._to_out(r) for r in rows]

    def delete_model(self, db: Session, user_id: str, model_id: str) -> bool:
        m = (db.query(models.UserModel)
             .filter_by(id=model_id, user_id=user_id).first())
        if not m:
            return False
        db.delete(m)
        db.commit()
        log(db, user_id, "llm", cmd=f"delete_model {m.display_name}", status="ok")
        return True

    def set_default(self, db: Session, user_id: str, model_id: str) -> bool:
        m = (db.query(models.UserModel)
             .filter_by(id=model_id, user_id=user_id).first())
        if not m:
            return False
        self._clear_default(db, user_id)
        m.is_default = True
        db.commit()
        return True

    def _clear_default(self, db: Session, user_id: str) -> None:
        db.query(models.UserModel).filter_by(user_id=user_id).update({"is_default": False})

    def _to_out(self, m: models.UserModel) -> dict:
        plain = self._kv.decrypt(m.api_key_enc) or ""
        return {
            "id": m.id, "display_name": m.display_name, "provider": m.provider,
            "base_url": m.base_url, "api_key_masked": mask_key(plain),
            "default_model": m.default_model, "temperature": m.temperature,
            "is_default": m.is_default, "enabled": m.enabled,
        }

    # ---------- 调用 ----------
    def _client(self, m: models.UserModel):
        from openai import OpenAI
        key = self._kv.decrypt(m.api_key_enc)
        if not key:
            raise PermissionError("模型密钥无法解密（主密钥可能已轮换）")
        return OpenAI(api_key=key, base_url=m.base_url)

    def chat(self, m: models.UserModel, messages: list[dict]) -> str:
        client = self._client(m)
        resp = client.chat.completions.create(
            model=m.default_model, messages=messages,
            temperature=m.temperature)
        return resp.choices[0].message.content or ""

    def chat_for_user(self, db: Session, user_id: str, messages: list[dict]) -> str:
        m = (db.query(models.UserModel)
             .filter_by(user_id=user_id, enabled=True)
             .order_by(models.UserModel.is_default.desc(), models.UserModel.created_at)
             .first())
        if not m:
            raise ValueError("尚未配置可用模型，请先在 Web 端添加")
        return self.chat(m, messages)

    def test(self, db: Session, user_id: str, model_id: str) -> tuple[bool, str]:
        m = (db.query(models.UserModel)
             .filter_by(id=model_id, user_id=user_id).first())
        if not m:
            return False, "模型不存在"
        try:
            reply = self.chat(m, [{"role": "user", "content": "请回复两个字：正常"}])
            log(db, user_id, "llm", cmd=f"test {m.display_name}", status="ok")
            return True, reply
        except Exception as e:  # noqa: BLE001
            log(db, user_id, "llm", cmd=f"test {m.display_name}",
                status="failed", result=str(e)[:500])
            return False, str(e)[:500]
