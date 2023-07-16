import logging
from typing import Optional

from common.exceptions.user import UserAlreadyExists, UserNotExists
from models.user import AuthUser
from repositories.base import SQLAlchemyRepository
from sqlalchemy.exc import IntegrityError

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
