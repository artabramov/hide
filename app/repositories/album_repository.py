from app.models.album_models import Album
from app.config import get_config
from app.repositories.basic_repository import BasicRepository
from typing import List

cfg = get_config()


class AlbumRepository(BasicRepository):

    async def exists(self, **kwargs) -> bool:
        return await self.entity_manager.exists(Album, **kwargs)

    async def insert(self, album: Album) -> Album:
        await self.entity_manager.insert(album, commit=True)
        await self.cache_manager.set(album)
        return album

    async def select(self, album_id: int = None, **kwargs) -> Album | None:
        album = None

        if album_id:
            album = await self.cache_manager.get(Album, album_id)

        if not album and album_id:
            album = await self.entity_manager.select(Album, album_id)

        elif not album and kwargs:
            album = await self.entity_manager.select_by(Album, **kwargs)

        if album:
            await self.cache_manager.set(album)

        return album

    async def update(self, album: Album) -> Album:
        await self.entity_manager.update(album, commit=True)
        await self.cache_manager.set(album)

    async def delete(self, album: Album):
        pass

    async def select_all(self, album: Album) -> List[Album]:
        pass
