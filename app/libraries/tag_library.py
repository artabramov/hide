import asyncio
from typing import List
from app.repository import Repository
from app.models.tag_models import Tag

asyncio_lock = asyncio.Lock()


class TagLibrary:

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    def extract_values(self, source_string: str | None) -> List[str]:
        values = []
        if source_string:
            values = source_string.split(",")
            values = [tag.strip().lower() for tag in values]
            values = list(set([value for value in values if value]))
        return values

    async def delete_all(self, document_id: int):
        # do not delete tags manually on document deletion,
        # it will be done automatically by SQLAlchemy relationship.
        # use only for document updation.
        tag_repository = Repository(self.session, self.cache, Tag)
        await tag_repository.delete_all(document_id__eq=document_id)

    async def insert_all(self, document_id: int, values: List[str]):
        tag_repository = Repository(self.session, self.cache, Tag)
        for value in values:
            try:
                async with asyncio_lock:
                    tag = Tag(document_id, value)
                    await tag_repository.insert(tag)

            except Exception:
                pass
