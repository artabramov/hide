import enum
from time import time
from sqlalchemy import Boolean, Column, Integer, BigInteger, SmallInteger, String, Enum
from app.postgres import Base
from sqlalchemy.ext.hybrid import hybrid_property
# from app.mixins.fernet_mixin import FernetMixin
from app.mixins.jti_mixin import JTIMixin
from app.mixins.mfa_mixin import MFAMixin
from app.mixins.fernet_mixin import FernetMixin
from app.helpers.hash_helper import HashHelper
from sqlalchemy.orm import relationship
from app.config import get_config
from app.models.basic_model import Basic

cfg = get_config()


class UserRole(enum.Enum):
    READER = "reader"
    WRITER = "writer"
    EDITOR = "editor"
    ADMIN = "admin"


class User(Basic, MFAMixin, JTIMixin, FernetMixin):
    __tablename__ = "users"

    suspended_date = Column(Integer, nullable=False, default=0)
    user_role = Column(Enum(UserRole), nullable=False, index=True, default=UserRole.READER)
    is_active = Column(Boolean)
    user_login = Column(String(40), nullable=False, index=True, unique=True)
    password_hash = Column(String(128), nullable=False, index=True)
    password_attempts = Column(SmallInteger, nullable=False, default=0)
    password_accepted = Column(Boolean, nullable=False, default=False)
    first_name = Column(String(40), nullable=False, index=True)
    last_name = Column(String(40), nullable=False, index=True)
    mfa_secret_encrypted = Column(String(512), nullable=False, unique=True)
    mfa_attempts = Column(SmallInteger(), nullable=False, default=0)
    jti_encrypted = Column(String(512), nullable=False, unique=True)
    user_summary = Column(String(512), index=False, nullable=True)

    # user_album = relationship("Album", back_populates="album_user", lazy="noload")
    # mediafile = relationship("Mediafile", back_populates="mediafile_user", lazy="noload")
    # user_comment = relationship("Comment", back_populates="comment_user", lazy="noload")

    # user_favorite = relationship("Favorite", back_populates="favorite_user", lazy="noload")

    def __init__(self, user_role: UserRole, user_login: str, user_password: str,
                 first_name: str, last_name: str, is_active: bool = False,
                 user_summary: str = ""):
        self.suspended_date = 0
        self.user_role = user_role
        self.is_active = is_active
        self.user_login = user_login
        self.password_hash = HashHelper.hash(user_password)
        self.password_attempts = 0
        self.password_accepted = False
        self.first_name = first_name
        self.last_name = last_name
        self.mfa_secret = self.create_mfa_secret()
        self.mfa_attempts = 0
        self.jti = self.create_jti()
        self.user_summary = user_summary

    @property
    def mfa_secret(self) -> str:
        return self.decrypt(self.mfa_secret_encrypted)

    @mfa_secret.setter
    def mfa_secret(self, value: str):
        self.mfa_secret_encrypted = self.encrypt(value)

    @property
    def mfa_url(self):
        return "http://localhost/user/%s/mfa/%s" % (
            self.id, self.mfa_secret)

    @property
    def jti(self) -> str:
        return self.decrypt(self.jti_encrypted)

    @jti.setter
    def jti(self, value: str):
        self.jti_encrypted = self.encrypt(value)

    @hybrid_property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name

    @property
    def can_admin(self) -> bool:
        return self.user_role == UserRole.ADMIN

    @property
    def can_edit(self) -> bool:
        return self.user_role in [UserRole.ADMIN, UserRole.EDITOR]

    @property
    def can_write(self) -> bool:
        return self.user_role in [UserRole.ADMIN, UserRole.EDITOR,
                                  UserRole.WRITER]

    @property
    def can_read(self) -> bool:
        return self.user_role in [UserRole.ADMIN, UserRole.EDITOR,
                                  UserRole.WRITER, UserRole.READER]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
            "user_role": self.user_role.name,
            "is_active": self.is_active,
            "user_login": self.user_login,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_summary": self.user_summary,
        }