# from motor.motor_asyncio import AsyncIOMotorDatabase
from redis import Redis
from app.managers.entity_manager import EntityManager
# from app.managers.cache_manager import CacheManager
from app.managers.file_manager import FileManager
# from app.context import get_context
# from app.mixins.hook_mixin import HookMixin
from sqlalchemy.ext.serializer import dumps, loads
from app.config import get_config
import os 

cfg = get_config()
# context = get_context()


class BasicRepository:

    def __init__(self, session):
        self.entity_manager = EntityManager(session)
        # self.cache_manager = CacheManager(cache) if cache else None
        self.file_manager = FileManager

    async def dump(self, entity):
        dump = dumps(entity)
        filename = "%s.%s" % (entity.id, cfg.APP_SYNC_FILE_EXT)
        path = os.path.join(cfg.APP_SYNC_BASE_PATH, entity.__tablename__, filename)
        await self.file_manager.file_write(path, dump)

