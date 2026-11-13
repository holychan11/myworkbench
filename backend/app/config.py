"""集中配置：环境变量优先，缺失时自动生成并持久化到 data/ 目录（开箱即用）。"""
import os
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent          # myworkbench/backend
ROOT_DIR = BASE_DIR.parent                                  # myworkbench/
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 加载项目根目录的 .env（若存在）；系统环境变量优先于 .env
load_dotenv(ROOT_DIR / ".env")


def _load_or_create(env_name: str, filename: str, generator) -> str:
    """优先读环境变量；否则读 data/<filename>；再否则生成并落盘。"""
    val = os.getenv(env_name)
    if val:
        return val
    f = DATA_DIR / filename
    if f.exists():
        return f.read_text(encoding="utf-8").strip()
    val = generator()
    f.write_text(val, encoding="utf-8")
    return val


class Settings:
    # ---- 安全 ----
    MASTER_KEY: str = _load_or_create(
        "MASTER_KEY", "master.key", lambda: Fernet.generate_key().decode())
    JWT_SECRET: str = _load_or_create(
        "JWT_SECRET", "jwt.secret", lambda: os.urandom(32).hex())
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "720"))  # 12h

    # ---- 数据库 ----
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(DATA_DIR / 'myworkbench.db').as_posix()}")

    # ---- 微信网关：console(本地测试) | wecom(企业微信) | wcf(WeChatFerry) ----
    GATEWAY_TYPE: str = os.getenv("GATEWAY_TYPE", "console")
    WCF_HOST: str = os.getenv("WCF_HOST", "127.0.0.1")
    WCF_PORT: int = int(os.getenv("WCF_PORT", "10086"))
    WECOM_CORP_ID: str = os.getenv("WECOM_CORP_ID", "")
    WECOM_AGENT_ID: str = os.getenv("WECOM_AGENT_ID", "")
    WECOM_SECRET: str = os.getenv("WECOM_SECRET", "")

    # ---- QQ（OneBot 11 协议，通过 NapCat / LLOneBot 等框架）----
    # NapCat 的 HTTP API 地址（发消息用）；收消息由 NapCat 上报到 /onebot/event
    ONE_BOT_HTTP_URL: str = os.getenv("ONE_BOT_HTTP_URL", "http://127.0.0.1:3000")

    # ---- A股调度 ----
    SCHEDULE_HOUR: int = int(os.getenv("SCHEDULE_HOUR", "8"))
    SCHEDULE_MINUTE: int = int(os.getenv("SCHEDULE_MINUTE", "30"))
    TZ: str = os.getenv("TZ", "Asia/Shanghai")

    # ---- 默认管理员（首次启动创建）----
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123456")

    # ---- 电脑操作沙箱 ----
    EXEC_WORKDIR: str = os.getenv(
        "EXEC_WORKDIR", str(ROOT_DIR / "workspace"))
    EXEC_TIMEOUT: float = float(os.getenv("EXEC_TIMEOUT", "60"))
    EXEC_MAX_OUTPUT: int = int(os.getenv("EXEC_MAX_OUTPUT", "4000"))


settings = Settings()

# 保证沙箱工作目录存在
Path(settings.EXEC_WORKDIR).mkdir(parents=True, exist_ok=True)
