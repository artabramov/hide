from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserRegisterRequest, UserRegisterResponse
from app.errors import E
from app.hooks import H, Hook
from app.repository import Repository

router = APIRouter()


@router.post("/user", summary="Register user",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=UserRegisterResponse, tags=["users"])
@locked
async def user_register(
    request: Request,
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(UserRegisterRequest)
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
        raise E("user_login", schema.user_login, E.VALUE_DUPLICATED,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    user_password = schema.user_password.get_secret_value()
    user = User(
        UserRole.reader, schema.user_login, user_password, schema.first_name,
        schema.last_name, user_signature=schema.user_signature,
        user_contacts=schema.user_contacts)
    await user_repository.insert(user, commit=False)

    hook = Hook(session, cache, request, current_user=user)
    await hook.execute(H.BEFORE_USER_REGISTER, user)

    await user_repository.commit()
    await hook.execute(H.AFTER_USER_REGISTER, user)

    return {
        "user_id": user.id,
        "mfa_secret": user.mfa_secret,
        "mfa_url": user.mfa_url,
    }
