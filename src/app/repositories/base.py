import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, delete

from common.exceptions.base import ObjectDoesNotExist


class SQLAlchemyRepository:
    @property
    def model(self):
        raise NotImplementedError

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def delete_by_id(self, obj_id: uuid.UUID):
        stmt = delete(self.model).where(self.model.id == obj_id)
        await self.session.execute(stmt)
        await self.commit()

    async def update_by_id(self, obj_id, **params):
        instance = await self.get_by(id=obj_id)
        if not instance:
            raise ObjectDoesNotExist()
        for field, value in params.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        await self.session.commit()
        return instance

    async def get_or_create(self, **kwargs):
        instance = await self.get_by(**kwargs)
        if not instance:
            instance = self.model(**kwargs)
            self.session.add(instance)
            await self.session.commit()
        return instance

    async def get_by(self, **kwargs):
        stmt = select(self.model).filter_by(**kwargs)
        instance = await self.session.scalar(stmt)
        return instance
