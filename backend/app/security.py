"""密码哈希、JWT、API Key 加密（Fernet）。"""
import uuid
from datetime import datetime, timedelta

import bcrypt
import jwt
from cryptography.fernet import Fernet, InvalidToken

from .config import settings


# ---------- 密码 ----------
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


# ---------- JWT ----------
def create_access_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


# ---------- API Key 加密（Fernet） ----------
class KeyVault:
    """主密钥来自 settings.MASTER_KEY；密文入库，明文只在内存短暂存在。"""

    def __init__(self):
        self._fernet = Fernet(settings.MASTER_KEY.encode())

    def encrypt(self, plain: str) -> str:
        return self._fernet.encrypt(plain.encode()).decode()

    def decrypt(self, token: str) -> str | None:
        try:
            return self._fernet.decrypt(token.encode()).decode()
        except (InvalidToken, ValueError):
            return None


vault = KeyVault()


def mask_key(plain: str) -> str:
    """生成掩码，如 sk-****abcd，前端永不回显明文。"""
    if len(plain) <= 8:
        return "*" * len(plain)
    return f"{plain[:3]}****{plain[-4:]}"


def new_id() -> str:
    return uuid.uuid4().hex
