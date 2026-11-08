
import base64
import hashlib
import hmac
import json
import secrets
import time

from app import config

_PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), _PBKDF2_ITERATIONS
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$")
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), _PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(digest.hex(), expected)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _from_b64url(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def create_token(user_id: int, email: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": int(time.time()) + config.AUTH_TOKEN_EXPIRE_SECONDS,
    }
    signing_input = _b64url(json.dumps(header).encode()) + "." + _b64url(
        json.dumps(payload).encode()
    )
    signature = hmac.new(
        config.AUTH_SECRET.encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    return signing_input + "." + _b64url(signature)


def decode_token(token: str) -> dict | None:
    try:
        head, body, signature = token.split(".")
        expected = hmac.new(
            config.AUTH_SECRET.encode(), f"{head}.{body}".encode(), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64url(expected), signature):
            return None
        payload = json.loads(_from_b64url(body))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None
