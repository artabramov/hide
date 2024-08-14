from fastapi import FastAPI, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.config import get_config
from app.context import get_context
from app.log import get_log
from app.routers import (
    static_routers, user_routers, collection_routers, document_routers,
    system_routers)
from app.database import Base, sessionmanager, get_session
from app.errors import Msg
from contextlib import asynccontextmanager
from pydantic import ValidationError
from time import time
from uuid import uuid4
import os
import importlib.util
import inspect
from app.hooks import HookAction, Hook
from app.cache import get_cache
from fastapi.staticfiles import StaticFiles

cfg = get_config()
ctx = get_context()
log = get_log()


async def after_startup(session=Depends(get_session),
                        cache=Depends(get_cache)):
    hook = Hook(session, cache)
    await hook.execute(HookAction.after_startup)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ctx.hooks = {}

    filenames = [file + ".py" for file in cfg.PLUGINS_ENABLED]
    for filename in filenames:
        module_name = filename.split(".")[0]
        module_path = os.path.join(cfg.PLUGINS_BASE_PATH, filename)

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            func_names = [attr for attr in dir(module)
                          if inspect.isfunction(getattr(module, attr))]

            for func_name in func_names:
                func = getattr(module, func_name)
                if func_name not in ctx.hooks:
                    ctx.hooks[func_name] = [func]
                else:
                    ctx.hooks[func_name].append(func)

        except Exception as e:
            log.debug("Hook error; filename=%s; e=%s;" % (filename, str(e)))
            raise e

    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await after_startup()
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=cfg.APP_VERSION)
app.include_router(static_routers.router)
app.include_router(user_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(document_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(system_routers.router, prefix=cfg.APP_PREFIX)
app.mount(cfg.USERPIC_PREFIX,
          StaticFiles(directory=cfg.USERPIC_BASE_PATH, html=False),
          name=cfg.USERPIC_BASE_PATH)


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    # ctx = get_context()
    ctx.request_start_time = time()
    ctx.trace_request_uuid = str(uuid4())

    log.debug("Request received; module=app; function=middleware_handler; "
              "elapsed_time=0; method=%s; url=%s; headers=%s;" % (
                  request.method, str(request.url), str(request.headers)))

    response = await call_next(request)

    elapsed_time = time() - ctx.request_start_time
    log.debug("Response sent; module=app; function=middleware_handler; "
              "elapsed_time=%s; status=%s; headers=%s;" % (
                  "{0:.10f}".format(elapsed_time), response.status_code,
                  str(response.headers.raw)))

    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception):
    # ctx = get_context()
    elapsed_time = time() - ctx.request_start_time

    if isinstance(e, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        error_details = e.errors()

    elif isinstance(e, (FileNotFoundError, FileExistsError)):
        status_code = status.HTTP_400_BAD_REQUEST,
        error_details = {"detail": Msg.BAD_REQUEST}

    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_details = {"detail": Msg.SERVER_ERROR}

    log.error("Request failed; module=app; function=exception_handler; "
              "elapsed_time=%s; status_code=%s; e=%s;" % (
                  elapsed_time, status_code, str(e)))
    response_content = jsonable_encoder({"detail": error_details})
    return JSONResponse(status_code=status_code, content=response_content)
