from fastapi import APIRouter, Depends, Response
from fastapi import HTTPException
from app.database import get_session
from app.cache import get_cache
from app.schemas.user_schemas import MFARequest
from app.repository import Repository
import qrcode
from io import BytesIO
from app.config import get_config
from app.models.user_model import User

router = APIRouter()
cfg = get_config()

MFA_MASK = "otpauth://totp/%s?secret=%s&issuer=%s"


@router.get("/user/{user_id}/mfa/{mfa_secret}", summary="Retrieve MFA QR-code",
            include_in_schema=False)
async def user_mfa(
    session=Depends(get_session),
    cache=Depends(get_cache),
    schema=Depends(MFARequest)
):
    """
    Retrieve a QR code for MFA setup for a user. This endpoint validates
    the user's MFA secret and generates a QR code that can be scanned by
    an MFA app. The QR code includes the MFA secret and user login
    information.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=schema.user_id)
    if not user or user.mfa_secret != schema.mfa_secret:
        raise HTTPException(status_code=404)

    qr = qrcode.QRCode(
        version=cfg.MFA_VERSION, box_size=cfg.MFA_BOX_SIZE,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        border=cfg.MFA_BORDER
        )
    qr.add_data(MFA_MASK % (cfg.MFA_APP_NAME, user.mfa_secret,
                            user.user_login))
    qr.make(fit=cfg.MFA_FIT)

    img = qr.make_image(fill_color=cfg.MFA_COLOR,
                        back_color=cfg.MFA_BACKGROUND)

    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)
    img_data = img_bytes.getvalue()

    return Response(content=img_data, media_type=cfg.MFA_MIMETYPE)
