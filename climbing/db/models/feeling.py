from climbing.util import ExtendedEnum


class Feeling(str, ExtendedEnum):
    """Перечисление для хранения ощущений от трассы
    (легко, нормально, сложно)."""

    EASY = "EASY"
    NORMAL = "NORMAL"
    HARD = "HARD"
