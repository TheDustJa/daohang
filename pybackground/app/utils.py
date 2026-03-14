from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def password_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

