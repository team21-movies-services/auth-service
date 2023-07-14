import uuid
from abc import ABC, abstractmethod
from typing import List

from models.history import ActionType
from repositories import DeviceRepository, HistoryRepository
from schemas.request.info import HistoryRequest
from schemas.response.info import HistoryResponse


class HistoryServiceABC(ABC):
    @abstractmethod
    async def create_history_event(self, user_id: uuid.UUID, user_agent: str, action_type: ActionType) -> None:
        ...

    @abstractmethod
    async def history_events(self, user_id: uuid.UUID, history_request: HistoryRequest) -> List[HistoryResponse]:
        ...


class HistoryService(HistoryServiceABC):
    async def create_history_event(self, user_id: uuid.UUID, user_agent: str, action_type: ActionType) -> None:
        device_db = await self.device_repository.get_or_create(user_agent=user_agent)
        await self.history_repository.add_history_event(user_id, device_db.id, action_type)
        await self.history_repository.commit()

    async def history_events(self, user_id: uuid.UUID, history_request: HistoryRequest) -> List[HistoryResponse]:
        history_db_list = await self.history_repository.get_history_by_user(
            user_id,
            limit=history_request.limit,
            offset=history_request.offset,
        )
        return [HistoryResponse.from_orm(history_db) for history_db in history_db_list]

    def __init__(self, history_repository: HistoryRepository, device_repository: DeviceRepository):
        self.device_repository = device_repository
        self.history_repository = history_repository
