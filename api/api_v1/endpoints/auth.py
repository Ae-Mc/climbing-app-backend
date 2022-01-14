from typing import Any, Dict
from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse

from core.security import generate_jwt, verify_jwt as security_verify_jwt
from schemas.result import Result


router = APIRouter()


@router.post("", response_class=PlainTextResponse)
def get_jwt(claims: Dict[str, Any] = Body(...)):
    return Result(generate_jwt(claims))


@router.get(
    "/verify-jwt",
    response_class=PlainTextResponse,
    responses={
        200: {
            "content": {
                "text/plain": {
                    "examples": {
                        "Success": {"value": "true"},
                        "Failure": {"value": "false"},
                    },
                },
            },
            "model": bool,
        }
    },
)
def verify_jwt(jwt: str):
    """Returns true if verified successfully else false"""
    return PlainTextResponse(str(security_verify_jwt(jwt)).lower())
