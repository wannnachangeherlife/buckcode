# -*- coding: utf-8 -*-
"""Batch initialize Notion review cards.

Usage (PowerShell):
  $env:NOTION_TOKEN = "secret_xxx"
  python automation/workflows/init_review_cards.py \
    --config automation/utils/notion_migration_config.json \
    --file data/review_seed.txt --dry-run

File formats supported:
- Plain text: one title per line
- CSV: column header `title` or `卡片标题`
- JSON: array of strings OR object {"标题1": {}, "标题2": {}} keys used as titles

Creates pages in the review database with initial properties:
  阶段 Stage = 0
  Ease = default_ease (from config, fallback 2.5)
  Interval = 0
  状态 = 新建
  上次复习日期 / 下次复习日期 left empty
Optionally add tags via --tags "三维,点云" (auto create multi_select values).

Use --limit to restrict creations, --dry-run to preview payloads.
"""
from __future__ import annotations
import os, sys, json, csv
from pathlib import Path
from typing import Any, Dict, List
import argparse
import requests

# Ensure root on path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(_ROOT.parent))

# Auto-load .env if critical vars missing (support NOTION_TOKEN/NOTION_API_KEY)
if not ((os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")) and os.getenv("NOTION_REVIEW_DB_ID")):
    env_path = Path(".env")
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=str(env_path))
        except Exception:
            pass

NOTION_VERSION = "2022-06-28"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Batch create initial review cards")
    p.add_argument("--config", required=True, help="Path to config json containing review_db_id")
    p.add_argument("--file", required=True, help="Seed file (txt/csv/json)")
    p.add_argument("--tags", help="Comma separated tags to apply to all cards")
    p.add_argument("--limit", type=int, help="Max number of cards to create")
    p.add_argument("--dry-run", action="store_true", help="Show payloads only")
    return p.parse_args(argv)


def load_config(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def fetch_db_schema(token: str, db_id: str) -> Dict[str, Any]:
    r = requests.get(f"https://api.notion.com/v1/databases/{db_id}", headers=headers(token), timeout=40)
    if r.status_code != 200:
        raise RuntimeError(f"fetch database schema failed status={r.status_code} body={r.text[:200]}")
    return r.json()


def find_title_property_name(db_json: Dict[str, Any]) -> str:
    props = db_json.get("properties", {})
    for name, meta in props.items():
        if isinstance(meta, dict) and meta.get("type") == "title":
            return name
    return "Name"


def ensure_db_properties(token: str, db_id: str) -> Dict[str, str]:
    db = fetch_db_schema(token, db_id)
    props = db.get("properties", {})
    title_name = find_title_property_name(db)
    mapping = {
        "title": title_name,
        "stage": "阶段 Stage",
        "ease": "Ease",
        "interval": "Interval",
        "status": "状态",
        "last_date": "上次复习日期",
        "next_date": "下次复习日期",
        "tags": "标签",
    }
    to_add: Dict[str, Any] = {}
    def missing(name: str) -> bool:
        return name not in props

    if missing(mapping["stage"]):
        to_add[mapping["stage"]] = {"number": {}}
    if missing(mapping["ease"]):
        to_add[mapping["ease"]] = {"number": {}}
    if missing(mapping["interval"]):
        to_add[mapping["interval"]] = {"number": {}}
    if missing(mapping["status"]):
        to_add[mapping["status"]] = {"select": {"options": [
            {"name": "新建"}, {"name": "复习"}, {"name": "重置"}, {"name": "完成"}
        ]}}
    if missing(mapping["last_date"]):
        to_add[mapping["last_date"]] = {"date": {}}
    if missing(mapping["next_date"]):
        to_add[mapping["next_date"]] = {"date": {}}
    if missing(mapping["tags"]):
        to_add[mapping["tags"]] = {"multi_select": {"options": []}}

    if to_add:
        payload = {"properties": to_add}
        r = requests.patch(f"https://api.notion.com/v1/databases/{db_id}", headers=headers(token), json=payload, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"update database props failed status={r.status_code} body={r.text[:240]}")
    return mapping


def read_titles(path: str) -> List[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    titles: List[str] = []
    if p.suffix.lower() == ".txt":
        for line in p.read_text(encoding="utf-8").splitlines():
            t = line.strip()
            if t:
                titles.append(t)
    elif p.suffix.lower() == ".csv":
        with p.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                t = (row.get("title") or row.get("卡片标题") or "").strip()
                if t:
                    titles.append(t)
    elif p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for v in data:
                if isinstance(v, str) and v.strip():
                    titles.append(v.strip())
        elif isinstance(data, dict):
            for k in data.keys():
                if k.strip():
                    titles.append(k.strip())
        else:
            raise ValueError("Unsupported JSON structure")
    else:
        raise ValueError("Unsupported file type. Use txt/csv/json")
    # Deduplicate preserving order
    seen = set()
    uniq: List[str] = []
    for t in titles:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def build_properties(title: str, ease: float, tags: List[str], mapping: Dict[str, str]) -> Dict[str, Any]:
    props: Dict[str, Any] = {
        mapping["title"]: {"title": [{"text": {"content": title}}]},
        mapping["stage"]: {"number": 0},
        mapping["ease"]: {"number": ease},
        mapping["interval"]: {"number": 0},
        mapping["status"]: {"select": {"name": "新建"}},
    }
    if tags:
        props[mapping["tags"]] = {"multi_select": [{"name": t} for t in tags]}
    return props


def create_page(token: str, db_id: str, properties: Dict[str, Any], dry_run: bool) -> bool:
    payload = {"parent": {"database_id": db_id}, "properties": properties}
    if dry_run:
        print(json.dumps({"CREATE_PREVIEW": payload}, ensure_ascii=False))
        return True
    r = requests.post("https://api.notion.com/v1/pages", headers=headers(token), json=payload, timeout=40)
    if r.status_code == 200:
        return True
    print(f"[WARN] create failed status={r.status_code} body={r.text[:200]}")
    return False


def main(argv=None):
    args = parse_args(argv)
    cfg = load_config(args.config)
    cfg_db = (cfg.get("review_db_id") or "").strip()
    if (not cfg_db) or cfg_db.upper().startswith("REPLACE"):
        review_db = (os.getenv("NOTION_REVIEW_DB_ID") or "").strip()
    else:
        review_db = cfg_db
    if not review_db:
        print("[ERROR] review_db_id missing (set in config or NOTION_REVIEW_DB_ID)")
        return 1
    token = os.getenv("NOTION_TOKEN", "") or os.getenv("NOTION_API_KEY", "")
    if not token:
        print("[ERROR] NOTION_TOKEN/NOTION_API_KEY missing; set env or .env file")
        return 1
    titles = read_titles(args.file)
    if not titles:
        print("[INFO] no titles found in seed file")
        return 0
    if args.limit:
        titles = titles[: args.limit]
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    ease_default = float(cfg.get("default_ease", 2.5))
    # Ensure DB properties exist, get actual names
    mapping = ensure_db_properties(token, review_db)
    created = 0
    for t in titles:
        props = build_properties(t, ease_default, tags, mapping)
        ok = create_page(token, review_db, props, args.dry_run)
        if ok:
            created += 1
    print(f"[DONE] attempted={len(titles)} created={created} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
