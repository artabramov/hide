from app.config import get_config

cfg = get_config()


def load_description():
    """
    Loads the OpenAPI description from the specified file path
    and returns the contents as a string.
    """
    with open(cfg.OPENAPI_DESCRIPTION_PATH, "r") as fn:
        return fn.read()
