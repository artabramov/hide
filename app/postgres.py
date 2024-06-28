"""Async session manager."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, async_sessionmaker
from asyncio import current_task
from app.config import get_config

cfg = get_config()
Base = declarative_base()


class SessionManager:
    """Async session manager."""

    def __init__(self):
        self.async_engine = self.create_engine()
        self.async_sessionmaker = self.create_sessionmaker()

    @property
    def connection_string(self):
        """The URL specifying the database connection details."""
        return "postgresql+asyncpg://%s:%s@%s:%s/%s" % (
            cfg.POSTGRES_USERNAME, cfg.POSTGRES_PASSWORD, cfg.POSTGRES_HOST,
            cfg.POSTGRES_PORT, cfg.POSTGRES_DATABASE)

    def create_engine(self):
        """
        The create_async_engine function is responsible for creating an asynchronous database engine.
        In the context of FastAPI and SQLAlchemy, this engine handles database connections and communication.
        """
        return create_async_engine(self.connection_string, echo=True, future=True, pool_size=cfg.POSTGRES_POOL_SIZE,
                                   max_overflow=cfg.POSTGRES_POOL_OVERFLOW)
    
    def create_sessionmaker(self):
        """
        The async_sessionmaker function is used to create an asynchronous session class.
        It's similar to the traditional sessionmaker but adapted for asynchronous operations.
        """
        return async_sessionmaker(self.async_engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def get_session(self):
        """
        The async_scoped_session function creates a scoped session for the current context.
        It allows to work with a single session within a particular scope, such as a request in FastAPI.
        """
        async_session = async_scoped_session(self.async_sessionmaker , scopefunc=current_task)
        return async_session()


sessionmanager = SessionManager()


async def get_session():
    """SQLAlchemy session creator."""
    try:
        session = sessionmanager.get_session()
        yield session
    except Exception:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()
