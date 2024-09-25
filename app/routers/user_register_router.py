from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserRegisterRequest, UserRegisterResponse
from app.errors import E
from app.hooks import H, Hook
from app.repository import Repository
from app.constants import LOC_BODY

router = APIRouter()


@router.post("/user", summary="Register a new user",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=UserRegisterResponse, tags=["users"])
@locked
async def user_register(
    schema: UserRegisterRequest,
    session=Depends(get_session), cache=Depends(get_cache)
) -> UserRegisterResponse:
    """
    FastAPI router for registering a new user. Checks if the user login
    already exists and raises a 422 error if it does. If the login is
    unique, creates a new user with the provided details and returns
    a 201 response with the user's ID, MFA secret, and a link to the
    MFA QR code.
    """
    user_repository = Repository(session, cache, User)
    user_exists = await user_repository.exists(
        user_login__eq=schema.user_login)

    if user_exists:
        raise E([LOC_BODY, "user_login"], schema.user_login,
                E.ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    user = User(
        UserRole.reader, schema.user_login, schema.user_password,
        schema.first_name, schema.last_name,
        user_signature=schema.user_signature,
        user_contacts=schema.user_contacts)
    await user_repository.insert(user, commit=False)

    hook = Hook(session, cache)
    await hook.do(H.BEFORE_USER_REGISTER, user)

    await user_repository.commit()
    await hook.do(H.AFTER_USER_REGISTER, user)

    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }
