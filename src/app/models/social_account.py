import uuid
from typing import TYPE_CHECKING

from models.base import BaseModel, mapped_column
from models.mixins import IdMixin, TsMixinCreated
from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from models import AuthUser


class SocialAccount(BaseModel, IdMixin, TsMixinCreated):
    """Data model for auth.history db table."""

    __tablename__ = "social_account"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_social_account_pkey'),
        Index("social_user_id_user_social_id_uniq", 'user_id', 'user_social_id', unique=True),
        ForeignKeyConstraint(['user_id'], ['auth.user.id'], name='auth_social_user_id_fkey', ondelete="CASCADE"),
        {"schema": "auth"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_social_id = mapped_column(Text, nullable=False)
    social_name = mapped_column(Text, nullable=False)

    user: Mapped["AuthUser"] = relationship(back_populates='social_accounts')

    def __repr__(self):
        return (
            f"SocialAccount(id={self.id}, user_id={self.user_id}, user_social_id={self.user_social_id}, "
            f"social_name={self.social_name}, created_at={self.created_at})",
        )
