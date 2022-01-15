from pprint import pprint
from core.security import generate_jwt, verify_jwt


pprint(
    generate_jwt({"iat": 1516239022, "name": "John Doe", "sub": "1234567890"})
)

print()
