from app.models.album_models import Album
from app.config import get_config
from app.repositories.basic_repository import BasicRepository

cfg = get_config()


class AlbumRepository(BasicRepository):

    async def exists(self, **kwargs) -> bool:
        return await self.entity_manager.exists(Album, **kwargs)

    async def insert(self, album: Album) -> Album:
        await self.entity_manager.insert(album, commit=True)
        await self.cache_manager.set(album)
        return album

    async def select(self, album_id: int = None, **kwargs) -> Album | None:
        pass

    async def update(self, album: Album):
        pass

    async def delete(self, album: Album):
        pass

    async def select_all(self, album: Album):
        pass
