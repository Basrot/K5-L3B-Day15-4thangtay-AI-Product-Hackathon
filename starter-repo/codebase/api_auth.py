"""Signed app tokens and active-user authentication dependencies."""

import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)
TOKEN_SECONDS = 3600


def _secret():
    secret = os.environ.get("APP_SECRET", "")
    if len(secret) < 32:
        raise HTTPException(503, "Cấu hình APP_SECRET dài ít nhất 32 ký tự trên server.")
    return secret.encode("utf-8")


def ensure_auth_ready():
    """Fail before creating an account if access tokens cannot be issued."""
    _secret()


def _encode(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unauthorized():
    return HTTPException(401, "Đăng nhập lại để tiếp tục.", headers={"WWW-Authenticate": "Bearer"})


def _mint_token(subject: str) -> dict:
    secret = _secret()
    payload = {"sub": subject, "exp": int(time.time()) + TOKEN_SECONDS}
    body = _encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _encode(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
    return {"access_token": body + "." + signature, "token_type": "bearer", "expires_in": TOKEN_SECONDS}


def issue_access_token(user: dict) -> dict:
    return _mint_token(user["id"])


def issue_token(username: str, password: str) -> dict:
    """Compatibility helper for the environment-seeded legacy admin account."""
    secret = _secret()
    expected_user = os.environ.get("APP_USERNAME", "demo")
    expected_password = os.environ.get("APP_PASSWORD", "")
    user_matches = hmac.compare_digest(username.encode("utf-8"), expected_user.encode("utf-8"))
    password_matches = hmac.compare_digest(password.encode("utf-8"), expected_password.encode("utf-8"))
    if not expected_password or not (user_matches and password_matches):
        raise _unauthorized()
    # Existing app tokens used the username as subject. The auth dependency
    # still resolves that subject to the seeded admin during token expiry.
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
        if not isinstance(payload, dict) or type(payload.get("exp")) is not int or not isinstance(payload.get("sub"), str):
            raise ValueError
        if payload["exp"] <= time.time():
            raise ValueError
        return payload["sub"]
    except (ValueError, UnicodeError, TypeError):
        raise _unauthorized() from None


def require_access(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()
    subject = verify_token(credentials.credentials)
    accounts = getattr(request.app.state, "accounts", None)
    user = accounts.get_by_id(subject) if accounts is not None else None
    if user is None and accounts is not None:
        # Let already-issued username-subject admin tokens age out normally.
        user = accounts.get_by_username(subject)
    if user is None:
        raise _unauthorized()
    return user
