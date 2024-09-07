"""
The module defines a FastAPI router for creating favorite entities.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.favorite_model import Favorite
from app.schemas.favorite_schemas import (
    FavoriteInsertRequest, FavoriteInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import H, Hook
from app.auth import auth

router = APIRouter()


@router.post("/favorite", summary="Create favorite",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=FavoriteInsertResponse, tags=["favorites"])
async def favorite_insert(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
    schema=Depends(FavoriteInsertRequest)
) -> FavoriteInsertResponse:
    """
    FastAPI router for creating a comment entity. The router verifies
    if the specified document exists, creates a favorite record if it
    does not already exist for the current user and document, updates
    the favorites count for the document, and executes related hooks.
    Returns the ID of the created favorite in a JSON response. The
    current user should have a reader role or higher. Returns a 201
    response on success, a 404 error if the document is not found,
    and a 403 error if authentication fails or the user does not have
    the required role.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id__eq=schema.document_id)

    if not document:
        raise E("document_id", schema.document_id, E.RESOURCE_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND)

    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(
        user_id__eq=current_user.id, document_id__eq=schema.document_id)

    if not favorite:
        favorite = Favorite(current_user.id, document.id)
        await favorite_repository.insert(favorite, commit=False)

    document.favorites_count = await favorite_repository.count_all(
        document_id__eq=document.id)
    await document_repository.update(document, commit=False)

    hook = Hook(session, cache, request, current_user=current_user)
    await hook.execute(H.BEFORE_FAVORITE_INSERT, favorite)

    await favorite_repository.commit()
    await hook.execute(H.AFTER_FAVORITE_INSERT, favorite)

    return {"favorite_id": favorite.id}
