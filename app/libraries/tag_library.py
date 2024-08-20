import asyncio
from app.repository import Repository
from app.models.tag_models import Tag, DocumentTag

asyncio_lock = asyncio.Lock()


class TagLibrary:

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    def _extract_values_from_string(self, value: str | None) -> list:
        """Extract tag values from string."""
        tags = []
        if value:
            tags = value.split(",")
            tags = [tag.strip().lower() for tag in tags]
            tags = list(set([tag for tag in tags if tag]))
        return tags

    async def insert_all(self, document_id: int, raw_data: str):
        """Get tags from string and insert them all."""
        values = self._extract_values_from_string(raw_data)
        if values:
            tag_repository = Repository(self.session, self.cache, Tag)
            document_tag_repository = Repository(
                self.session, self.cache, DocumentTag)

            for value in values:
                try:
                    tag = await tag_repository.select(value__eq=value)
                    if not tag:
                        async with asyncio_lock:
                            tag = Tag(value)
                            await tag_repository.insert(tag, commit=False)
                    
                    async with asyncio_lock:
                        tag.documents_count += 1
                        await tag_repository.update(tag)

                    async with asyncio_lock:
                        document_tag = DocumentTag(document_id, tag.id)
                        await document_tag_repository.insert(document_tag)

                except Exception:
                    pass

    async def delete_all(self, document_id: int):
        document_tag_repository = Repository(
            self.session, self.cache, DocumentTag)

        offset = 0
        limit = 2
        while document_tags := await document_tag_repository.select_all(
                document_id__eq=document_id, order_by="id", order="asc",
                offset=offset, limit=limit):

            offset += limit
            for document_tag in document_tags:
                document_tags
                a = 1
                # await self.delete(obj, commit=commit)
