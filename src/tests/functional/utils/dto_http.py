import enum
from dataclasses import dataclass

from http import HTTPStatus

from typing import Optional, List, Dict
from multidict import CIMultiDictProxy


class HttpMethod(enum.Enum):
    GET = 'get'
    POST = 'post'


@dataclass
class HttpResponse:
    status: HTTPStatus | int
    body: Optional[List | Dict] = None
    headers: Optional[CIMultiDictProxy[str]] = None
