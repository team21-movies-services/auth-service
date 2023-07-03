from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.registrator import add_factory_to_mapper
from dependencies.common import get_session
from services.history import HistoryServiceABC, HistoryService

from repositories import HistoryRepository, DeviceRepository


@add_factory_to_mapper(HistoryServiceABC)
def create_history_service(
        session: AsyncSession = Depends(get_session),
):
    return HistoryService(
        HistoryRepository(session=session),
        DeviceRepository(session=session),
    )
