from enum import Enum
from typing import List


class ExtendedEnum(Enum):
    """Enum with additional values() method."""

    @classmethod
    def values(cls) -> List:
        """Returns list of values in Enum

        Returns:
            (List): list of Enum values
        """
        return list(cls)
