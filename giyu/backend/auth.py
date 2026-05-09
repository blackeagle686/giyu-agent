import os
import hmac
from fastapi import Header, HTTPException


def _safe_equal(a: str, b: str) -> bool:
    return hmac.compare_digest((a or "").encode(), (b or "").encode())


def require_agent_token(x_agent_token: str = Header(default="")) -> None:
    expected = os.getenv("GIYU_AGENT_TOKEN", "").strip()
    if not expected:
        return
    if not _safe_equal(x_agent_token.strip(), expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


def validate_clearance_token(token: str) -> bool:
    expected = os.getenv("GIYU_RENGOKU_TOKEN", "").strip()
    if not expected:
        return False
    return _safe_equal(token.strip(), expected)
