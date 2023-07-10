class AppException(Exception):
    """Base Exception"""


class ObjectDoesNotExist(Exception):
    """Does not exist Exception"""


class TooManyRequests(AppException):
    """Too Many Requests Exception"""
