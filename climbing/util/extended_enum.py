from enum import Enum


class ExtendedEnum(Enum):
    """Enum with additional values() method."""

    @classmethod
    def values(cls) -> list:
        """Returns list of values in Enum

        Returns:
            (List): list of Enum values
        """
        return list(cls)
