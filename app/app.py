"""
This module sets up and configures the FastAPI application. It includes
middleware for logging HTTP requests and responses, an exception handler
for managing and responding to errors, and a lifespan context manager
for handling startup tasks such as loading extension modules,
registering hooks, and initializing the database schema. The application
also includes routes for static files and other resources, with specific
configuration for the application's title, version, and file paths.
"""

from fastapi import FastAPI, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.config import get_config
from app.context import get_context
from app.log import get_log
from app.routers import (
    static_routers, user_routers, collection_routers, document_routers,
    comment_routers, download_routers, system_routers)
from app.database import Base, sessionmanager, get_session
from app.errors import SERVER_ERROR
from contextlib import asynccontextmanager
from time import time
from uuid import uuid4
import os
import importlib.util
import inspect
from app.hooks import H, Hook
from app.cache import get_cache
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

cfg = get_config()
ctx = get_context()
log = get_log()


async def after_startup(session=Depends(get_session),
                        cache=Depends(get_cache)):
    """
    Executes actions needed after the application startup using the
    provided session and cache.
    """
    hook = Hook(session, cache)
    await hook.execute(H.AFTER_STARTUP)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application startup lifecycle by loading extension
    modules, registering functions as hooks, initializing the database
    schema, and performing additional startup actions. This function
    loads specified modules, gathers functions from these modules into
    a hook registry, and creates necessary database tables. It yields
    control after these setup tasks are completed, ensuring that the
    application is properly configured before serving requests.
    """
    ctx.hooks = {}

    # Load and register functions from extension modules.
    filenames = [file + ".py" for file in cfg.EXTENSIONS_ENABLED]
    for filename in filenames:
        module_name = filename.split(".")[0]
        module_path = os.path.join(cfg.EXTENSIONS_BASE_PATH, filename)

        try:
            # Load the module from the specified file path.
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Register functions from the module as hooks.
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

    # Create the database schema.
    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await after_startup()
    yield


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=cfg.APP_VERSION)
app.include_router(static_routers.router)
app.include_router(user_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(document_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(download_routers.router, prefix=cfg.APP_PREFIX)
app.include_router(system_routers.router, prefix=cfg.APP_PREFIX)
app.mount(cfg.USERPIC_PREFIX,
          StaticFiles(directory=cfg.USERPIC_BASE_PATH, html=False),
          name=cfg.USERPIC_BASE_PATH)
app.mount(cfg.THUMBNAILS_PREFIX,
          StaticFiles(directory=cfg.THUMBNAILS_BASE_PATH, html=False),
          name=cfg.THUMBNAILS_BASE_PATH)


@app.middleware("http")
async def middleware_handler(request: Request, call_next):
    """
    Middleware function that logs details of incoming HTTP requests and
    outgoing responses. It records the start time and a unique trace ID
    for each request, logs the request method, URL, and headers, then
    processes the request. After receiving the response, it calculates
    the elapsed time, logs the response status and headers, and returns
    the response to the client.
    """
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
    """
    Handles all exceptions raised during request processing by
    calculating the elapsed time and returning a JSON response with
    an appropriate status code. If the exception is a ValidationError
    from Pydantic, it logs detailed validation error information and
    responds with 422 status code and the validation errors. For other
    exceptions, it logs an error message and responds with 500 status
    code and a generic error message.
    """
    elapsed_time = time() - ctx.request_start_time

    # Handle validation errors raised by Pydantic schema validators.
    if isinstance(e, ValidationError):
        log.debug("Response sent; module=app; function=exception_handler; "
                  "elapsed_time=%s; status=%s; headers=%s;" % (
                    elapsed_time, status.HTTP_422_UNPROCESSABLE_ENTITY,
                    str(e)))

        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=jsonable_encoder({"detail": e.errors()}))

    # Handle all other exceptions.
    else:
        log.error("Request failed; module=app; function=exception_handler; "
                  "elapsed_time=%s; e=%s;" % (elapsed_time, str(e)))

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=jsonable_encoder({"detail": SERVER_ERROR}))
