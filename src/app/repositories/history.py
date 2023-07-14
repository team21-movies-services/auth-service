from typing import Sequence
import logging
import uuid
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload

from repositories.base import SQLAlchemyRepository
from models.history import AuthHistory, ActionType

logger = logging.getLogger(__name__)


class HistoryRepository(SQLAlchemyRepository):
    model = AuthHistory

    async def get_history_by_user(self, user_id: uuid.UUID, limit: int = 10, offset: int = 0) -> Sequence[AuthHistory]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.device))
            .offset(offset)
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_history_event(self, user_id: uuid.UUID, device_id: uuid.UUID, action_type: ActionType) -> None:
        db_history = self.model(user_id=user_id, action_type=action_type, device_id=device_id)
        self.session.add(db_history)
        await self.session.commit()
