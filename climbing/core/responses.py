from typing import Any

SUPERUSER_REQUIRED: dict[int | str, dict[str, Any]] = {
    403: {"description": "Not a superuser"}
}
LOGIN_REQUIRED: dict[int | str, dict[str, Any]] = {
    401: {"description": "Missing token or inactive user"}
}
ID_NOT_FOUND = {404: {"description": "Item with ID not found"}}
