import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Boolean,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from models.base import BaseModel, Column
from models.mixins import IdMixin, TsMixinCreated, TsMixinUpdated

if TYPE_CHECKING:
    from models import AuthRole, SocialAccount


class AuthUser(BaseModel, IdMixin, TsMixinCreated, TsMixinUpdated):
    """Data model for auth.user db table."""

    __tablename__ = "user"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_user_pkey'),
        UniqueConstraint('email', name='auth_user_email_unique'),
        {"schema": "auth"},
    )

    first_name: Mapped[str] = Column(String(127), nullable=True)
    last_name: Mapped[str] = Column(String(127), nullable=True)

    email: Mapped[str] = Column(String(255), nullable=False)
    password: Mapped[str] = Column(String(127), nullable=False)

    is_superuser: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    roles: Mapped[List["AuthRole"]] = relationship(
        'AuthRole',
        secondary='auth.user_role',
    )
    social_accounts: Mapped["SocialAccount"] = relationship(back_populates='user')

    def __repr__(self):
        return (
            f"AuthUser(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
            f"email={self.email}, password={self.password}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )


class AuthUserRole(BaseModel, IdMixin, TsMixinCreated):
    """Data model for auth.user_role db table."""

    __tablename__ = "user_role"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_user_role_pkey'),
        Index("user_role_user_id_role_id_uniq", 'user_id', 'role_id', unique=True),
        ForeignKeyConstraint(
            ['user_id'],
            ['auth.user.id'],
            name='user_id__fk',
        ),
        ForeignKeyConstraint(
            ['role_id'],
            ['auth.role.id'],
            name='role_id__fk',
        ),
        {"schema": "auth"},
    )

    user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), nullable=False)
    role_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), nullable=False)

    def __repr__(self):
        return (
            f"AuthUserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id}, "
            f"created_at={self.created_at})"
        )


class AuthUserRememberDevice(BaseModel, IdMixin, TsMixinCreated):
    """Data model for auth.user_remember_device db table."""

    __tablename__ = "user_remember_device"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_user_remember_device_pkey'),
        Index("user_remember_device_user_id_device_id_uniq", 'user_id', 'device_id', unique=True),
        ForeignKeyConstraint(
            ['user_id'],
            ['auth.user.id'],
            name='user_id__fk',
        ),
        ForeignKeyConstraint(
            ['device_id'],
            ['auth.device.id'],
            name='device_id__fk',
        ),
        {"schema": "auth"},
    )

    user_id: Mapped[UUID] = Column(UUID(as_uuid=True), nullable=False)
    device_id: Mapped[UUID] = Column(UUID(as_uuid=True), nullable=False)

    def __repr__(self):
        return (
            f"AuthUserRememberDevice(id={self.id}, user_id={self.user_id}, device_id={self.device_id}, "
            f"created_at={self.created_at})"
        )
