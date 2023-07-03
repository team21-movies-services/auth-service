import logging
import uuid
from typing import List

from sqlalchemy.sql import select, delete
from sqlalchemy.exc import IntegrityError

from common.exceptions.role import RoleAlreadyExists
from models import AuthRole, AuthUser, AuthUserRole
from repositories.base import SQLAlchemyRepository

logger = logging.getLogger(__name__)


class RoleRepository(SQLAlchemyRepository):
    model = AuthRole

    async def get_roles(self):
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get_roles_by_user(self, user_id: uuid.UUID):
        stmt = (
            select(self.model)
            .join(self.model.users)
            .where(AuthUser.id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_role(self, **fields):
        role_db = AuthRole(**fields)
        self.session.add(role_db)
        try:
            await self.session.commit()
        except IntegrityError:
            raise RoleAlreadyExists()
        return role_db

    async def add_roles_to_user(self, user_id, role_ids: List[uuid.UUID]):
        self.session.add_all(
            (AuthUserRole(role_id=role_id, user_id=user_id) for role_id in role_ids),
        )
        try:
            await self.session.commit()
        except IntegrityError:
            raise RoleAlreadyExists()

    async def delete_roles_by_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]):
        stmt = (
            delete(AuthUserRole)
            .where(AuthUserRole.role_id.in_(role_ids))
            .where(AuthUserRole.user_id == user_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()
