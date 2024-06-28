from fastapi import FastAPI
from app.config import get_config
from app.routers import user_routers
from app.postgres import Base, sessionmanager
from contextlib import asynccontextmanager

cfg = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with sessionmanager.async_engine.begin() as conn:
        from app.models.user_models import User
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=cfg.APP_VERSION)
app.include_router(user_routers.router, prefix=cfg.APP_PREFIX)
