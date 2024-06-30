from fastapi import APIRouter, Depends, Response
from fastapi import HTTPException, status
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_models import User, UserRole
from app.schemas.user_schemas import UserRegisterRequest, UserRegisterResponse, MFARequest
from app.repositories.user_repository import UserRepository
from app.errors import E, Msg
import qrcode
from io import BytesIO
from app.config import get_config

router = APIRouter()
cfg = get_config()


@router.post("/user", response_model=UserRegisterResponse, tags=["users"])
async def user_register(session = Depends(get_session), cache = Depends(get_cache),
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


@router.get("/user/{user_id}/mfa/{mfa_secret}", include_in_schema=False)
async def user_mfa(session = Depends(get_session), cache = Depends(get_cache),
                   schema=Depends(MFARequest)):

    user_repository = UserRepository(session, cache)
    user = await user_repository.select(schema.user_id)
    if not user or user.mfa_secret != schema.mfa_secret:
        raise HTTPException(status_code=404)

    qr = qrcode.QRCode(
        version=cfg.MFA_VERSION,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=cfg.MFA_BOX_SIZE,
        border=cfg.MFA_BORDER,
    )
    qr.add_data("otpauth://totp/%s?secret=%s&issuer=%s" % (cfg.MFA_REF_APP, user.mfa_secret, user.user_login))
    qr.make(fit=cfg.MFA_FIT)
    
    img = qr.make_image(fill_color=cfg.MFA_COLOR, back_color=cfg.MFA_BACKGROUND)
    
    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)
    img_data = img_bytes.getvalue()

    return Response(content=img_data, media_type=cfg.MFA_MIMETYPE)
    