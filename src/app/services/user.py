import datetime
import logging
import uuid
from abc import ABC, abstractmethod

from passlib.context import CryptContext

from common.exceptions.user import UserException
from repositories import UserRepository
from schemas.oauth import OAuthUserInfoSchema
from schemas.request.user import (
    UserChangeInfoSchema, UserRegistrationSchema,
    UserLoginSchema, UserChangePasswordSchema,
)
from schemas.response.user import UserResponse


from domain.oauth.dto import OAuthUserInfoDto


pwd_context = CryptContext(schemes=["bcrypt"])
logger = logging.getLogger(__name__)


class UserServiceABC(ABC):
    @abstractmethod
    async def create_user(self, user_schema: UserRegistrationSchema) -> UserResponse:
        ...

    @abstractmethod
    async def login(self, user: UserLoginSchema) -> UserResponse:
        ...

    @abstractmethod
    async def change_info(self, user_id: uuid.UUID,
                          info_schema: UserChangeInfoSchema) -> UserResponse:
        ...

    @abstractmethod
    async def password_change(self, user_id: uuid.UUID,
                              password_schema: UserChangePasswordSchema) -> UserResponse:
        ...

    @abstractmethod
    async def user_info(self, user_id: uuid.UUID) -> UserResponse:
        ...

    @abstractmethod
    async def get_or_create_user_from_oauth(self, user_data: OAuthUserInfoDto) -> uuid.UUID:
        ...


class UserService(UserServiceABC):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_or_create_user_from_oauth(self, user_data: OAuthUserInfoDto) -> uuid.UUID:
        """Создание пользователя на основе данных полученных из стороннего сервиса аутентификации."""
        user_db = await self.user_repository.get_by(email=user_data.email)
        if not user_db:
            # FIXME: генерируем рандомный пароль для пользователей вошедших через oauth,
            #  в дальнейшем и будет доступен только сброс пароля?
            password = pwd_context.encrypt(str(uuid.uuid4()))
            user_db = await self.user_repository.create_user(password=password, **user_data.as_dict())
        return user_db.id

    def _verify_password(self, plan_password: str, hashed_password: str) -> bool:
        """Валидация пароля."""
        return pwd_context.verify(plan_password, hashed_password)

    async def create_user(self, user_schema: UserRegistrationSchema) -> UserResponse:
        """Создание пользователя."""
        user_schema.password = pwd_context.encrypt(user_schema.password)

        user_db = await self.user_repository.create_user(
            **user_schema.dict(exclude={'password_confirm'}),
        )

        return UserResponse.from_orm(user_db)

    async def login(self, login_schema: UserLoginSchema) -> UserResponse:
        """Логин пользователя."""
        user_db = await self.user_repository.get_user_by_field(email=login_schema.email)

        if not self._verify_password(login_schema.password, user_db.password):
            raise UserException("Wrong password")

        return UserResponse.from_orm(user_db)

    async def change_info(self, user_id: uuid.UUID,
                          info_schema: UserChangeInfoSchema) -> UserResponse:
        """Изменение информации о пользователе"""
        user_db = await self.user_repository.get_user_by_field(id=user_id)

        await self.user_repository.update_user_fields(user_db, **info_schema.dict())
        return UserResponse.from_orm(user_db)

    async def password_change(self, user_id: uuid.UUID,
                              password_schema: UserChangePasswordSchema) -> UserResponse:
        """Изменение пароля пользователя"""
        user_db = await self.user_repository.get_user_by_field(id=user_id)

        if not self._verify_password(password_schema.password, user_db.password):
            logger.info(f"Change password: password wrong, user_id - {user_id}")
            raise UserException("Wrong password")

        await self.user_repository.update_user_fields(
            user_db,
            password=pwd_context.encrypt(password_schema.new_password),
            updated_at=datetime.datetime.utcnow(),
        )
        return UserResponse.from_orm(user_db)

    async def user_info(self, user_id: uuid.UUID) -> UserResponse:
        """Получение информации о пользователе"""
        user_db = await self.user_repository.get_user_by_field(id=user_id)
        return UserResponse.from_orm(user_db)
