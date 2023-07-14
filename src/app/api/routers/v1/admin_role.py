import logging
import uuid
from typing import List

from common.exceptions.role import RoleException
from dependencies.auth import get_auth_admin
from fastapi import APIRouter, Depends, HTTPException, status
from services.role import RoleServiceABC

router = APIRouter(prefix='/users', tags=['Действия с ролями'])

logger = logging.getLogger().getChild('admin-role-actions')


@router.post(
    '/{user_id}/roles',
    summary="Назначить пользователю роли",
    dependencies=[Depends(get_auth_admin)],
)
async def _add_role_to_user(
    user_id: uuid.UUID,
    role_ids: List[uuid.UUID],
    role_service: RoleServiceABC = Depends(),
):
    logger.debug(f'Add roles to user: user_id - {user_id}, roles - {role_ids}')
    try:
        await role_service.add_roles_to_user(user_id, role_ids)
    except RoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.delete(
    '/{user_id}/roles',
    summary="Отобрать у пользователя роли",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_auth_admin)],
)
async def _delete_role_to_user(
    user_id: uuid.UUID,
    role_ids: List[uuid.UUID],
    role_service: RoleServiceABC = Depends(),
):
    logger.debug(f'Remove roles to user: user_id - {user_id}, roles - {role_ids}')
    try:
        await role_service.delete_roles_by_user(user_id, role_ids)
    except RoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.get(
    '/{user_id}/roles',
    summary="Получение прав у пользователя",
    dependencies=[Depends(get_auth_admin)],
)
async def _get_role_to_user(
    user_id: uuid.UUID,
    role_service: RoleServiceABC = Depends(),
):
    logger.debug(f'View roles to user: user_id - {user_id}')
    try:
        response_role = await role_service.get_roles_by_user(user_id)
    except RoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return response_role
