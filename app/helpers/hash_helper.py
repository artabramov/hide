import hashlib
from app.config import get_config

cfg = get_config()


def get_hash(value: str) -> str:
    encoded_value = (value + cfg.HASH_SALT).encode()
    hash = hashlib.sha512(encoded_value)
    return hash.hexdigest()
