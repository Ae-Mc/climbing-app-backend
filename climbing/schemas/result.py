from typing import Any, Generic, Optional, TypeVar
from pydantic import Field
from pydantic.generics import GenericModel

ResultType = TypeVar("ResultType")


class Result(GenericModel, Generic[ResultType]):
    """Class for returning results of any types deserializable by standard json
    deserializers."""

    result: ResultType = Field(...)
