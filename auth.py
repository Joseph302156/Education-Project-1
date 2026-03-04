from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
BEARER = HTTPBearer(auto_error=False)


def _check_token(token: str) -> bool:
    return token and token == settings.api_key


async def verify_api_key(
    x_api_key: str | None = Security(API_KEY_HEADER),
    credentials: HTTPAuthorizationCredentials | None = Security(BEARER),
) -> str:
    if x_api_key and _check_token(x_api_key):
        return x_api_key
    if credentials and _check_token(credentials.credentials):
        return credentials.credentials
    raise HTTPException(status_code=401, detail="Invalid or missing API key")
