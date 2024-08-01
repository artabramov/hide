"""User repository."""

# from fastapi.exceptions import RequestValidationError
# from app.managers.entity_manager import EntityManager
# from app.managers.cache_manager import CacheManager
from app.models.user_models import User
# from app.helpers.jwt_helper import JWTHelper
# from app.helpers.mfa_helper import MFAHelper
# from app.helpers.hash_helper import HashHelper
# from fastapi import HTTPException, UploadFile
# from PIL import Image, ImageOps
# from app.errors import E
from app.config import get_config
from app.repositories.basic_repository import BasicRepository
from typing import List

cfg = get_config()


class UserRepository(BasicRepository):

    async def exists(self, **kwargs) -> bool:
        return await self.entity_manager.exists(User, **kwargs)

    async def insert(self, user: User, commit: bool = True) -> User:
        await self.entity_manager.insert(user)
        await self.cache_manager.set(user)
        return user

    async def select(self, user_id: int = None, **kwargs) -> User | None:
        user = None

        if user_id:
            user = await self.cache_manager.get(User, user_id)

        if not user and user_id:
            user = await self.entity_manager.select(User, user_id)

        elif not user and kwargs:
            user = await self.entity_manager.select_by(User, **kwargs)

        if user:
            await self.cache_manager.set(user)

        return user

    async def update(self, user: User, commit: bool = True):
        await self.entity_manager.update(user, commit=commit)
        await self.cache_manager.set(user)

    async def delete(self, user: User, commit: bool = True):
        raise NotImplementedError

    async def select_all(self, **kwargs) -> List[User]:
        ...

    async def count_all(self, **kwargs) -> int:
        ...

    async def sum_all(self, column_name: str, **kwargs) -> int:
        ...
