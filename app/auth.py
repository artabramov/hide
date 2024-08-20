
from app.models.user_models import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from app.database import get_session
from app.cache import get_cache
from fastapi import Depends
from app.repository import Repository
from fastapi.security import HTTPBearer
from app.helpers.jwt_helper import jwt_decode
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.errors import E, Msg

jwt = HTTPBearer()


def auth(user_role: UserRole):
    if user_role == UserRole.reader:
        return _can_read

    elif user_role == UserRole.writer:
        return _can_write

    elif user_role == UserRole.editor:
        return _can_edit

    elif user_role == UserRole.admin:
        return _can_admin


async def _can_read(session: AsyncSession = Depends(get_session),
                    cache: Redis = Depends(get_cache), header=Depends(jwt)):
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_read:
        raise E("user_token", user_token, Msg.USER_TOKEN_DENIED)
    return user


async def _can_write(session: AsyncSession = Depends(get_session),
                     cache: Redis = Depends(get_cache), header=Depends(jwt)):
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_write:
        raise E("user_token", user_token, Msg.USER_TOKEN_DENIED)
    return user


async def _can_edit(session: AsyncSession = Depends(get_session),
                    cache: Redis = Depends(get_cache), header=Depends(jwt)):
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_edit:
        raise E("user_token", user_token, Msg.USER_TOKEN_DENIED)
    return user


async def _can_admin(session: AsyncSession = Depends(get_session),
                     cache: Redis = Depends(get_cache), header=Depends(jwt)):
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_admin:
        raise E("user_token", user_token, Msg.USER_TOKEN_DENIED)
    return user


async def _auth(user_token: str, session: AsyncSession, cache: Redis):
    if not user_token:
        raise E("user_token", user_token, Msg.USER_TOKEN_EMPTY)

    try:
        token_payload = jwt_decode(user_token)

    except ExpiredSignatureError:
        raise E("user_token", user_token, Msg.USER_TOKEN_EXPIRED)

    except PyJWTError:
        raise E("user_token", user_token, Msg.USER_TOKEN_INVALID)

    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=token_payload["user_id"])

    if not user:
        raise E("user_token", user_token, Msg.USER_TOKEN_ORPHANED)

    elif not user.is_active:
        raise E("user_token", user_token, Msg.USER_TOKEN_INACTIVE)

    elif token_payload["jti"] != user.jti:
        raise E("user_token", user_token, Msg.USER_TOKEN_DECLINED)

    return user
