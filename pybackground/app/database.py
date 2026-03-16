from __future__ import annotations

import json
import sqlite3
from contextlib import closing

from .config import DATA_DIR, DB_PATH, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME
from .seed_data import SEED_ARTICLES, SEED_SITES
from .utils import now_iso, password_hash


ARTICLE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    logo TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    level1 TEXT NOT NULL DEFAULT '',
    level2 TEXT NOT NULL DEFAULT '',
    level3 TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    isRecommended INTEGER NOT NULL DEFAULT 0,
    sortOrder INTEGER NOT NULL DEFAULT 0,
    content TEXT NOT NULL DEFAULT '',
    contentFormat TEXT NOT NULL DEFAULT 'html',
    status TEXT NOT NULL DEFAULT 'approved',
    submitterEmail TEXT,
    legacySiteId INTEGER UNIQUE,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL
)
"""


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with closing(get_db()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                passwordHash TEXT NOT NULL,
                createdAt TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL DEFAULT '',
                logo TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                level1 TEXT NOT NULL DEFAULT '',
                level2 TEXT NOT NULL DEFAULT '',
                level3 TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                isRecommended INTEGER NOT NULL DEFAULT 0,
                sortOrder INTEGER NOT NULL DEFAULT 0,
                type TEXT NOT NULL DEFAULT 'site',
                content TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'approved',
                submitterEmail TEXT,
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL
            )
            """
        )
        cursor.execute(ARTICLE_TABLE_SQL)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS friend_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                siteName TEXT NOT NULL,
                siteUrl TEXT NOT NULL,
                siteDesc TEXT NOT NULL DEFAULT '',
                contactEmail TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL DEFAULT ''
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parentId INTEGER,
                sortOrder INTEGER NOT NULL DEFAULT 0,
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL,
                UNIQUE(name, parentId),
                FOREIGN KEY(parentId) REFERENCES categories(id) ON DELETE CASCADE
            )
            """
        )
        ensure_column(cursor, "articles", "contentFormat", "TEXT NOT NULL DEFAULT 'html'")
        ensure_column(cursor, "articles", "legacySiteId", "INTEGER")
        ensure_column(cursor, "friend_links", "updatedAt", "TEXT NOT NULL DEFAULT ''")
        ensure_column(cursor, "sites", "clickCount", "INTEGER NOT NULL DEFAULT 0")
        ensure_column(cursor, "articles", "clickCount", "INTEGER NOT NULL DEFAULT 0")
        ensure_column(cursor, "sites", "likes", "INTEGER NOT NULL DEFAULT 0")
        ensure_column(cursor, "sites", "dislikes", "INTEGER NOT NULL DEFAULT 0")
        ensure_column(cursor, "articles", "likes", "INTEGER NOT NULL DEFAULT 0")
        ensure_column(cursor, "articles", "dislikes", "INTEGER NOT NULL DEFAULT 0")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL,
                checkinDate TEXT NOT NULL,
                streak INTEGER NOT NULL DEFAULT 1,
                totalPoints INTEGER NOT NULL DEFAULT 0,
                createdAt TEXT NOT NULL,
                UNIQUE(fingerprint, checkinDate)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL,
                contentType TEXT NOT NULL,
                contentId INTEGER NOT NULL,
                voteType TEXT NOT NULL,
                createdAt TEXT NOT NULL,
                UNIQUE(fingerprint, contentType, contentId)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                type TEXT NOT NULL DEFAULT 'info',
                isActive INTEGER NOT NULL DEFAULT 1,
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL
            )
            """
        )
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_legacy_site_id ON articles(legacySiteId)")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL DEFAULT 'feature',
                content TEXT NOT NULL DEFAULT '',
                createdAt TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contentType TEXT NOT NULL,
                contentId INTEGER NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                createdAt TEXT NOT NULL
            )
            """
        )
        seed_admin(cursor)
        migrate_legacy_articles(cursor)
        seed_sites(cursor)
        seed_articles(cursor)
        seed_categories(cursor)
        conn.commit()


def ensure_column(cursor: sqlite3.Cursor, table_name: str, column_name: str, definition: str) -> None:
    columns = {row["name"] for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def seed_admin(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] > 0:
        return
    cursor.execute(
        "INSERT INTO admins (username, passwordHash, createdAt) VALUES (?, ?, ?)",
        (DEFAULT_ADMIN_USERNAME, password_hash(DEFAULT_ADMIN_PASSWORD), now_iso()),
    )


def migrate_legacy_articles(cursor: sqlite3.Cursor) -> None:
    site_columns = {row["name"] for row in cursor.execute("PRAGMA table_info(sites)").fetchall()}
    if "type" not in site_columns:
        return

    rows = cursor.execute("SELECT * FROM sites WHERE type = 'article'").fetchall()
    if not rows:
        return

    for row in rows:
        payload = dict(row)
        cursor.execute(
            """
            INSERT OR IGNORE INTO articles (
                name, url, logo, description, level1, level2, level3, tags,
                isRecommended, sortOrder, content, contentFormat, status,
                submitterEmail, legacySiteId, createdAt, updatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["name"],
                payload.get("url", ""),
                payload.get("logo", "") or payload["name"][:1],
                payload.get("description", ""),
                payload.get("level1", ""),
                payload.get("level2", ""),
                payload.get("level3", ""),
                payload.get("tags", "[]"),
                payload.get("isRecommended", 0),
                payload.get("sortOrder", 0),
                payload.get("content", ""),
                "html",
                payload.get("status", "approved"),
                payload.get("submitterEmail"),
                payload["id"],
                payload.get("createdAt", now_iso()),
                payload.get("updatedAt", now_iso()),
            ),
        )

    cursor.execute("DELETE FROM sites WHERE type = 'article'")


def seed_sites(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT COUNT(*) FROM sites")
    if cursor.fetchone()[0] > 0:
        return

    timestamp = now_iso()
    for site in SEED_SITES:
        cursor.execute(
            """
            INSERT INTO sites (
                name, url, logo, description, level1, level2, level3, tags,
                isRecommended, sortOrder, type, content, status, submitterEmail,
                createdAt, updatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'site', '', ?, ?, ?, ?)
            """,
            (
                site["name"],
                site.get("url", ""),
                site.get("logo", "") or site["name"][:1],
                site.get("description", ""),
                site.get("level1", ""),
                site.get("level2", ""),
                site.get("level3", ""),
                json.dumps(site.get("tags", []), ensure_ascii=False),
                1 if site.get("isRecommended") else 0,
                site.get("sortOrder", 0),
                site.get("status", "approved"),
                None,
                timestamp,
                timestamp,
            ),
        )


def seed_articles(cursor: sqlite3.Cursor) -> None:
    timestamp = now_iso()
    for article in SEED_ARTICLES:
        existing = cursor.execute("SELECT id FROM articles WHERE name = ?", (article["name"],)).fetchone()
        if existing is not None:
            continue
        cursor.execute(
            """
            INSERT INTO articles (
                name, url, logo, description, level1, level2, level3, tags,
                isRecommended, sortOrder, content, contentFormat, status,
                submitterEmail, createdAt, updatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                article["name"],
                article.get("url", ""),
                article.get("logo", "") or article["name"][:1],
                article.get("description", ""),
                article.get("level1", ""),
                article.get("level2", ""),
                article.get("level3", ""),
                json.dumps(article.get("tags", []), ensure_ascii=False),
                1 if article.get("isRecommended") else 0,
                article.get("sortOrder", 0),
                article.get("content", ""),
                article.get("contentFormat", "markdown"),
                article.get("status", "approved"),
                None,
                timestamp,
                timestamp,
            ),
        )


def seed_categories(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] > 0:
        return

    timestamp = now_iso()
    level1_map: dict[str, int] = {}
    rows = cursor.execute(
        """
        SELECT DISTINCT level1, level2 FROM sites
        WHERE TRIM(level1) != '' AND TRIM(level2) != ''
        UNION
        SELECT DISTINCT level1, level2 FROM articles
        WHERE TRIM(level1) != '' AND TRIM(level2) != ''
        ORDER BY level1 ASC, level2 ASC
        """
    ).fetchall()

    for row in rows:
        level1 = (row["level1"] or "").strip()
        level2 = (row["level2"] or "").strip()
        if not level1 or not level2:
            continue

        if level1 not in level1_map:
            parent_cursor = cursor.execute(
                """
                INSERT INTO categories (name, parentId, sortOrder, createdAt, updatedAt)
                VALUES (?, NULL, 0, ?, ?)
                """,
                (level1, timestamp, timestamp),
            )
            level1_map[level1] = parent_cursor.lastrowid

        cursor.execute(
            """
            INSERT OR IGNORE INTO categories (name, parentId, sortOrder, createdAt, updatedAt)
            VALUES (?, ?, 0, ?, ?)
            """,
            (level2, level1_map[level1], timestamp, timestamp),
        )
