"""MyWorkbench FastAPI 入口。"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models, security
from .config import settings
from .core.dispatcher import Dispatcher
from .database import SessionLocal, init_db
from .gateway.factory import create_gateway
from .stock.base import discover
from .stock.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("myworkbench")


def _ensure_admin() -> None:
    db = SessionLocal()
    try:
        exists = db.query(models.User).filter_by(username=settings.ADMIN_USERNAME).first()
        if not exists:
            db.add(models.User(
                username=settings.ADMIN_USERNAME,
                password_hash=security.hash_password(settings.ADMIN_PASSWORD),
                role="admin"))
            db.commit()
            log.info("已创建默认管理员账号: %s", settings.ADMIN_USERNAME)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    discover()                      # 注册 A股策略
    _ensure_admin()
    gateway = create_gateway()
    app.state.gateway = gateway
    app.state.dispatcher = Dispatcher(gateway)
    start_scheduler(gateway)
    log.info("MyWorkbench 已启动，网关通道 = %s", settings.GATEWAY_TYPE)
    yield
    stop_scheduler()


app = FastAPI(title="MyWorkbench", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "gateway": settings.GATEWAY_TYPE,
            "version": "1.0.0"}


# 路由注册
from .router import (admin, auth, bind, gateway_router, logs,  # noqa: E402
                     models_router, onebot_router, stock_router)

app.include_router(auth.router)
app.include_router(models_router.router)
app.include_router(bind.router)
app.include_router(stock_router.router)
app.include_router(admin.router)
app.include_router(logs.router)
app.include_router(gateway_router.router)
app.include_router(onebot_router.router)
