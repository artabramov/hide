import enum


class H(enum.Enum):
    BEFORE_USER_REGISTER = "before_user_register"
    AFTER_USER_REGISTER = "after_user_register"
    BEFORE_USER_LOGIN = "before_user_login"
    AFTER_USER_LOGIN = "after_user_login"
