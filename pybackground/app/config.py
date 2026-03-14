from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "navigation.db"
SECRET_KEY = os.getenv("NAV_SECRET_KEY", "navigation-dev-secret")
ACCESS_TOKEN_EXPIRE_HOURS = 12
DEFAULT_ADMIN_USERNAME = os.getenv("NAV_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("NAV_ADMIN_PASSWORD", "admin123")

