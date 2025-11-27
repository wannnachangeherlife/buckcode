# -*- coding: utf-8 -*-
"""One-click environment doctor for Notion review system.

Checks:
- Load .env and config
- Validate NOTION_TOKEN and NOTION_REVIEW_DB_ID
- Query Notion to verify access
- Optionally ensure required DB properties exist
- Optionally initialize seed cards
- Finally run review scheduler in dry-run to validate end-to-end

Usage (PowerShell):
    python automation/workflows/doctor.py --fix --init --seed data/review_seed.csv --tags "三维,文化遗产" --max 5 --dry-run
    python automation/workflows/doctor.py --fix --full --report docs/analytics/doctor_report.html --max 10
"""
from __future__ import annotations
import os, sys, json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse
import requests

# Ensure project root on sys.path
_CUR = Path(__file__).resolve().parent
_ROOT = _CUR.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Lazy load dotenv if needed
if not ((os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")) and os.getenv("NOTION_REVIEW_DB_ID")):
    env_path = Path(".env")
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=str(env_path))
        except Exception:
            pass

# Reuse helpers from existing scripts
from automation.workflows.init_review_cards import (
    ensure_db_properties,
    read_titles,
    build_properties,
    create_page,
)
from automation.workflows import review_scheduler as rs

NOTION_VERSION = "2022-06-28"


def headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def load_config(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="One-click environment doctor")
    p.add_argument("--config", default="automation/utils/notion_migration_config.json", help="Config path")
    p.add_argument("--fix", action="store_true", help="Ensure DB properties exist")
    p.add_argument("--init", action="store_true", help="Initialize seed cards if --seed provided")
    p.add_argument("--seed", help="Seed file (txt/csv/json)")
    p.add_argument("--tags", help="Comma separated tags to apply when initializing")
    p.add_argument("--dry-run", action="store_true", help="Do not modify Notion (applies to init and scheduler)")
    p.add_argument("--max", type=int, default=5, help="Max cards to process in scheduler validation")
    p.add_argument("--report", help="Write an HTML report to this path")
    p.add_argument("--full", action="store_true", help="Run full chain: scheduler with stats+dashboard+backup (respects --dry-run)")
    return p.parse_args(argv)


def assert_token_and_db() -> tuple[str, str]:
    token = (os.getenv("NOTION_TOKEN", "") or os.getenv("NOTION_API_KEY", "")).strip()
    if not token:
        raise SystemExit("[ERROR] NOTION_TOKEN/NOTION_API_KEY is missing. Set it in .env or environment.")
    cfg = load_config("automation/utils/notion_migration_config.json")
    cfg_db = (cfg.get("review_db_id") or "").strip() if isinstance(cfg, dict) else ""
    if (not cfg_db) or cfg_db.upper().startswith("REPLACE"):
        db_id = (os.getenv("NOTION_REVIEW_DB_ID") or "").strip()
    else:
        db_id = cfg_db
    if not db_id:
        raise SystemExit("[ERROR] review_db_id missing (config or NOTION_REVIEW_DB_ID)")
    return token, db_id


def sanity_query(token: str, db_id: str, attempts: int = 3) -> Tuple[bool, str]:
    import time
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    last = ""
    for i in range(1, attempts + 1):
        try:
            r = requests.post(url, headers=headers(token), json={"page_size": 1}, timeout=40)
            if r.status_code == 200:
                return True, "OK"
            last = f"status={r.status_code} body={r.text[:240]}"
        except Exception as e:
            last = repr(e)
        time.sleep(2 ** (i - 1))
    return False, last


def run_scheduler_validation(cfg_path: str, dry_run: bool, max_n: int) -> int:
    argv = [
        "--config", cfg_path,
        "--only-due",
        "--max", str(max_n),
    ]
    if dry_run:
        argv.append("--dry-run")
    print("[INFO] Running review scheduler validation...", "dry-run=" + str(dry_run))
    return rs.main(argv)


def run_full_chain(cfg_path: str, dry_run: bool, max_n: int) -> int:
    argv = [
        "--config", cfg_path,
        "--max", str(max_n),
        "--stats",
        "--generate-dashboard",
        "--backup",
    ]
    if dry_run:
        argv.append("--dry-run")
    print("[INFO] Running full chain (stats+dashboard+backup)...", "dry-run=" + str(dry_run))
    return rs.main(argv)


def write_html_report(path: Path, sections: List[Tuple[str, str]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    html = [
        "<html><head><meta charset='utf-8'><title>Doctor Report</title>",
        "<style>body{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;color:#111;background:#fafafa}h1{font-size:22px}h2{font-size:18px;margin-top:1.2em}.ok{color:#15803d}.warn{color:#b45309}.err{color:#b91c1c}.card{background:#fff;border:1px solid #e5e7eb;padding:12px 16px;border-radius:8px;margin:10px 0}</style>",
        "</head><body>",
        "<h1>Notion Review System - Doctor Report</h1>",
    ]
    for title, content in sections:
        html.append(f"<div class='card'><h2>{title}</h2><div>{content}</div></div>")
    html.append("</body></html>")
    path.write_text("\n".join(html), encoding="utf-8")


def main(argv=None):
    args = parse_args(argv)
    token, db_id = assert_token_and_db()
    print(f"[INFO] Token present, DB={db_id}")
    ok, info = sanity_query(token, db_id)
    sections: List[Tuple[str, str]] = []
    if ok:
        print("[INFO] Notion database reachable.")
        sections.append(("Connectivity", "<p class='ok'>Reachable</p>"))
    else:
        print(f"[ERROR] Notion query failed: {info}")
        sections.append(("Connectivity", f"<p class='err'>Failed: {info}</p>"))
        if args.report:
            write_html_report(Path(args.report), sections)
        raise SystemExit(1)

    mapping = None
    if args.fix:
        print("[INFO] Ensuring required database properties exist...")
        mapping = ensure_db_properties(token, db_id)
        print("[INFO] Properties ensured.")
        sections.append(("DB Properties", "<p class='ok'>Ensured/Verified</p>"))

    if args.init and args.seed:
        print(f"[INFO] Initializing seed cards from: {args.seed}")
        try:
            titles = read_titles(args.seed)
        except Exception as e:
            raise SystemExit(f"[ERROR] reading seed failed: {e}")
        if not titles:
            print("[WARN] No titles found in seed, skip init.")
            sections.append(("Seed", "<p class='warn'>No titles found</p>"))
        else:
            if mapping is None:
                mapping = ensure_db_properties(token, db_id)
            tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
            created = 0
            for t in titles:
                props = build_properties(t, ease=2.5, tags=tags, mapping=mapping)
                ok = create_page(token, db_id, props, args.dry_run)
                if ok:
                    created += 1
            print(f"[INFO] Seed create attempted={len(titles)} created={created} dry_run={args.dry_run}")
            sections.append(("Seed", f"<p class='ok'>Attempted {len(titles)}, created {created}, dry_run={args.dry_run}</p>"))

    # Final validation via scheduler
    if args.full:
        rc = run_full_chain(args.config, args.dry_run, args.max)
        title = "Full Chain"
    else:
        rc = run_scheduler_validation(args.config, args.dry_run, args.max)
        title = "Scheduler Validation"
    if rc == 0:
        print("[DONE] Doctor finished successfully.")
        sections.append((title, "<p class='ok'>OK</p>"))
    else:
        print(f"[WARN] {title} returned code {rc}")
        sections.append((title, f"<p class='warn'>Exit code {rc}</p>"))

    if args.report:
        write_html_report(Path(args.report), sections)
        print(f"[INFO] Report written: {args.report}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
