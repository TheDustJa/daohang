from __future__ import annotations

import argparse
import sqlite3

from app.config import DB_PATH
from app.importer import ensure_database_ready, import_sites, resolve_import_source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import site data into pybackground SQLite database.")
    parser.add_argument("--source", help="Path to a JSON file to import.")
    parser.add_argument("--level1", default="AI工具", help="Fallback level1 category when source data does not provide one.")
    parser.add_argument(
        "--status",
        default="approved",
        choices=["draft", "approved", "pending"],
        help="Default status for imported records.",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Insert records even when the same name/url/level1/level2 combination already exists.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ensure_database_ready()
    source, sites = resolve_import_source(args.source, default_level1=args.level1)

    conn = sqlite3.connect(DB_PATH)
    try:
        inserted, skipped = import_sites(
            conn,
            sites,
            default_status=args.status,
            skip_existing=not args.allow_duplicates,
        )
        conn.commit()
    finally:
        conn.close()

    print(f"Source: {source}")
    print(f"Loaded: {len(sites)}")
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    print(f"Database: {DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
