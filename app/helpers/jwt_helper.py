"""JWT helper."""

import jwt
import time
import string
from app.config import get_config
import random

cfg = get_config()


class JWTHelper:
    """JWT mixin."""

    @staticmethod
    def create_jti():
        """Generate JTI."""
        return "".join(random.choices(string.ascii_letters + string.digits,
                                      k=cfg.JTI_LENGTH))

    @staticmethod
    def encode_token(user) -> str:
        """Encode user data into JWT token."""
        current_time = int(time.time())
        payload = {
            "user_id": user.id,
            "user_role": user.user_role.name,
            "user_login": user.user_login,
            "jti": user.jti,
            "iat": current_time,
            "exp": current_time + cfg.JWT_EXPIRES,
        }
        return jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

    @staticmethod
    def decode_token(jwt_token: str) -> dict:
        """Decode user data from JWT token."""
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
