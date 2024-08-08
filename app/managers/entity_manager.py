
from sqlalchemy import select, text, asc, desc
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from typing import Union, Type, List, Optional
from app.decorators.timed_deco import timed

ID = "id"
ORDER_BY, ORDER = "order_by", "order"
ASC, DESC = "asc", "desc"
OFFSET, LIMIT = "offset", "limit"
RESERVED_KEYS = [ORDER_BY, ORDER, OFFSET, LIMIT]
RESERVED_OPERATORS = {
    "in": "in_",
    "eq": "__eq__",
    "ne": "__ne__",
    "ge": "__ge__",
    "le": "__le__",
    "gt": "__gt__",
    "lt": "__lt__",
    "like": "like",
    "ilike": "ilike",
}
DELETE_ALL_BATCH_SIZE = 500


class EntityManager:
    """
    Manages database operations for SQLAlchemy entities with async support.

    Provides methods for CRUD operations, counting, and aggregation with
    SQLAlchemy using an asynchronous session.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the EntityManager with an AsyncSession instance."""
        self.session = session

    @timed
    async def exists(self, cls: Type[DeclarativeBase], **kwargs) -> bool:
        """Check if an entity exists based on provided filters."""
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none() is not None

    @timed
    async def insert(self, obj: DeclarativeBase, flush: bool = True, commit: bool = True):
        """Insert a new entity into the database."""
        self.session.add(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    @timed
    async def select(self, cls: Type[DeclarativeBase], obj_id: int) -> Union[DeclarativeBase, None]:  # noqa E501
        """Select an entity by its id."""
        async_result = await self.session.execute(
            select(cls).where(cls.id == obj_id).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_by(self, cls: Type[DeclarativeBase], **kwargs) -> Union[DeclarativeBase, None]:  # noqa E501
        """Select an entity by various filters."""
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_all(self, cls: Type[DeclarativeBase], **kwargs) -> List[DeclarativeBase]:
        """Select all entities matching the filters."""
        async_result = await self.session.execute(
            select(cls)
            .where(*self._where(cls, **kwargs))
            .order_by(self._order_by(cls, **kwargs))
            .offset(self._offset(**kwargs))
            .limit(self._limit(**kwargs)))
        return async_result.unique().scalars().all()

    @timed
    async def update(self, obj: DeclarativeBase, flush: bool = True, commit: bool = False):
        """Update an existing entity in the database."""
        await self.session.merge(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    @timed
    async def delete(self, obj: DeclarativeBase, commit: bool = False):
        """Delete an entity from the database."""
        await self.session.delete(obj)

        if commit:
            await self.commit()

    @timed
    async def delete_all(self, cls: Type[DeclarativeBase], commit: bool = False, **kwargs):
        """Delete all entities of a class with optional filters."""
        kwargs = kwargs | {ORDER_BY: ID, ORDER: ASC, OFFSET: 0, LIMIT: DELETE_ALL_BATCH_SIZE}
        while objs := await self.select_all(cls, **kwargs):
            kwargs[OFFSET] += kwargs[LIMIT]
            for obj in objs:
                await self.delete(obj, commit=commit)

    @timed
    async def count_all(self, cls: Type[DeclarativeBase], **kwargs) -> int:
        """Count all entities matching the filters."""
        async_result = await self.session.execute(
            select(func.count(getattr(cls, ID))).where(*self._where(cls, **kwargs)))
        return async_result.unique().scalars().one_or_none() or 0

    @timed
    async def sum_all(self, cls: Type[DeclarativeBase], column_name: str, **kwargs) -> int:
        """Sum values of a specific column for all entities matching the filters."""
        async_result = await self.session.execute(
            select(func.sum(getattr(cls, column_name))).where(*self._where(cls, **kwargs)))
        return async_result.unique().scalars().one_or_none() or 0

    @timed
    async def lock_all(self, cls: Type[DeclarativeBase]):
        """Lock the table to prevent other transactions from modifying it."""
        await self.session.execute(
            text("LOCK TABLE %s IN ACCESS EXCLUSIVE MODE;" % cls.__tablename__))

    # async def subquery(self, cls, foreign_key, **kwargs):
    #     return self.session.query(getattr(cls, foreign_key)).filter(
    # *self._where(cls, **kwargs))

    async def flush(self):
        """Flush the session to synchronize with the database."""
        await self.session.flush()

    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self):
        """Roll back the current transaction."""
        await self.session.rollback()

    def _where(self, cls: Type[DeclarativeBase], **kwargs) -> list:
        """Construct a list of SQLAlchemy "where" clauses based on filters."""
        where = []
        for key in {x: kwargs[x] for x in kwargs if x not in RESERVED_KEYS}:
            column_name, operator = key.split("__")

            if hasattr(cls, column_name):
                value = kwargs[key]

                if value:
                    if operator == "in":
                        value = [x.strip() for x in value.split(",")]

                    elif operator in ["like", "ilike"]:
                        value = "%" + value + "%"

                    else:
                        value = value

                    column = getattr(cls, column_name)
                    operation = getattr(column, RESERVED_OPERATORS[operator])(value)
                    where.append(operation)
        return where

    def _order_by(self, cls: Type[DeclarativeBase], **kwargs) -> Union[asc, desc, None]:
        """Determine the order by clause based on the provided filters."""
        order_by = getattr(cls, kwargs.get(ORDER_BY))

        if kwargs.get(ORDER) == ASC:
            return asc(order_by)

        elif kwargs.get(ORDER) == DESC:
            return desc(order_by)

    def _offset(self, **kwargs) -> Optional[int]:
        """Get the offset value from the provided filters."""
        return kwargs.get(OFFSET)

    def _limit(self, **kwargs) -> Optional[int]:
        """Get the limit value from the provided filters."""
        return kwargs.get(LIMIT)
