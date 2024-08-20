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


def jwt_encode(user) -> str:
    current_time = int(time.time())
    payload = {
        "user_id": user.id,
        "user_role": user.user_role.value,
        "user_login": user.user_login,
        "jti": user.jti,
        "iat": current_time,
        "exp": current_time + cfg.JWT_EXPIRES,
    }
    return jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)


def jwt_decode(jwt_token: str) -> dict:
    payload = jwt.decode(jwt_token, cfg.JWT_SECRET,
                         algorithms=cfg.JWT_ALGORITHM)

    return {
        "user_id": payload["user_id"],
        "user_role": payload["user_role"],
        "user_login": payload["user_login"],
        "iat": payload["iat"],
        "jti": payload["jti"],
        "exp": payload["exp"]
    }
