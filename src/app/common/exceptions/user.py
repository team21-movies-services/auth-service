from common.exceptions.base import AppException


class UserException(AppException):
    """Base User Exception"""


class UserAlreadyExists(UserException):
    """User Already Exists"""


class UserNotExists(UserException):
    """User Not Exists"""
