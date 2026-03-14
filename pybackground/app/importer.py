from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .database import init_db
from .schemas import SiteCreate
from .utils import now_iso


DEFAULT_IMPORT_SOURCES = [
    Path(__file__).resolve().parents[2] / "数据爬取" / "pybackground_sites.json",
    Path(__file__).resolve().parents[2] / "数据爬取" / "collected_sites.json",
    Path(__file__).resolve().parents[2] / "数据爬取" / "data" / "deduped_sites.json",
]


def normalize_site(site: dict[str, Any], index: int, default_level1: str) -> SiteCreate | None:
    name = str(site.get("name", "")).strip() or str(site.get("title", "")).strip()
    url = str(site.get("url", "")).strip() or str(site.get("site_url", "")).strip()
    description = str(site.get("description", "")).strip() or str(site.get("desc", "")).strip()
    level1 = str(site.get("level1", "")).strip() or default_level1
    level2 = str(site.get("level2", "")).strip() or str(site.get("category", "")).strip() or "未分类"
    level3 = str(site.get("level3", "")).strip()
    logo = str(site.get("logo", "")).strip() or name[:1]
    tags = site.get("tags", [])

    if not name:
        return None

    if isinstance(tags, str):
        tags = [item.strip() for item in tags.split(",") if item.strip()]
    if not isinstance(tags, list):
        tags = []

    return SiteCreate(
        name=name,
        url=url,
        logo=logo,
        description=description,
        level1=level1,
        level2=level2,
        level3=level3,
        tags=tags,
        isRecommended=bool(site.get("isRecommended", False)),
        sortOrder=int(site.get("sortOrder", index + 1)),
        type=str(site.get("type", "site")).strip() or "site",
        content=str(site.get("content", "")).strip(),
        status=str(site.get("status", "approved")).strip() or "approved",
    )


def load_sites_from_source(source: Path, default_level1: str) -> list[SiteCreate]:
    payload = json.loads(source.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        sites = payload
    elif isinstance(payload, dict) and isinstance(payload.get("pybackground_sites"), list):
        sites = payload["pybackground_sites"]
    elif isinstance(payload, dict) and isinstance(payload.get("categories"), list):
        sites = []
        for category_item in payload["categories"]:
            category_name = str(category_item.get("name", "")).strip() or "未分类"
            for item in category_item.get("items", []):
                merged = dict(item)
                merged.setdefault("level2", category_name)
                sites.append(merged)
    else:
        raise ValueError(f"Unsupported JSON structure: {source}")

    normalized: list[SiteCreate] = []
    for index, site in enumerate(sites):
        if not isinstance(site, dict):
            continue
        item = normalize_site(site, index, default_level1=default_level1)
        if item is not None:
            normalized.append(item)
    return normalized


def resolve_import_source(source_path: str | None, default_level1: str) -> tuple[Path, list[SiteCreate]]:
    if source_path:
        source = Path(source_path).expanduser().resolve()
        return source, load_sites_from_source(source, default_level1=default_level1)

    for source in DEFAULT_IMPORT_SOURCES:
        if not source.exists():
            continue
        try:
            return source, load_sites_from_source(source, default_level1=default_level1)
        except Exception:
            continue
    raise FileNotFoundError("No valid import source found")


def import_sites(
    conn: sqlite3.Connection,
    sites: list[SiteCreate],
    *,
    default_status: str = "approved",
    skip_existing: bool = True,
) -> tuple[int, int]:
    inserted = 0
    skipped = 0
    timestamp = now_iso()

    for site in sites:
        existing = conn.execute(
            "SELECT id FROM sites WHERE name = ? AND url = ? AND level1 = ? AND level2 = ?",
            (site.name, site.url, site.level1, site.level2),
        ).fetchone()
        if existing and skip_existing:
            skipped += 1
            continue

        conn.execute(
            """
            INSERT INTO sites (
                name, url, logo, description, level1, level2, level3, tags,
                isRecommended, sortOrder, type, content, status, submitterEmail,
                createdAt, updatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                site.name,
                site.url,
                site.logo or site.name[:1],
                site.description,
                site.level1,
                site.level2,
                site.level3,
                json.dumps(site.tags, ensure_ascii=False),
                1 if site.isRecommended else 0,
                site.sortOrder,
                site.type,
                site.content,
                site.status or default_status,
                None,
                timestamp,
                timestamp,
            ),
        )
        inserted += 1

    return inserted, skipped


def ensure_database_ready() -> None:
    init_db()
