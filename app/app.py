from fastapi import FastAPI, Request
from app.config import get_config
from app.context import get_context
from app.log import get_log
from app.routers import user_routers
from app.postgres import Base, sessionmanager
from contextlib import asynccontextmanager
from time import time
from uuid import uuid4

cfg = get_config()
log = get_log()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with sessionmanager.async_engine.begin() as conn:
        from app.models.user_models import User
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=cfg.APP_VERSION)
app.include_router(user_routers.router, prefix=cfg.APP_PREFIX)


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    ctx = get_context()
    ctx.request_start_time = time()
    ctx.trace_request_uuid = str(uuid4())

    log.debug("Request received; module=app; function=middleware_handler; method=%s; url=%s; headers=%s;" % (
        request.method, str(request.url), str(request.headers)))

    response = await call_next(request)

    elapsed_time = time() - ctx.request_start_time
    log.debug("Response sent; module=app; function=middleware_handler; elapsed_time=%s; status=%s; headers=%s;" % (
        "{0:.10f}".format(elapsed_time), response.status_code,
        str(response.headers.raw)))

    return response
