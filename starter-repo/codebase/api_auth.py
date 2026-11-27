"""Shared demo login with expiring, HMAC-signed bearer tokens."""

import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)
TOKEN_SECONDS = 3600


def _secret():
    secret = os.environ.get("APP_SECRET", "")
    if len(secret) < 32 or not os.environ.get("APP_PASSWORD"):
        raise HTTPException(503, "Cấu hình APP_PASSWORD và APP_SECRET ít nhất 32 ký tự trên server.")
    return secret.encode("utf-8")


def _encode(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unauthorized():
    return HTTPException(401, "Đăng nhập lại để tiếp tục.", headers={"WWW-Authenticate": "Bearer"})


def issue_token(username: str, password: str) -> dict:
    secret = _secret()
    expected_user = os.environ.get("APP_USERNAME", "demo")
    user_matches = hmac.compare_digest(username.encode("utf-8"), expected_user.encode("utf-8"))
    password_matches = hmac.compare_digest(
        password.encode("utf-8"), os.environ["APP_PASSWORD"].encode("utf-8")
    )
    if not (user_matches and password_matches):
        raise _unauthorized()
    payload = {"sub": username, "exp": int(time.time()) + TOKEN_SECONDS}
    body = _encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _encode(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
    return {"access_token": body + "." + signature, "token_type": "bearer", "expires_in": TOKEN_SECONDS}


def verify_token(token: str) -> str:
    secret = _secret()
    try:
        if len(token) > 1024:
            raise ValueError
        body, signature = token.split(".")
        expected = _encode(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if not isinstance(payload, dict) or type(payload.get("exp")) is not int:
            raise ValueError
        if payload["exp"] <= time.time() or payload.get("sub") != os.environ.get("APP_USERNAME", "demo"):
            raise ValueError
    except (ValueError, UnicodeError, TypeError):
        raise _unauthorized() from None
    return payload["sub"]


def require_access(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()
    return verify_token(credentials.credentials)
