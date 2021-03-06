from climbing.util import ExtendedEnum


class Category(str, ExtendedEnum):
    """Перечисление для хранения сложностей трасс."""

    FIVE_A = "5a"
    FIVE_A_PLUS = "5a+"
    FIVE_B = "5b"
    FIVE_B_PLUS = "5b+"
    FIVE_C = "5c"
    FIVE_C_PLUS = "5c+"
    SIX_A = "6a"
    SIX_A_PLUS = "6a+"
    SIX_B = "6b"
    SIX_B_PLUS = "6b+"
    SIX_C = "6c"
    SIX_C_PLUS = "6c+"
    SEVEN_A = "7a"
    SEVEN_A_PLUS = "7a+"
    SEVEN_B = "7b"
    SEVEN_B_PLUS = "7b+"
    SEVEN_C = "7c"
    SEVEN_C_PLUS = "7c+"
    EIGHT_A = "8a"
    EIGHT_A_PLUS = "8a+"
    EIGHT_B = "8b"
    EIGHT_B_PLUS = "8b+"
    EIGHT_C = "8c"
    EIGHT_C_PLUS = "8c+"
    NINE_A = "9a"
    NINE_A_PLUS = "9a+"
    NINE_B = "9b"
    NINE_B_PLUS = "9b+"
    NINE_C = "9c"
    NINE_C_PLUS = "9c+"
