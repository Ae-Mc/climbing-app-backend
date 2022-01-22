from uuid import uuid4

from sqlalchemy import Column, MetaData
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy_utils import UUIDType


@as_declarative()
class Base:  # pylint: disable=too-few-public-methods
    """Base class for any database table model

    Attributes:
        id: All models must have id primary key
        __name__ (str): name of class. Check python docs for more details
    """

    __name__: str
    metadata: MetaData

    id = Column(UUIDType, primary_key=True, default=uuid4)

    @declared_attr
    def __tablename__(self) -> str:
        """Generate table name automatically"""
        return self.__name__.lower()
