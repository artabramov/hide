
"""Config."""

from dotenv import dotenv_values
from dataclasses import dataclass, fields
from functools import lru_cache

DOTENV_FILE = "/hide/.env"


@dataclass
class Config:
    UVICORN_HOST: str
    UVICORN_PORT: int
    UVICORN_WORKERS: int

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_POOL_SIZE: int
    POSTGRES_POOL_OVERFLOW: int

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DECODE_RESPONSES: bool
    REDIS_EXPIRE: int

    APP_TITLE: str
    APP_VERSION: str
    APP_PREFIX: str
    APP_HASH_SALT: str
    APP_FERNET_KEY: str
    APP_JTI_LENGTH: int
    APP_SYNC_BASE_PATH: str
    APP_SYNC_FILE_EXT: str


@lru_cache(maxsize=None)
def get_config() -> Config:
    """Create config object from dotenv file."""
    keys_and_types = {x.name: x.type for x in fields(Config)}
    values = dotenv_values(DOTENV_FILE)
    config_dict = {}

    for key, value in values.items():
        value_type = keys_and_types.get(key)
        if value_type == int:
            value = int(value)

        elif value_type == list:
            value = value.split(",")

        elif value_type == bool:
            value = value.lower() == "true"
        
        config_dict[key] = value

    return Config(**config_dict)
