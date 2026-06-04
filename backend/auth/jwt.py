"""JWT issue and verification."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from backend.config import NexusConfig

ALGORITHM = "HS256"


def create_access_token(config: NexusConfig, tenant_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_expire_minutes)
    payload = {
        "sub": tenant_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, config.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(config: NexusConfig, token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, config.jwt_secret, algorithms=[ALGORITHM])
    except JWTError:
        return None
