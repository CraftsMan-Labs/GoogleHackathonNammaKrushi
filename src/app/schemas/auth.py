from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None