from fastapi import Header, HTTPException
from .config import AUTH_TOKEN

def verify_token(authorization: str | None = Header(None)):
    if not authorization or authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True
