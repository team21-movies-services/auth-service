from dependencies.common import get_session
from dependencies.registrator import add_factory_to_mapper
from fastapi import Depends
from repositories import DeviceRepository, HistoryRepository
from services.history import HistoryService, HistoryServiceABC
from sqlalchemy.ext.asyncio import AsyncSession


@add_factory_to_mapper(HistoryServiceABC)
def create_history_service(
    session: AsyncSession = Depends(get_session),
):
    return HistoryService(
        HistoryRepository(session=session),
        DeviceRepository(session=session),
    )
