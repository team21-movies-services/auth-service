from sqlalchemy import (
    Text,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Column
from models.mixins import IdMixin


class AuthDevice(BaseModel, IdMixin):
    """Data model for auth.device db table."""

    __tablename__ = "device"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_device_pkey'),
        UniqueConstraint('user_agent', name='auth_device_user_agent_unique'),
        {"schema": "auth"},
    )

    user_agent: Mapped[str] = Column(Text(), nullable=True)

    def __repr__(self):
        return f"AuthDevice(id={self.id}, user_agent={self.user_agent})"
