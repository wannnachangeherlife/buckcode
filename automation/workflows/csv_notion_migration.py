# -*- coding: utf-8 -*-
"""CSV → Notion migration workflow (skeleton).
Run with: python automation/workflows/csv_notion_migration.py --config automation/utils/notion_migration_config.json --source path --only knowledge --dry-run
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import requests

from automation.utils.migration_mapping import get_mapping
from automation.utils.normalization import (
    parse_date,
    normalize_priority,
    normalize_status,
    split_multi,
    coerce_number,
    build_title,
    build_rich,
)
from automation.utils.relation_resolver import build_relation_resolver

NOTION_VERSION = "2022-06-28"

class MigrationContext:
    def __init__(self, config: Dict[str, Any], dry_run: bool, resume: bool):
        self.config = config
        self.dry_run = dry_run
        self.resume = resume
        self.token = os.getenv("NOTION_TOKEN", "")
        if not self.token:
            print("[WARN] NOTION_TOKEN environment variable is empty.")
        self.id_map_path = Path(config["id_map_file"]) if config.get("id_map_file") else Path("automation/utils/notion_id_map.json")
        self.id_map: Dict[str, Dict[str, str]] = self._load_id_map()
        self.relation_cache_path = config.get("cache_file", "automation/utils/notion_relation_cache.json")
        self.relation_resolver = build_relation_resolver(self.token, self.relation_cache_path)
        self.batch_size = config.get("batch_size", 6)

    def _load_id_map(self) -> Dict[str, Dict[str, str]]:
        if self.id_map_path.exists():
            try:
                return json.loads(self.id_map_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def save_id_map(self):
        tmp = self.id_map_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.id_map, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.id_map_path)
        self.relation_resolver.save()

    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }


class BaseImporter:
    KIND = "base"

    def __init__(self, ctx: MigrationContext, db_id_key: str, mapping_key: str):
        self.ctx = ctx
        self.db_id = ctx.config.get(db_id_key)
        if not self.db_id:
            raise ValueError(f"Missing database id for {db_id_key}")
        self.mapping = get_mapping(mapping_key)
        self.kind = mapping_key

    def unique_key(self, row: Dict[str, str]) -> str:
        seed = row.get(next(iter(row)), "") + "|" + self.kind
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

    def already_imported(self, key: str) -> bool:
        return key in self.ctx.id_map.get(self.kind, {}) if self.ctx.resume else False

    def load_csv(self, path: Path) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        with path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append({k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in r.items()})
        return rows

    def transform_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        props: Dict[str, Any] = {}
        for src, (target, ptype) in self.mapping.items():
            raw = row.get(src, "")
            if ptype == "title":
                props[target] = build_title(raw)
            elif ptype == "rich_text":
                props[target] = build_rich(raw)
            elif ptype == "date":
                iso = parse_date(raw)
                if iso:
                    props[target] = {"date": {"start": iso}}
            elif ptype == "select":
                if raw:
                    props[target] = {"select": {"name": raw}}
            elif ptype == "multi_select":
                vals = split_multi(raw)
                if vals:
                    props[target] = {"multi_select": [{"name": v} for v in vals]}
            elif ptype == "number":
                num = coerce_number(raw)
                if num is not None:
                    props[target] = {"number": num}
            elif ptype == "url":
                if raw:
                    props[target] = {"url": raw}
            elif ptype == "relation":
                # relation expects a page id; fallback skip if not resolvable
                if raw:
                    title_guess = self._extract_title_from_relation(raw)
                    rel_id = self.ctx.relation_resolver.ensure(title_guess, self.ctx.config.get("knowledge_db_id"))
                    if rel_id:
                        props[target] = {"relation": [{"id": rel_id}]}
        return props

    def _extract_title_from_relation(self, raw: str) -> str:
        # Attempt decode URL component then split last path-like segment
        from urllib.parse import unquote
        decoded = unquote(raw)
        # Remove extension .csv or .md if present
        return decoded.rsplit(" ", 1)[0].split("/")[-1].replace(".csv", "").replace(".md", "")

    def build_payload(self, props: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "parent": {"database_id": self.db_id},
            "properties": props,
        }

    def create_page(self, payload: Dict[str, Any]) -> str:
        if self.ctx.dry_run:
            print(json.dumps(payload, ensure_ascii=False)[:400] + "... [dry-run]")
            return "dry-run-id"
        r = requests.post("https://api.notion.com/v1/pages", headers=self.ctx.headers(), json=payload, timeout=30)
        if r.status_code == 200:
            return r.json().get("id", "")
        print(f"[ERROR] create_page status={r.status_code} body={r.text[:300]}")
        return ""

    def run_files(self, files: List[Path], limit: int = None):
        imported = 0
        for file in files:
            rows = self.load_csv(file)
            for row in rows:
                ukey = self.unique_key(row)
                if self.already_imported(ukey):
                    continue
                props = self.transform_row(row)
                if not props:
                    continue
                page_id = self.create_page(self.build_payload(props))
                if page_id:
                    self.ctx.id_map.setdefault(self.kind, {})[ukey] = page_id
                imported += 1
                if limit and imported >= limit:
                    break
            if limit and imported >= limit:
                break
            # Batch flush
            if imported % self.ctx.batch_size == 0:
                self.ctx.save_id_map()
        self.ctx.save_id_map()

class KnowledgeImporter(BaseImporter):
    KIND = "knowledge"

class TaskImporter(BaseImporter):
    KIND = "tasks"

class ResourceImporter(BaseImporter):
    KIND = "resources"

IMPORTER_CLASSES = {
    "knowledge": KnowledgeImporter,
    "tasks": TaskImporter,
    "resources": ResourceImporter,
}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="CSV → Notion migration")
    p.add_argument("--config", required=True, help="Path to config json")
    p.add_argument("--source", required=True, help="Path to source directory")
    p.add_argument("--only", help="Comma list: knowledge,tasks,resources")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--limit", type=int, help="Limit total imported rows")
    p.add_argument("--fail-fast", action="store_true", help="Stop on first error")
    p.add_argument("--seed-review", action="store_true", help="Create initial review cards after knowledge import")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    ctx = MigrationContext(config=config, dry_run=args.dry_run, resume=args.resume)
    kinds = [k.strip() for k in args.only.split(",")] if args.only else list(IMPORTER_CLASSES.keys())
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"[ERROR] source path not found: {source_path}")
        return 1
    errors = 0
    for kind in kinds:
        imp_cls = IMPORTER_CLASSES.get(kind)
        if not imp_cls:
            print(f"[WARN] unsupported kind: {kind}")
            continue
        importer = imp_cls(ctx, f"{kind}_db_id", kind)
        pattern = "*all.csv" if kind in ("knowledge", "tasks", "resources") else "*.csv"
        files = list(source_path.rglob(pattern))
        print(f"[INFO] kind={kind} files={len(files)} dry_run={ctx.dry_run}")
        try:
            importer.run_files(files, limit=args.limit)
        except Exception as e:
            errors += 1
            print(f"[ERROR] kind={kind} unexpected exception: {e}")
            if args.fail_fast:
                break
    if args.seed_review and "knowledge" in kinds:
        seed_review_cards(ctx)
    print(f"[DONE] migration finished errors={errors}")
    return 0


def seed_review_cards(ctx: MigrationContext):
    """Create initial review cards (Stage 0) for each imported knowledge page if review db provided."""
    review_db = ctx.config.get("review_db_id")
    if not review_db:
        print("[INFO] seed_review skipped: missing review_db_id")
        return
    knowledge_entries = ctx.id_map.get("knowledge", {})
    print(f"[INFO] Seeding review cards for {len(knowledge_entries)} knowledge items")
    today = time.strftime("%Y-%m-%d")
    for ukey, page_id in knowledge_entries.items():
        props = {
            "卡片标题": {"title": [{"text": {"content": ukey}}]},
            "关联知识点": {"relation": [{"id": page_id}]},
            "阶段 Stage": {"number": 0},
            "Ease": {"number": ctx.config.get("default_ease", 2.5)},
            "Interval": {"number": ctx.config.get("default_initial_interval_days", 1)},
            "上次复习日期": {"date": {"start": today}},
            "下次复习日期": {"date": {"start": today}},
            "状态": {"select": {"name": "新建"}},
        }
        payload = {"parent": {"database_id": review_db}, "properties": props}
        if ctx.dry_run:
            print(json.dumps(payload, ensure_ascii=False)[:200] + "... [dry-run review]")
            continue
        r = requests.post("https://api.notion.com/v1/pages", headers=ctx.headers(), json=payload, timeout=30)
        if r.status_code != 200:
            print(f"[WARN] failed seeding review card status={r.status_code}")

if __name__ == "__main__":
    sys.exit(main())
