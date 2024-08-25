"""JWT helper."""

import jwt
import time
import string
from app.config import get_config
import random

cfg = get_config()


def jti_create():
    return "".join(random.choices(string.ascii_letters + string.digits,
                                  k=cfg.JTI_LENGTH))


def jwt_encode(user, token_exp: int = None) -> str:
    current_time = int(time.time())
    token_payload = {
        "user_id": user.id,
        "user_role": user.user_role.value,
        "user_login": user.user_login,
        "jti": user.jti,
        "iat": current_time,
    }
    if token_exp:
        token_payload["exp"] = token_exp

    token_encoded = jwt.encode(token_payload, cfg.JWT_SECRET,
                               algorithm=cfg.JWT_ALGORITHM)
    return token_encoded


def jwt_decode(jwt_token: str) -> dict:
    token_decoded = jwt.decode(jwt_token, cfg.JWT_SECRET,
                               algorithms=cfg.JWT_ALGORITHM)

    token_payload = {
        "user_id": token_decoded["user_id"],
        "user_role": token_decoded["user_role"],
        "user_login": token_decoded["user_login"],
        "iat": token_decoded["iat"],
        "jti": token_decoded["jti"],
    }

    if "exp" in token_decoded:
        token_payload["exp"] = token_decoded["exp"]

    return token_payload
