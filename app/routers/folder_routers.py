from fastapi import APIRouter, Depends, HTTPException, status
from app.postgres import get_session
from app.redis import get_cache
from app.models.folder_models import Folder
from app.helpers.hash_helper import HashHelper
from app.helpers.jwt_helper import JWTHelper
from app.schemas.folder_schemas import (FolderInsertRequest,
                                        FolderInsertResponse)
from app.repositories.folder_repository import FolderRepository
from app.errors import E, Msg
from app.config import get_config
# from time import time
# from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()
cfg = get_config()


@router.post("/folder", response_model=FolderInsertResponse, tags=["folders"])
async def user_register(session=Depends(get_session), cache=Depends(get_cache),
                        current_user: User = Depends(auth(UserRole.WRITER)),
                        schema=Depends(FolderInsertRequest)):

    folder_repository = FolderRepository(session, cache)
    folder_exists = await folder_repository.exists(
        folder_name__eq=schema.folder_name)

    if folder_exists:
        raise E("folder_name", schema.folder_name, Msg.VALUE_EXISTS)

    folder = Folder(current_user.id, schema.is_locked, schema.folder_name,
                    folder_summary=schema.folder_summary)

    # hook = Hook(user_repository.entity_manager, user_repository.cache_manager)
    # user = await hook.execute(H.BEFORE_USER_REGISTER, entity=user)
    folder = await folder_repository.insert(folder)
    # user = await hook.execute(H.AFTER_USER_REGISTER, entity=user)

    return {"folder_id": folder.id}


# @router.get("/user/{user_id}", response_model=UserSelectResponse, tags=["users"])  # noqa E501
# async def user_select(session=Depends(get_session), cache=Depends(get_cache),
#                       current_user: User = Depends(auth(UserRole.READER)),
#                       schema=Depends(UserSelectRequest)):
#     """Select user."""
#     user_repository = UserRepository(session, cache)
#     user = await user_repository.select(schema.user_id)

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

#     return {
#         "user": user.to_dict(),
#     }
