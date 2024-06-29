from sqlalchemy.ext.serializer import dumps, loads
from app.config import get_config
import os 

cfg = get_config()


class SyncManager:

    async def dump(self, entity):
        dump = dumps(entity)
        filename = "%s.%s" % (entity.id, cfg.APP_SYNC_FILE_EXT)
        path = os.path.join(cfg.APP_SYNC_BASE_PATH, entity.__tablename__, filename)
        await self.file_manager.file_write(path, dump)