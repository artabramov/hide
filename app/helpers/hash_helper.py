import hashlib
from app.config import get_config

cfg = get_config()


class HashHelper:
    """Hash mixin."""

    @staticmethod
    def hash(value: str) -> str:
        """Return hashed value."""
        encoded_value = (value + cfg.APP_HASH_SALT).encode()
        hash = hashlib.sha512(encoded_value)
        return hash.hexdigest()
