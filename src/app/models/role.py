from typing import TYPE_CHECKING, List

from sqlalchemy import PrimaryKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from models.base import BaseModel, Column
from models.mixins import IdMixin

if TYPE_CHECKING:
    from models import AuthUser


class AuthRole(BaseModel, IdMixin):
    """Data model for auth.role db table."""

    __tablename__ = "role"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_role_pkey'),
        UniqueConstraint('name', name='auth_role_name_unique'),
        {"schema": "auth"},
    )

    name: Mapped[str] = Column(String(127), nullable=True)
    description: Mapped[str] = Column(Text(), nullable=True)

    users: Mapped[List["AuthUser"]] = relationship(
        'AuthUser',
        secondary='auth.user_role',
    )

    def __repr__(self):
        return f"AuthRole(id={self.id}, name={self.name}, description={self.description})"
