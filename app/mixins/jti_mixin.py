import random
import string
from app.config import get_config

config = get_config()


class JTIMixin:
    def create_jti(self):
        """Generate JTI."""
        return "".join(random.choices(string.ascii_letters + string.digits,
                                      k=config.APP_JTI_LENGTH))
