from fastapi import APIRouter, Depends
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_models import User, UserRole
from app.schemas.user_schemas import UserRegisterRequest, UserRegisterResponse
from app.repositories.user_repository import UserRepository
from app.errors import E, Msg
from app.config import get_config

router = APIRouter()
cfg = get_config()


@router.post("/user", response_model=UserRegisterResponse, tags=["users"])
async def user_register(session=Depends(get_session), cache=Depends(get_cache),
                        schema=Depends(UserRegisterRequest)):

    user_repository = UserRepository(session, cache)
    if await user_repository.exists(user_login__eq=schema.user_login):
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_EXISTS)

    user_password = schema.user_password.get_secret_value()
    user = User(UserRole.READER, schema.user_login, user_password,
                first_name=schema.first_name, last_name=schema.last_name)

    user = await user_repository.insert(user)
    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }
