import http
import logging

from config.env import TOKEN

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.openapi.models import APIKey

from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

from telegram_webapp_auth.auth import TelegramAuthenticator
from telegram_webapp_auth.auth import WebAppUser
from telegram_webapp_auth.auth import generate_secret_key
from telegram_webapp_auth.errors import InvalidInitDataError

class TelegramInitDataScheme(SecurityBase):
    def __init__(self):
        self.scheme_name = "Telegram-Init-Data"
        self.model = APIKey(  # <-- Добавляем, чтобы Swagger работал
            **{
                "type": "apiKey",
                "in": "header",
                "name": "Authorization Telegram-Init-Data",
            }
        )

    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")

        scheme, param = get_authorization_scheme_param(authorization)

        if scheme.lower() != self.scheme_name.lower():
            raise HTTPException(
                status_code=401,
                detail=f"Invalid auth scheme: {scheme}, expected '{self.scheme_name}'"
            )

        return param
    
class TelegramTokenDataScheme(SecurityBase):
    def __init__(self):
        self.scheme_name = "Telegram-Bot-Token"
        self.model = APIKey(
            **{
                "type": "apiKey",
                "in": "header",
                "name": "Authorization Telegram-Bot-Token",
            }
        )

    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")

        scheme, param = get_authorization_scheme_param(authorization)
        if scheme.lower() != self.scheme_name.lower():
            raise HTTPException(
                status_code=401,
                detail=f"Invalid auth scheme: {scheme}, expected '{self.scheme_name}'"
            )

        return param
    

def get_telegram_authenticator() -> TelegramAuthenticator:
    secret_key = generate_secret_key(TOKEN)
    return TelegramAuthenticator(secret_key)


def get_current_user(
    auth_cred: HTTPAuthorizationCredentials = Depends(TelegramInitDataScheme()),
    telegram_authenticator: TelegramAuthenticator = Depends(get_telegram_authenticator),
) -> WebAppUser:
    try:
        init_data = telegram_authenticator.validate(auth_cred)
    except InvalidInitDataError:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )
    except Exception:
        raise HTTPException(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Internal error.",
        )

    if init_data.user is None:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )

    return init_data.user

async def verify_bot_token(auth_cred: HTTPAuthorizationCredentials = Depends(TelegramTokenDataScheme)):
    return True