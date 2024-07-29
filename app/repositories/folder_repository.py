from app.models.folder_models import Folder
from app.config import get_config
from app.repositories.basic_repository import BasicRepository

cfg = get_config()


class FolderRepository(BasicRepository):

    async def exists(self, **kwargs) -> bool:
        pass

    async def insert(self, folder: Folder) -> Folder:
        pass

    async def select(self, folder_id: int = None, **kwargs) -> Folder | None:
        pass

    async def update(self, folder: Folder):
        pass

    async def delete(self, folder: Folder):
        pass

    async def select_all(self, folder: Folder):
        pass
