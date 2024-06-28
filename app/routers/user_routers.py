from fastapi import APIRouter, Depends
from app.postgres import get_session
from app.models.user_models import User, UserRole
from app.schemas.user_schemas import UserRegister
from app.repositories.user_repository import UserRepository
from app.helpers.hash_helper import HashHelper
from app.errors import E, Msg

router = APIRouter()


@router.post("/user", tags=["users"])
async def user_register(session = Depends(get_session),
                        schema=Depends(UserRegister)):

    user_repository = UserRepository(session)
    if await user_repository.exists(user_login__eq=schema.user_login):
        raise E("user_login", schema.user_login, Msg.USER_LOGIN_EXISTS)

    password_hash = HashHelper.hash(schema.user_password.get_secret_value())
    user = User(UserRole.READER, schema.user_login, password_hash,
                first_name=schema.first_name, last_name=schema.last_name)

    user = await user_repository.insert(user)
    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
    }
