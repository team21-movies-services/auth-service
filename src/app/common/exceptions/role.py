from common.exceptions import AppException


class RoleException(AppException):
    """Base Role Exception"""


class RoleAlreadyExists(RoleException):
    """Role Already Exists"""
