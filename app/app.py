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
    token_select_router, token_delete_router, user_register_router,
    user_mfa_router, user_login_router, user_select_router, user_update_router,
    user_delete_router, role_update_router, password_update_router,
    userpic_upload_router, userpic_delete_router, user_list_router,

    collection_insert_router, collection_select_router,
    collection_update_router, collection_delete_router,
    collection_list_router,

    document_upload_router, document_replace_router, document_select_router,
    document_update_router, document_delete_router, document_list_router,

    comment_insert_router, comment_select_router, comment_update_router,
    comment_delete_router, comment_list_router,

    upload_select_router, upload_download_router, upload_list_router,

    favorite_insert_router, favorite_select_router, favorite_delete_router,
    favorite_list_router, download_select_router, download_list_router,

    option_insert_router, option_select_router, option_update_router,
    option_delete_router, option_list_router,

    time_retrieve_router, telemetry_retrieve_router, lock_create_router,
    lock_retrieve_router, lock_delete_router)
from app.database import Base, sessionmanager, get_session
from app.errors import SERVER_ERROR
from contextlib import asynccontextmanager
import time
from uuid import uuid4
import os
import importlib.util
import inspect
from app.hooks import H, Hook
from app.cache import get_cache
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from app.version import __version__

cfg = get_config()
ctx = get_context()
log = get_log()


async def on_startup(session=Depends(get_session),
                     cache=Depends(get_cache)):
    """
    Executes startup hook using the provided database session and cache.
    """
    hook = Hook(session, cache)
    await hook.execute(H.ON_STARTUP)


def load_hooks():
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application startup lifecycle by initializing the
    database schema, creating scheduler, registering hooks, loading
    extension modules, and performing additional startup actions.
    """
    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    load_hooks()
    await on_startup()
    yield


def load_description():
    """
    Reads and returns the content of a short application description
    file as a string. The file is opened in read mode, and its entire
    content is returned. The function assumes the file exists and is
    accessible.
    """
    with open(cfg.APP_DESCRIPTION_PATH, "r") as fn:
        return fn.read()


app = FastAPI(lifespan=lifespan, title=cfg.APP_TITLE, version=__version__,
              description=load_description())

# user routers
app.include_router(user_login_router.router, prefix=cfg.APP_PREFIX)
app.include_router(token_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(token_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_register_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_mfa_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(role_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(password_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(userpic_upload_router.router, prefix=cfg.APP_PREFIX)
app.include_router(userpic_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(user_list_router.router, prefix=cfg.APP_PREFIX)

# collection routers
app.include_router(collection_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(collection_list_router.router, prefix=cfg.APP_PREFIX)

# document routers
app.include_router(document_upload_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_replace_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(document_list_router.router, prefix=cfg.APP_PREFIX)

# comment routers
app.include_router(comment_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(comment_list_router.router, prefix=cfg.APP_PREFIX)

# upload routers
app.include_router(upload_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(upload_download_router.router, prefix=cfg.APP_PREFIX)
app.include_router(upload_list_router.router, prefix=cfg.APP_PREFIX)

# download routers
app.include_router(download_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(download_list_router.router, prefix=cfg.APP_PREFIX)

# favorite routers
app.include_router(favorite_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(favorite_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(favorite_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(favorite_list_router.router, prefix=cfg.APP_PREFIX)

# option routers
app.include_router(option_insert_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_select_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_update_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_delete_router.router, prefix=cfg.APP_PREFIX)
app.include_router(option_list_router.router, prefix=cfg.APP_PREFIX)

# system routers
app.include_router(time_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(telemetry_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(lock_retrieve_router.router, prefix=cfg.APP_PREFIX)
app.include_router(lock_create_router.router, prefix=cfg.APP_PREFIX)
app.include_router(lock_delete_router.router, prefix=cfg.APP_PREFIX)


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
    ctx.request_start_time = time.time()
    ctx.trace_request_uuid = str(uuid4())

    log.debug("Request received; module=app; function=middleware_handler; "
              "elapsed_time=0; method=%s; url=%s; headers=%s;" % (
                  request.method, str(request.url), str(request.headers)))

    response = await call_next(request)

    elapsed_time = time.time() - ctx.request_start_time
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
    elapsed_time = time.time() - ctx.request_start_time

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
