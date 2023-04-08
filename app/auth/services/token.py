from datetime import datetime, timedelta
from app.auth.schemas.jwt import RefreshTokenSchema
from core.db import Transactional
from core.exceptions.token import InvalidTokenException
from core.utils import (
    TokenHelper,
    HashHelper,
    StringHelper,
)
from core.repository import (
    UserRepo
)


class TokenService:
    user_repo = UserRepo()
    
    async def verify_token(self, token: str) -> None:
        TokenHelper.decode(token=token)

    @Transactional()
    async def create_refresh_token(
        self,
        token: str,
        refresh_token: str,
    ) -> RefreshTokenSchema:
        token = TokenHelper.decode_expired_token(token=token)
        user = await UserRepo().get_by_id(id=token.get("user_id"))

        if not HashHelper.check_hash(user.refresh_token, refresh_token):
            raise InvalidTokenException

        raw_refresh_token = StringHelper.random_string(10)
        refresh_token = HashHelper.get_hash(raw_refresh_token)
        refresh_token_valid_until = datetime.utcnow() + timedelta(hours=24)
        
        # Update user
        await self.user_repo.update_by_id(
            id=user.id,
            params={
                "refresh_token": raw_refresh_token,
                "refresh_token_valid_until": refresh_token_valid_until
            },
        )

        return RefreshTokenSchema(
            token=TokenHelper.encode(payload={"user_id": token.get("user_id"), "is_email_verified": token.get("is_email_verified")}),
            refresh_token=refresh_token,
        )
