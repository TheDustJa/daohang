from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from contextlib import closing
from typing import Any, Literal

from fastapi import HTTPException

from .database import get_db
from .schemas import (
    AdminCategoryCreate,
    AdminCategoryNode,
    AdminCategoryOut,
    AdminCategoryUpdate,
    FriendLinkCreate,
    FriendLinkOut,
    FriendLinkUpdate,
    Level1CategoryOut,
    Level2CategoryOut,
    SiteBase,
    SiteCreate,
    SiteOut,
)
from .utils import now_iso
from .utils import password_hash

ContentType = Literal["site", "article"]

SITE_SELECT = """
SELECT
    id,
    name,
    url,
    logo,
    description,
    level1,
    level2,
    level3,
    tags,
    isRecommended,
    sortOrder,
    'site' AS type,
    '' AS content,
    'text' AS contentFormat,
    status,
    createdAt,
    updatedAt
FROM sites
"""

ARTICLE_SELECT = """
SELECT
    id,
    name,
    url,
    logo,
    description,
    level1,
    level2,
    level3,
    tags,
    isRecommended,
    sortOrder,
    'article' AS type,
    content,
    contentFormat,
    status,
    createdAt,
    updatedAt
FROM articles
"""


def row_to_site(row: sqlite3.Row) -> SiteOut:
    payload = dict(row)
    payload["tags"] = json.loads(payload.get("tags") or "[]")
    return SiteOut.model_validate(payload)


def row_to_friend_link(row: sqlite3.Row) -> FriendLinkOut:
    return FriendLinkOut.model_validate(dict(row))


def row_to_category(row: sqlite3.Row) -> AdminCategoryOut:
    return AdminCategoryOut.model_validate(dict(row))


def normalize_category_values(level1: str, level2: str) -> tuple[str, str]:
    level1_value = level1.strip()
    level2_value = level2.strip()
    if not level1_value or not level2_value:
        raise HTTPException(status_code=422, detail="Level 1 and level 2 categories are required")
    return level1_value, level2_value


def ensure_category_path(conn: sqlite3.Connection, level1: str, level2: str, sort_order: int = 0) -> None:
    level1_value, level2_value = normalize_category_values(level1, level2)
    timestamp = now_iso()

    level1_row = conn.execute(
        "SELECT id FROM categories WHERE name = ? AND parentId IS NULL",
        (level1_value,),
    ).fetchone()
    if level1_row is None:
        cursor = conn.execute(
            """
            INSERT INTO categories (name, parentId, sortOrder, createdAt, updatedAt)
            VALUES (?, NULL, ?, ?, ?)
            """,
            (level1_value, sort_order, timestamp, timestamp),
        )
        level1_id = cursor.lastrowid
    else:
        level1_id = level1_row["id"]

    level2_row = conn.execute(
        "SELECT id FROM categories WHERE name = ? AND parentId = ?",
        (level2_value, level1_id),
    ).fetchone()
    if level2_row is None:
        conn.execute(
            """
            INSERT INTO categories (name, parentId, sortOrder, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?)
            """,
            (level2_value, level1_id, sort_order, timestamp, timestamp),
        )


def build_union_query(status_filter: str | None) -> tuple[str, list[Any]]:
    site_query = SITE_SELECT
    article_query = ARTICLE_SELECT
    params: list[Any] = []

    if status_filter:
        site_query += " WHERE status = ?"
        article_query += " WHERE status = ?"
        params.extend([status_filter, status_filter])

    query = f"""
    SELECT * FROM (
        {site_query}
        UNION ALL
        {article_query}
    ) AS contents
    ORDER BY sortOrder DESC, isRecommended DESC, id DESC
    """
    return query, params


def list_sites(status_filter: str | None) -> list[SiteOut]:
    query, params = build_union_query(status_filter)
    with closing(get_db()) as conn:
        rows = conn.execute(query, params).fetchall()
    return [row_to_site(row) for row in rows]


def build_navigation_categories(sites: list[SiteOut]) -> list[Level1CategoryOut]:
    category_rows = list_categories()
    roots = [item for item in category_rows if item.parentId is None]
    children_by_parent: dict[int, list[AdminCategoryOut]] = defaultdict(list)

    for item in category_rows:
        if item.parentId is not None:
            children_by_parent[item.parentId].append(item)

    roots.sort(key=lambda item: (-item.sortOrder, item.name, item.id))
    for items in children_by_parent.values():
        items.sort(key=lambda item: (-item.sortOrder, item.name, item.id))

    grouped: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    totals: dict[str, int] = defaultdict(int)
    for site in sites:
        level1 = site.level1.strip()
        level2 = site.level2.strip()
        if not level1 or not level2:
            continue
        grouped[level1][level2] += 1
        totals[level1] += 1

    result: list[Level1CategoryOut] = []
    for root in roots:
        total_for_root = totals.get(root.name, 0)
        if total_for_root <= 0:
            continue

        ordered_children: list[Level2CategoryOut] = []
        for child in children_by_parent.get(root.id, []):
            total = grouped[root.name].pop(child.name, 0)
            if total > 0:
                ordered_children.append(Level2CategoryOut(name=child.name, total=total))

        extra_children = sorted(grouped[root.name].items(), key=lambda item: (-item[1], item[0]))
        ordered_children.extend(Level2CategoryOut(name=name, total=total) for name, total in extra_children)

        if ordered_children:
            result.append(Level1CategoryOut(name=root.name, total=total_for_root, children=ordered_children))

    existing_names = {item.name for item in category_rows if item.parentId is None}
    remaining_level1 = [(name, total) for name, total in totals.items() if name not in existing_names and total > 0]
    for level1, total in sorted(remaining_level1, key=lambda item: (-item[1], item[0])):
        sorted_children = sorted(grouped[level1].items(), key=lambda item: (-item[1], item[0]))
        if not sorted_children:
            continue
        result.append(
            Level1CategoryOut(
                name=level1,
                total=total,
                children=[Level2CategoryOut(name=name, total=count) for name, count in sorted_children],
            )
        )

    return result


def get_category_options(status_filter: str | None = "approved") -> dict[str, Any]:
    del status_filter
    categories = list_categories()
    level1_items = [item for item in categories if item.parentId is None]
    children_by_parent: dict[int, list[AdminCategoryOut]] = defaultdict(list)
    for item in categories:
        if item.parentId is not None:
            children_by_parent[item.parentId].append(item)

    level1_items.sort(key=lambda item: (-item.sortOrder, item.name, item.id))
    for items in children_by_parent.values():
        items.sort(key=lambda item: (-item.sortOrder, item.name, item.id))

    level1_options = [item.name for item in level1_items]
    level2_by_level1 = {item.name: [child.name for child in children_by_parent.get(item.id, [])] for item in level1_items}
    level2_options = sorted({child.name for items in children_by_parent.values() for child in items})
    return {
        "level1Options": level1_options,
        "level2Options": level2_options,
        "level2ByLevel1": level2_by_level1,
    }


def list_categories() -> list[AdminCategoryOut]:
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT id, name, parentId, sortOrder, createdAt, updatedAt FROM categories ORDER BY sortOrder DESC, name ASC, id ASC"
        ).fetchall()
    return [row_to_category(row) for row in rows]


def get_category_by_id(category_id: int) -> AdminCategoryOut | None:
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT id, name, parentId, sortOrder, createdAt, updatedAt FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
    return row_to_category(row) if row else None


def build_admin_category_tree() -> list[AdminCategoryNode]:
    categories = list_categories()
    sites = list_sites(None)
    level1_totals: dict[str, int] = defaultdict(int)
    level2_totals: dict[tuple[str, str], int] = defaultdict(int)

    for site in sites:
        level1 = site.level1.strip()
        level2 = site.level2.strip()
        if level1 and level2:
            level1_totals[level1] += 1
            level2_totals[(level1, level2)] += 1

    children_by_parent: dict[int, list[AdminCategoryOut]] = defaultdict(list)
    roots: list[AdminCategoryOut] = []
    for item in categories:
        if item.parentId is None:
            roots.append(item)
        else:
            children_by_parent[item.parentId].append(item)

    roots.sort(key=lambda item: (-item.sortOrder, item.name, item.id))
    for items in children_by_parent.values():
        items.sort(key=lambda item: (-item.sortOrder, item.name, item.id))

    result: list[AdminCategoryNode] = []
    for root in roots:
        child_nodes = [
            AdminCategoryNode(
                id=child.id,
                name=child.name,
                total=level2_totals[(root.name, child.name)],
                sortOrder=child.sortOrder,
                parentId=child.parentId,
            )
            for child in children_by_parent.get(root.id, [])
        ]
        result.append(
            AdminCategoryNode(
                id=root.id,
                name=root.name,
                total=level1_totals[root.name],
                sortOrder=root.sortOrder,
                parentId=None,
                children=child_nodes,
            )
        )
    return result


def create_category(payload: AdminCategoryCreate) -> AdminCategoryOut:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Category name is required")

    parent_id = payload.parentId
    timestamp = now_iso()

    with closing(get_db()) as conn:
        if parent_id is not None:
            parent = conn.execute(
                "SELECT id, name, parentId FROM categories WHERE id = ?",
                (parent_id,),
            ).fetchone()
            if parent is None:
                raise HTTPException(status_code=404, detail="Parent category not found")
            if parent["parentId"] is not None:
                raise HTTPException(status_code=400, detail="Only two category levels are supported")

        exists = conn.execute(
            "SELECT id FROM categories WHERE name = ? AND parentId IS ?",
            (name, parent_id),
        ).fetchone()
        if exists is not None:
            raise HTTPException(status_code=409, detail="Category already exists")

        cursor = conn.execute(
            """
            INSERT INTO categories (name, parentId, sortOrder, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, parent_id, payload.sortOrder, timestamp, timestamp),
        )
        category_id = cursor.lastrowid
        conn.commit()

    category = get_category_by_id(category_id)
    assert category is not None
    return category


def update_category(category_id: int, payload: AdminCategoryUpdate) -> AdminCategoryOut:
    existing = get_category_by_id(category_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Category not found")

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Category name is required")

    parent_id = payload.parentId
    if existing.parentId is None and parent_id is not None:
        raise HTTPException(status_code=400, detail="Level 1 category cannot be moved under another category")
    if existing.parentId is not None and parent_id is None:
        raise HTTPException(status_code=400, detail="Level 2 category must keep a parent category")
    if existing.parentId != parent_id:
        raise HTTPException(status_code=400, detail="Changing category hierarchy is not supported")

    now_value = now_iso()
    with closing(get_db()) as conn:
        duplicate = conn.execute(
            "SELECT id FROM categories WHERE name = ? AND parentId IS ? AND id != ?",
            (name, parent_id, category_id),
        ).fetchone()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Category already exists")

        conn.execute(
            """
            UPDATE categories
            SET name = ?, sortOrder = ?, updatedAt = ?
            WHERE id = ?
            """,
            (name, payload.sortOrder, now_value, category_id),
        )

        if existing.name != name:
            if existing.parentId is None:
                conn.execute("UPDATE sites SET level1 = ?, updatedAt = ? WHERE level1 = ?", (name, now_value, existing.name))
                conn.execute("UPDATE articles SET level1 = ?, updatedAt = ? WHERE level1 = ?", (name, now_value, existing.name))
            else:
                parent = get_category_by_id(existing.parentId)
                assert parent is not None
                conn.execute(
                    "UPDATE sites SET level2 = ?, updatedAt = ? WHERE level1 = ? AND level2 = ?",
                    (name, now_value, parent.name, existing.name),
                )
                conn.execute(
                    "UPDATE articles SET level2 = ?, updatedAt = ? WHERE level1 = ? AND level2 = ?",
                    (name, now_value, parent.name, existing.name),
                )

        conn.commit()

    category = get_category_by_id(category_id)
    assert category is not None
    return category


def delete_category(category_id: int, delete_related_content: bool = False) -> None:
    existing = get_category_by_id(category_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Category not found")

    now_value = now_iso()
    with closing(get_db()) as conn:
        if existing.parentId is None:
            child_rows = conn.execute("SELECT id FROM categories WHERE parentId = ?", (category_id,)).fetchall()
            conn.execute("UPDATE sites SET level1 = '', level2 = '', updatedAt = ? WHERE level1 = ?", (now_value, existing.name))
            conn.execute("UPDATE articles SET level1 = '', level2 = '', updatedAt = ? WHERE level1 = ?", (now_value, existing.name))
            if child_rows:
                conn.execute("DELETE FROM categories WHERE parentId = ?", (category_id,))
        else:
            parent = get_category_by_id(existing.parentId)
            assert parent is not None
            if delete_related_content:
                conn.execute("DELETE FROM sites WHERE level1 = ? AND level2 = ?", (parent.name, existing.name))
                conn.execute("DELETE FROM articles WHERE level1 = ? AND level2 = ?", (parent.name, existing.name))
            else:
                conn.execute(
                    "UPDATE sites SET level2 = '', updatedAt = ? WHERE level1 = ? AND level2 = ?",
                    (now_value, parent.name, existing.name),
                )
                conn.execute(
                    "UPDATE articles SET level2 = '', updatedAt = ? WHERE level1 = ? AND level2 = ?",
                    (now_value, parent.name, existing.name),
                )

        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()


def get_site_by_id(site_id: int, content_type: ContentType, allow_pending: bool = False) -> SiteOut | None:
    table_name = "sites" if content_type == "site" else "articles"
    query = f"SELECT * FROM {table_name} WHERE id = ?"
    params: list[Any] = [site_id]
    if not allow_pending:
        query += " AND status = 'approved'"
    with closing(get_db()) as conn:
        row = conn.execute(query, params).fetchone()
    if row is None:
        return None

    payload = dict(row)
    payload["type"] = content_type
    payload["tags"] = json.loads(payload.get("tags") or "[]")
    if content_type == "site":
        payload["content"] = ""
        payload["contentFormat"] = "text"
    return SiteOut.model_validate(payload)


def create_site(payload: SiteBase, status_value: str, submitter_email: str | None = None) -> SiteOut:
    level1_value, level2_value = normalize_category_values(payload.level1, payload.level2)
    timestamp = now_iso()
    with closing(get_db()) as conn:
        ensure_category_path(conn, level1_value, level2_value)
        if payload.type == "article":
            cursor = conn.execute(
                """
                INSERT INTO articles (
                    name, url, logo, description, level1, level2, level3, tags,
                    isRecommended, sortOrder, content, contentFormat, status,
                    submitterEmail, createdAt, updatedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.name,
                    payload.url,
                    payload.logo or payload.name[:1],
                    payload.description,
                    level1_value,
                    level2_value,
                    payload.level3,
                    json.dumps(payload.tags, ensure_ascii=False),
                    1 if payload.isRecommended else 0,
                    payload.sortOrder,
                    payload.content,
                    payload.contentFormat,
                    status_value,
                    submitter_email,
                    timestamp,
                    timestamp,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO sites (
                    name, url, logo, description, level1, level2, level3, tags,
                    isRecommended, sortOrder, type, content, status, submitterEmail,
                    createdAt, updatedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'site', '', ?, ?, ?, ?)
                """,
                (
                    payload.name,
                    payload.url,
                    payload.logo or payload.name[:1],
                    payload.description,
                    level1_value,
                    level2_value,
                    payload.level3,
                    json.dumps(payload.tags, ensure_ascii=False),
                    1 if payload.isRecommended else 0,
                    payload.sortOrder,
                    status_value,
                    submitter_email,
                    timestamp,
                    timestamp,
                ),
            )
        site_id = cursor.lastrowid
        conn.commit()
    site = get_site_by_id(site_id, payload.type, allow_pending=True)
    assert site is not None
    return site


def update_site(site_id: int, payload: SiteCreate) -> SiteOut:
    existing = get_site_by_id(site_id, payload.type, allow_pending=True)
    if existing is None:
        raise HTTPException(status_code=404, detail="Content not found")

    level1_value, level2_value = normalize_category_values(payload.level1, payload.level2)
    status_value = payload.status or existing.status
    now_value = now_iso()
    with closing(get_db()) as conn:
        ensure_category_path(conn, level1_value, level2_value)
        if payload.type == "article":
            conn.execute(
                """
                UPDATE articles
                SET name = ?, url = ?, logo = ?, description = ?, level1 = ?, level2 = ?, level3 = ?,
                    tags = ?, isRecommended = ?, sortOrder = ?, content = ?, contentFormat = ?, status = ?, updatedAt = ?
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.url,
                    payload.logo or payload.name[:1],
                    payload.description,
                    level1_value,
                    level2_value,
                    payload.level3,
                    json.dumps(payload.tags, ensure_ascii=False),
                    1 if payload.isRecommended else 0,
                    payload.sortOrder,
                    payload.content,
                    payload.contentFormat,
                    status_value,
                    now_value,
                    site_id,
                ),
            )
        else:
            conn.execute(
                """
                UPDATE sites
                SET name = ?, url = ?, logo = ?, description = ?, level1 = ?, level2 = ?, level3 = ?,
                    tags = ?, isRecommended = ?, sortOrder = ?, status = ?, updatedAt = ?
                WHERE id = ?
                """,
                (
                    payload.name,
                    payload.url,
                    payload.logo or payload.name[:1],
                    payload.description,
                    level1_value,
                    level2_value,
                    payload.level3,
                    json.dumps(payload.tags, ensure_ascii=False),
                    1 if payload.isRecommended else 0,
                    payload.sortOrder,
                    status_value,
                    now_value,
                    site_id,
                ),
            )
        conn.commit()
    site = get_site_by_id(site_id, payload.type, allow_pending=True)
    assert site is not None
    return site


def delete_site(site_id: int, content_type: ContentType) -> None:
    table_name = "sites" if content_type == "site" else "articles"
    with closing(get_db()) as conn:
        row = conn.execute(f"SELECT id FROM {table_name} WHERE id = ?", (site_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Content not found")
        conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (site_id,))
        conn.commit()


def clear_uncategorized_sites() -> int:
    with closing(get_db()) as conn:
        site_count = conn.execute(
            "SELECT COUNT(*) FROM sites WHERE TRIM(level1) = '' OR TRIM(level2) = ''"
        ).fetchone()[0]
        article_count = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE TRIM(level1) = '' OR TRIM(level2) = ''"
        ).fetchone()[0]
        conn.execute("DELETE FROM sites WHERE TRIM(level1) = '' OR TRIM(level2) = ''")
        conn.execute("DELETE FROM articles WHERE TRIM(level1) = '' OR TRIM(level2) = ''")
        conn.commit()
    return site_count + article_count


def create_friend_link(payload: FriendLinkCreate) -> FriendLinkOut:
    timestamp = now_iso()
    with closing(get_db()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO friend_links (siteName, siteUrl, siteDesc, contactEmail, status, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, 'pending', ?, ?)
            """,
            (payload.siteName, payload.siteUrl, payload.siteDesc, payload.contactEmail, timestamp, timestamp),
        )
        friend_link_id = cursor.lastrowid
        conn.commit()
        row = conn.execute("SELECT * FROM friend_links WHERE id = ?", (friend_link_id,)).fetchone()
    assert row is not None
    return row_to_friend_link(row)


def list_friend_links(status_filter: str | None = None) -> list[FriendLinkOut]:
    with closing(get_db()) as conn:
        if status_filter:
            rows = conn.execute(
                "SELECT * FROM friend_links WHERE status = ? ORDER BY id DESC",
                (status_filter,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM friend_links ORDER BY id DESC").fetchall()
    return [row_to_friend_link(row) for row in rows]


def update_friend_link(friend_link_id: int, payload: FriendLinkUpdate) -> FriendLinkOut:
    now_value = now_iso()
    with closing(get_db()) as conn:
        existing = conn.execute("SELECT * FROM friend_links WHERE id = ?", (friend_link_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Friend link not found")
        conn.execute(
            "UPDATE friend_links SET status = ?, updatedAt = ? WHERE id = ?",
            (payload.status, now_value, friend_link_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM friend_links WHERE id = ?", (friend_link_id,)).fetchone()
    assert row is not None
    return row_to_friend_link(row)


def delete_friend_link(friend_link_id: int) -> None:
    with closing(get_db()) as conn:
        existing = conn.execute("SELECT id FROM friend_links WHERE id = ?", (friend_link_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Friend link not found")
        conn.execute("DELETE FROM friend_links WHERE id = ?", (friend_link_id,))
        conn.commit()


def get_admin_by_username(username: str) -> dict[str, Any] | None:
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT id, username, passwordHash, createdAt FROM admins WHERE username = ?",
            (username,),
        ).fetchone()
    return dict(row) if row else None


def update_admin_password(username: str, old_password: str, new_password: str) -> None:
    admin = get_admin_by_username(username)
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    if admin["passwordHash"] != password_hash(old_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if old_password == new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")

    with closing(get_db()) as conn:
        conn.execute(
            "UPDATE admins SET passwordHash = ? WHERE username = ?",
            (password_hash(new_password), username),
        )
        conn.commit()
