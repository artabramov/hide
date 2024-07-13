"""User repository."""

# from fastapi.exceptions import RequestValidationError
# from app.managers.entity_manager import EntityManager
# from app.managers.cache_manager import CacheManager
# from app.managers.file_manager import FileManager
from app.models.user_models import User
from sqlalchemy.ext.serializer import dumps  # , loads
# from app.helpers.jwt_helper import JWTHelper
# from app.helpers.mfa_helper import MFAHelper
# from app.helpers.hash_helper import HashHelper
# from fastapi import HTTPException, UploadFile
# from PIL import Image, ImageOps
# from app.errors import E
from app.config import get_config
from app.repositories.basic_repository import BasicRepository

cfg = get_config()


class UserRepository(BasicRepository):

    async def exists(self, **kwargs) -> bool:
        return await self.entity_manager.exists(User, **kwargs)

    async def insert(self, user: User) -> User:
        await self.entity_manager.insert(user, commit=True)
        await self.cache_manager.set(user)
        await self.file_manager.write(user.dump_path, dumps(user))
        return user

    async def select(self, user_id: int = None, **kwargs) -> User | None:
        """Select user."""
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

    async def update(self, user: User):
        await self.entity_manager.update(user, commit=True)
        await self.cache_manager.set(user)
        await self.file_manager.write(user.dump_path, dumps(user))
