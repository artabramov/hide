# from motor.motor_asyncio import AsyncIOMotorDatabase
from redis import Redis
from app.managers.entity_manager import EntityManager
from app.managers.dump_manager import DumpManager
# from app.managers.cache_manager import CacheManager
# from app.managers.file_manager import FileManager
# from app.context import get_context
# from app.mixins.hook_mixin import HookMixin

# context = get_context()


class BasicRepository:

    def __init__(self, session):
        self.entity_manager = EntityManager(session)
        self.dump_manager = DumpManager
        # self.cache_manager = CacheManager(cache) if cache else None
        # self.file_manager = FileManager
