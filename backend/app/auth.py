import secrets

from fastapi import Header, HTTPException

from app.config import settings


def require_admin(authorization: str | None = Header(None)) -> None:
    """Admin endpoints change what every SDK client sees, so they are gated."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(token, settings.admin_token):
        raise HTTPException(status_code=401, detail="Invalid token")
