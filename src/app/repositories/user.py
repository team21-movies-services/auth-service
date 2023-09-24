import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from common.exceptions.user import UserAlreadyExists, UserNotExists
from models.user import AuthUser
from repositories.base import SQLAlchemyRepository

logger = logging.getLogger(__name__)


class UserRepository(SQLAlchemyRepository[AuthUser]):
    model = AuthUser

    async def get_user_by_field(self, raise_if_notfound: bool = True, **fields) -> Optional[AuthUser]:
        """Получение записи пользователя по полю если оно существует"""

        result = await self.get_by(**fields)
        if not result and raise_if_notfound:
            logger.error(f"User does not exists: {fields}")
            raise UserNotExists(f"User with {fields} does not exists")

        return result

    async def get_user_by_field_with_roles(self, **fields) -> AuthUser:
        """Возвращает пользователя с ролями"""

        query = (
            select(AuthUser)
            .filter_by(**fields)
            .join(AuthUser.roles, isouter=True)
            .options(selectinload(AuthUser.roles))
        )
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotExists(f"User with {fields} does not exists")

        return user

    async def update_user_fields(self, user_db: AuthUser, **fields) -> None:
        for field, value in fields.items():
            if hasattr(user_db, field):
                setattr(user_db, field, value)
        await self.session.commit()

    async def create_user(self, **fields) -> AuthUser:
        """Создание пользователя в БД postgres."""
        db_user = self.model()
        for field, value in fields.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)
        self.session.add(db_user)

        try:
            await self.session.commit()
        except IntegrityError:
            raise UserAlreadyExists()

        return db_user
