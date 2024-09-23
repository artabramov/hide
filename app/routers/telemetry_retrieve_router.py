from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.auth import auth
from app.models.user_model import User, UserRole
from app.decorators.locked_decorator import locked
import platform
import psutil
from app.managers.entity_manager import EntityManager
# from app.schemas.system_schemas import SystemHelloResponse

router = APIRouter()


@router.get("/telemetry", summary="Retrieve telemetry",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            # response_model=SystemHelloResponse,
            tags=["system"])
@locked
async def telemetry_retrieve(
    request: Request, session=Depends(get_session),
    current_user: User = Depends(auth(UserRole.admin))
):
    entity_manager = EntityManager(session)

    postgres_version = await entity_manager.execute("SELECT version();")
    postgres_database_name = await entity_manager.execute("SELECT current_database();")  # noqa E501
    postgres_database_size = await entity_manager.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")  # noqa E501
    postgres_tables_count = await entity_manager.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")  # noqa E501
    postgres_users_count = await entity_manager.execute("SELECT COUNT(*) FROM pg_user;")  # noqa E501
    postgres_start_time = await entity_manager.execute("SELECT pg_postmaster_start_time();")  # noqa E501
    postgres_active_connections = await entity_manager.execute("SELECT COUNT(*) FROM pg_stat_activity;")  # noqa E501
    # pg_version = await entity_manager.execute("")

    return {
        "postgres_version": postgres_version[0][0],
        "postgres_database_name": postgres_database_name[0][0],
        "postgres_database_size": postgres_database_size[0][0],
        "postgres_tables_count": postgres_tables_count[0][0],
        "postgres_users_count": postgres_users_count[0][0],
        "postgres_start_time": postgres_start_time[0][0],
        "postgres_active_connections": postgres_active_connections[0][0],

        "platform_architecture": platform.architecture()[0],
        "platform_machine": platform.machine(),
        "platform_node": platform.node(),
        "platform_alias": platform.platform(aliased=True),
        "platform_processor": platform.processor(),

        "python_buildno": platform.python_build()[0],
        "python_builddate": platform.python_build()[1],
        "python_compiler": platform.python_compiler(),
        "python_branch": platform.python_branch(),
        "python_implementation": platform.python_implementation(),
        "python_revision": platform.python_revision(),
        "python_version": platform.python_version(),

        "os_name": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),

        "hdd_total": psutil.disk_usage("/").total,
        "hdd_used": psutil.disk_usage("/").used,
        "hdd_free": psutil.disk_usage("/").free,

        "ram_total": psutil.virtual_memory().total,
        "ram_used": psutil.virtual_memory().used,
        "ram_free": psutil.virtual_memory().free,

        "cpu_count": psutil.cpu_count(logical=False),
        "cpu_freq": int(psutil.cpu_freq(percpu=False).current),
        "cpu_percent": psutil.cpu_percent(),
    }
