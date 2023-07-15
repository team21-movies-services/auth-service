import uuid
from typing import Generic, Type, TypeVar

from common.exceptions.base import ObjectDoesNotExist
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete, select

dbModel = TypeVar("dbModel")


class SQLAlchemyRepository(Generic[dbModel]):
    @property
    def model(self) -> Type[dbModel]:
        raise NotImplementedError

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def delete_by_id(self, obj_id: uuid.UUID) -> None:
        stmt = delete(self.model).where(self.model.id == obj_id)  # type:ignore
        await self.session.execute(stmt)
        await self.commit()

    async def update_by_id(self, obj_id, **params) -> dbModel:
        instance = await self.get_by(id=obj_id)
        if not instance:
            raise ObjectDoesNotExist()
        for field, value in params.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        await self.session.commit()
        return instance

    async def get_or_create(self, **kwargs) -> dbModel:
        instance = await self.get_by(**kwargs)
        if not instance:
            instance = self.model(**kwargs)
            self.session.add(instance)
            await self.session.commit()
        return instance

    async def get_by(self, **kwargs) -> dbModel | None:
        stmt = select(self.model).filter_by(**kwargs)
        instance = await self.session.scalar(stmt)
        return instance
