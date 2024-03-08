from typing import Generic, TypeVar

from fastapi_users.authentication.strategy.db.models import AccessTokenProtocol
from fastapi_users.models import ID


class AccessTokenProtocolExtended(Generic[ID], AccessTokenProtocol[ID]):
    refresh_token: str


APE = TypeVar("APE", bound=AccessTokenProtocolExtended)
