from json import loads as _loads
from pydantic import BaseModel


class MultipartFormDataCompatibleModel(BaseModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**_loads(value))
        if isinstance(value, dict):
            return cls(**value)
        return value
