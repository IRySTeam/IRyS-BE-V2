from fastapi import APIRouter, Response

from api.auth.request.auth import RefreshTokenRequest, VerifyTokenRequest
from api.auth.response.auth import RefreshTokenResponse
from app.auth.services.token import TokenService
from core.utils import CustomExceptionHelper
from core.exceptions import (
    InvalidTokenException,
)

auth_router = APIRouter()


@auth_router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    responses={
        "400": CustomExceptionHelper.get_exception_response(
            InvalidTokenException, "Invalid refresh token"
        )
    },
)
async def refresh_token(request: RefreshTokenRequest):
    token = await TokenService().create_refresh_token(
        token=request.token, refresh_token=request.refresh_token
    )
    return {"token": token.token, "refresh_token": token.refresh_token}


@auth_router.post("/verify")
async def verify_token(request: VerifyTokenRequest):
    await TokenService().verify_token(token=request.token)
    return Response(status_code=200)
