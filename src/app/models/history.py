import uuid
import enum

from sqlalchemy.dialects.postgresql import UUID, ENUM

from sqlalchemy import (
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from models import AuthDevice
from models.base import BaseModel, Column
from models.mixins import IdMixin, TsMixinCreated


@enum.unique
class ActionType(enum.Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    CHANGE_PASSWORD = 'change_password'
    CHANGE_INFO = 'change_info'


class AuthHistory(BaseModel, IdMixin, TsMixinCreated):
    """Data model for auth.history db table."""

    __tablename__ = "history"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_history_pkey'),
        # Index("history_user_id_action_id_device_id_uniq", 'user_id', 'action_type', 'device_id', unique=True),
        ForeignKeyConstraint(
            ['user_id'], ['auth.user.id'],
            name='user_id__fk',
        ),
        ForeignKeyConstraint(
            ['device_id'], ['auth.device.id'],
            name='device_id__fk',
        ),
        {"schema": "auth"},
    )

    user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), nullable=False)
    action_type: Mapped[str] = Column(ENUM(ActionType, name="action_type"), nullable=False)
    device_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), nullable=False)

    device: Mapped[AuthDevice] = relationship(
        primaryjoin="foreign(AuthHistory.device_id) == AuthDevice.id",
        uselist=False,
        lazy='selectin',
        # back_populates="history_events"
    )

    def __repr__(self):
        return (
            f"AuthHistory(id={self.id}, user_id={self.user_id}, action_type={self.action_type}, "
            f"device_id={self.device_id}, created_at={self.created_at})",
        )
