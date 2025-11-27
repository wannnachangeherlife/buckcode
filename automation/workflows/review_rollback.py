# -*- coding: utf-8 -*-
"""Rollback previously saved review card properties from a backup JSON.

Backup file format (created by --backup in review_scheduler):
[
  {"id": "<page-id>", "properties": { ... original properties ... }},
  ...
]

Usage:
$env:NOTION_TOKEN="secret_xxx"
python automation/workflows/review_rollback.py --backup automation/analytics/review_backup_2025-11-27.json --dry-run
python automation/workflows/review_rollback.py --backup automation/analytics/review_backup_2025-11-27.json
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
import requests

NOTION_VERSION = "2022-06-28"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Rollback review card properties")
    p.add_argument("--backup", required=True, help="Path to backup JSON file")
    p.add_argument("--dry-run", action="store_true", help="Show patches only")
    return p.parse_args(argv)


def headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def main(argv=None):
    args = parse_args(argv)
    token = os.getenv("NOTION_TOKEN", "") or os.getenv("NOTION_API_KEY", "")
    if not token:
        print("[WARN] NOTION_TOKEN/NOTION_API_KEY empty")
    path = Path(args.backup)
    if not path.exists():
        print(f"[ERROR] backup file not found: {path}")
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    restored = 0
    for entry in data:
        page_id = entry.get("id")
        props = entry.get("properties", {})
        if not page_id or not isinstance(props, dict):
            continue
        if args.dry_run:
            print(json.dumps({"id": page_id, "restore": True}, ensure_ascii=False))
            restored += 1
            continue
        r = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers(token), json={"properties": props}, timeout=30)
        if r.status_code == 200:
            restored += 1
        else:
            print(f"[WARN] rollback failed id={page_id} status={r.status_code} body={r.text[:160]}")
    print(f"[DONE] restored={restored} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
