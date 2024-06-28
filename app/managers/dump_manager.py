from sqlalchemy.ext.serializer import dumps, loads


class DumpManager:

    @staticmethod
    async def write(entity: object):
        serialized_data = dumps(entity)
        filename = "/hide/sync/%s/%s.bin" % (entity.__tablename__, entity.id)
        with open(filename, "wb") as f:
            f.write(serialized_data)
