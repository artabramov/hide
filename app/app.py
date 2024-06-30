from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.config import get_config
from app.context import get_context
from app.log import get_log
from app.routers import static_routers
from app.routers import user_routers
from app.postgres import Base, sessionmanager
from app.errors import E, Msg
from contextlib import asynccontextmanager
from pydantic import ValidationError
from time import time
from uuid import uuid4

cfg = get_config()
log = get_log()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=cfg.APP_VERSION)
app.include_router(static_routers.router)
app.include_router(user_routers.router, prefix=cfg.APP_PREFIX)


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    ctx = get_context()
    ctx.request_start_time = time()
    ctx.trace_request_uuid = str(uuid4())

    log.debug("Request received; module=app; function=middleware_handler; elapsed_time=0; method=%s; url=%s; headers=%s;" % (
        request.method, str(request.url), str(request.headers)))

    response = await call_next(request)

    elapsed_time = time() - ctx.request_start_time
    log.debug("Response sent; module=app; function=middleware_handler; elapsed_time=%s; status=%s; headers=%s;" % (
        "{0:.10f}".format(elapsed_time), response.status_code,
        str(response.headers.raw)))

    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception):
    ctx = get_context()
    elapsed_time = time() - ctx.request_start_time

    if isinstance(e, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        error_details = e.errors()

    elif isinstance(e, (FileNotFoundError, FileExistsError)):
        status_code=status.HTTP_400_BAD_REQUEST,
        error_details = {"detail": Msg.BAD_REQUEST.value}

    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_details = {"detail": Msg.SERVER_ERROR.value}

    log.error("Request failed; module=app; function=exception_handler; elapsed_time=%s; status_code=%s; e=%s;" % (elapsed_time, status_code, str(e)))
    response_content = jsonable_encoder({"detail": error_details})
    return JSONResponse(status_code=status_code, content=response_content)
