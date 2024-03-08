from typing import Any, Coroutine

from fastapi import Response, status
from fastapi.responses import JSONResponse
from fastapi_users.authentication import BearerTransport, Transport
from fastapi_users.authentication.transport.bearer import BearerResponse
from fastapi_users.openapi import OpenAPIResponseType

from climbing.core.refresh_token.db.models import AccessTokenProtocolExtended


class TransportExtended(Transport):
    async def get_login_response(
        self, token: AccessTokenProtocolExtended
    ) -> Response: ...


class BearerResponseExtended(BearerResponse):
    refresh_token: str


class BearerTransportRefresh(BearerTransport, TransportExtended):
    async def get_login_response(
        self,
        token: AccessTokenProtocolExtended,
    ) -> Coroutine[Any, Any, Response]:
        bearer_response = BearerResponseExtended(
            access_token=token.token,
            refresh_token=token.refresh_token,
            token_type="bearer",
        )
        return JSONResponse(bearer_response.model_dump())

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponseExtended,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
                            "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
                            "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
                            "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
                            "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
                            "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
                            "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
                            "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
                            "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }
