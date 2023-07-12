from uuid import UUID

from fastapi import Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.common import get_session
from repositories import DeviceRepository


class DeviceService:
    def __init__(self, user_agent: str = Header(),
                 session: AsyncSession = Depends(get_session)):
        self.device_repository = DeviceRepository(session=session)
        self.user_agent = user_agent

    async def get_device_id(self) -> UUID:
        device_db = await self.device_repository.get_or_create(user_agent=self.user_agent)
        return device_db.id
