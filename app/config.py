"""
Defines the configuration settings for the application using a dataclass
to hold various configuration parameters. Loads these settings from an
.env file using dotenv and converts them to the appropriate types.
Utilizes an LRU cache to store the configuration object for efficient
retrieval.
"""

from dotenv import dotenv_values
from dataclasses import dataclass, fields
from functools import lru_cache

DOTENV_FILE = "/hide/.env"


@dataclass
class Config:
    COPYRIGHT: str
    PROJECT: str
    AUTHOR: str

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
    REDIS_DECODE: bool
    REDIS_EXPIRE: int

    LOG_LEVEL: str
    LOG_NAME: str
    LOG_FORMAT: str
    LOG_FILENAME: str
    LOG_FILESIZE: int
    LOG_FILES_LIMIT: int

    MFA_APP_NAME: str
    MFA_MIMETYPE: str
    MFA_VERSION: int
    MFA_BOX_SIZE: int
    MFA_BORDER: int
    MFA_FIT: bool
    MFA_COLOR: str
    MFA_BACKGROUND: str

    EXTENSIONS_BASE_PATH: str
    EXTENSIONS_ENABLED: list

    APP_TITLE: str
    APP_VERSION: str
    APP_PREFIX: str
    APP_DESCRIPTION: str

    HASH_SALT: str
    FERNET_KEY: str

    JWT_SECRET: str
    JWT_EXPIRES: int
    JWT_ALGORITHM: str
    JTI_LENGTH: int

    USER_LOGIN_ATTEMPTS: int
    USER_MFA_ATTEMPTS: int
    USER_SUSPENDED_TIME: int

    USERPIC_BASE_PATH: str
    USERPIC_BASE_URL: str
    USERPIC_PREFIX: str
    USERPIC_MIMES: list
    USERPIC_EXTENSION: str
    USERPIC_MODE: str
    USERPIC_WIDTH: int
    USERPIC_HEIGHT: int
    USERPIC_QUALITY: int

    UPLOADS_BASE_PATH: str
    UPLOADS_EXTENSION: str

    THUMBNAILS_BASE_URL: str
    THUMBNAILS_BASE_PATH: str
    THUMBNAILS_EXTENSION: str
    THUMBNAILS_PREFIX: str
    THUMBNAIL_WIDTH: int
    THUMBNAIL_HEIGHT: int
    THUMBNAIL_QUALITY: int


@lru_cache(maxsize=None)
def get_config() -> Config:
    """
    Loads configuration settings from an .env file and returns them as a
    Config dataclass instance. The function uses type hints to convert
    the environment variable values to their appropriate types, such as
    int, list, or bool. Caches the result to optimize performance
    for subsequent calls.
    """
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
