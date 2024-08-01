from app.models.album_models import Album
from app.config import get_config
from app.repositories.basic_repository import BasicRepository
from typing import List

cfg = get_config()


class AlbumRepository(BasicRepository):

    async def exists(self, **kwargs) -> bool:
        return await self.entity_manager.exists(Album, **kwargs)

    async def insert(self, album: Album, commit: bool = True) -> Album:
        await self.entity_manager.insert(album, commit=commit)
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

    async def update(self, album: Album, commit: bool = True):
        await self.entity_manager.update(album, commit=commit)
        await self.cache_manager.set(album)

    async def delete(self, album: Album, commit: bool = True):
        await self.entity_manager.delete(album, commit=commit)
        await self.cache_manager.delete(album)

    async def select_all(self, **kwargs) -> List[Album]:
        albums = await self.entity_manager.select_all(Album, **kwargs)
        for album in albums:
            await self.cache_manager.set(album)
        return albums

    async def count_all(self, **kwargs) -> int:
        return await self.entity_manager.count_all(Album, **kwargs)

    async def sum_all(self, column_name: str, **kwargs) -> int:
        return await self.entity_manager.sum_all(Album, column_name, **kwargs)
