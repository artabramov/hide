
from sqlalchemy import asc, desc, text
from sqlalchemy.sql import func
from sqlalchemy import select
# from decimal import Decimal
# from time import time
from app.decorators.timed_deco import timed

_ORDER_BY, _ORDER = "order_by", "order"
_ID = "id"
_ASC, _DESC = "asc", "desc"
_OFFSET, _LIMIT = "offset", "limit"
_RESERVED = [_ORDER_BY, _ORDER, _OFFSET, _LIMIT]
_OPERATORS = {
    "in": "in_",
    "eq": "__eq__",
    "not": "__ne__",
    "gte": "__ge__",
    "lte": "__le__",
    "gt": "__gt__",
    "lt": "__lt__",
    "like": "like",
    "ilike": "ilike",
}
_DELETE_ALL_LIMIT = 500


class EntityManager:

    def __init__(self, session):
        self.session = session

    @timed
    async def exists(self, cls: object, **kwargs) -> bool:
        """Check if object exists in Postgres database."""
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none() is not None

    @timed
    async def insert(self, obj: object, flush: bool = True,
                     commit: bool = True):
        self.session.add(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    @timed
    async def select(self, cls: object, obj_id: int) -> object | None:
        """Select SQLAlchemy object from Postgres database."""
        async_result = await self.session.execute(
            select(cls).where(cls.id == obj_id).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_by(self, cls: object, **kwargs) -> object | None:
        """Select SQLAlchemy object from Postgres database."""
        async_result = await self.session.execute(
            select(cls).where(*self._where(cls, **kwargs)).limit(1))
        return async_result.unique().scalars().one_or_none()

    @timed
    async def select_all(self, cls: object, **kwargs) -> list:
        """Select a bunch of SQLAlchemy objects from Postgres database."""
        async_result = await self.session.execute(
            select(cls)
            .where(*self._where(cls, **kwargs))
            .order_by(self._order_by(cls, **kwargs))
            .offset(self._offset(**kwargs))
            .limit(self._limit(**kwargs)))
        return async_result.unique().scalars().all()

    @timed
    async def update(self, obj: object, flush: bool = True,
                     commit: bool = False):
        """Update SQLAlchemy object in Postgres database."""
        await self.session.merge(obj)

        if flush:
            await self.flush()

        if commit:
            await self.commit()

    @timed
    async def delete(self, obj: object, commit: bool = False):
        """Delete SQLAlchemy object from Postgres database."""
        await self.session.delete(obj)

        if commit:
            await self.commit()

    @timed
    async def delete_all(self, cls: object, commit: bool = False, **kwargs):
        kwargs = kwargs | {_ORDER_BY: _ID, _ORDER: _ASC, _OFFSET: 0,
                           _LIMIT: _DELETE_ALL_LIMIT}
        while objs := await self.select_all(cls, **kwargs):
            kwargs[_OFFSET] += kwargs[_LIMIT]
            for obj in objs:
                await self.delete(obj, commit=commit)

    @timed
    async def count_all(self, cls: object, **kwargs) -> int:
        """Count SQLAlchemy objects in Postgres database."""
        async_result = await self.session.execute(
            select(func.count(getattr(cls, _ID))).where(
                *self._where(cls, **kwargs)))
        return async_result.unique().scalars().one_or_none() or 0

    @timed
    async def sum_all(self, cls: object, column_name: str, **kwargs):
        """Sum SQLAlchemy object column in Postgres database."""
        async_result = await self.session.execute(
            select(func.sum(getattr(cls, column_name))).where(
                *self._where(cls, **kwargs)))
        return async_result.unique().scalars().one_or_none() or 0

    @timed
    async def lock_all(self, cls: object) -> None:
        """Lock Postgres table."""
        await self.session.execute(text(
            "LOCK TABLE %s IN ACCESS EXCLUSIVE MODE;" % cls.__tablename__))

    # async def subquery(self, cls, foreign_key, **kwargs):
    #     """Make a subquery expression for another class by a foreign key."""
    #     return self.session.query(getattr(cls, foreign_key)).filter(
    # *self._where(cls, **kwargs))

    async def flush(self):
        """Flush session."""
        await self.session.flush()

    async def commit(self):
        """Commit transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback transaction."""
        await self.session.rollback()

    def _where(self, cls, **kwargs):
        """Make WHERE statement."""
        where = []
        for key in {x: kwargs[x] for x in kwargs if x not in _RESERVED}:
            column_name, operator = key.split("__")

            if hasattr(cls, column_name):
                column = getattr(cls, column_name)
                value = kwargs[key]

                if isinstance(value, str):
                    if operator == "in":
                        value = [x.strip() for x in value.split(",")]
                    elif operator in ["like", "ilike"]:
                        value = "%" + value + "%"
                    else:
                        value = value

                    operation = getattr(column, _OPERATORS[operator])(value)
                    where.append(operation)
        return where

    def _order_by(self, cls, **kwargs):
        """Make ORDER BY statement."""
        order_by = getattr(cls, kwargs.get(_ORDER_BY))

        if kwargs.get(_ORDER) == _ASC:
            return asc(order_by)

        elif kwargs.get(_ORDER) == _DESC:
            return desc(order_by)

    def _offset(self, **kwargs):
        """Make OFFSET statement."""
        return kwargs.get(_OFFSET)

    def _limit(self, **kwargs):
        """Make LIMIT statement."""
        return kwargs.get(_LIMIT)
