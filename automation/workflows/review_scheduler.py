# -*- coding: utf-8 -*-
"""Review scheduler for spaced repetition Notion cards.

Usage (PowerShell):
$env:NOTION_TOKEN = "secret_xxx"
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --dry-run
python automation/workflows/review_scheduler.py --config automation/utils/notion_migration_config.json --quality 5 --max 50

Optional flags:
--only-due (default True) process only due cards
--quality INT default 4; ignored if --interactive
--interactive prompt per card quality (0-5)
--today YYYY-MM-DD override today's date
--max N limit processed cards
--dry-run do not PATCH, just show changes
--quality-file CSV/JSON mapping title→quality[,latency]
--stats write aggregated stats JSON
--tag comma list of tags to require (属性 `标签`)
--stage-min / --stage-max filter by stage range
--tasks-sync create a task when status becomes 完成
--backup save pre-update snapshot for rollback
--generate-dashboard produce markdown dashboard
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import date
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import requests
from pathlib import Path as _PathCheck

# Auto-load .env if critical vars missing (support NOTION_TOKEN/NOTION_API_KEY)
if not ((os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")) and os.getenv("NOTION_REVIEW_DB_ID")):
    env_path = _PathCheck(".env")
    if env_path.exists():
        try:
            from dotenv import load_dotenv  # python-dotenv already in requirements
            load_dotenv(dotenv_path=str(env_path))
        except Exception:
            pass

# Ensure project root is on sys.path (handles execution from subdirectory)
_CURRENT = Path(__file__).resolve().parent
_ROOT = _CURRENT.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from automation.utils.spaced_repetition import schedule_review, is_due
except ModuleNotFoundError:
    # Fallback: attempt relative import if executed as package module
    try:
        from ..utils.spaced_repetition import schedule_review, is_due  # type: ignore
    except Exception as e:  # pragma: no cover
        raise

NOTION_VERSION = "2022-06-28"
RATE_LIMIT_PER_SEC = 3

_last_requests: List[float] = []  # timestamps

def _rate_limit():
    import time
    now = time.time()
    _last_requests.append(now)
    # keep only last second entries
    window_start = now - 1.0
    while _last_requests and _last_requests[0] < window_start:
        _last_requests.pop(0)
    if len(_last_requests) > RATE_LIMIT_PER_SEC:
        sleep_for = _last_requests[0] + 1.0 - now
        if sleep_for > 0:
            time.sleep(sleep_for)

def _request_with_retry(method: str, url: str, token: str, json_payload: Dict[str, Any], timeout: int = 30, max_attempts: int = 3) -> Optional[requests.Response]:
    import time
    for attempt in range(1, max_attempts + 1):
        _rate_limit()
        try:
            r = requests.request(method, url, headers=headers(token), json=json_payload, timeout=timeout)
            if r.status_code in (200, 202):
                return r
            # Retry only on 429 / 5xx
            if r.status_code == 429 or 500 <= r.status_code < 600:
                backoff = 2 ** (attempt - 1)
                time.sleep(backoff)
                continue
            return r
        except requests.RequestException as e:
            backoff = 2 ** (attempt - 1)
            time.sleep(backoff)
    return None


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Spaced repetition review scheduler")
    p.add_argument("--config", required=True, help="Path to config json")
    p.add_argument("--quality", type=int, default=4, help="Default quality if not interactive")
    p.add_argument("--interactive", action="store_true", help="Prompt quality per card")
    p.add_argument("--only-due", action="store_true", help="Only process due cards")
    p.add_argument("--today", help="Override today's date (YYYY-MM-DD)")
    p.add_argument("--max", type=int, help="Limit number of processed cards")
    p.add_argument("--dry-run", action="store_true", help="Show planned updates only")
    p.add_argument("--quality-file", help="CSV/JSON file with per-card quality/latency")
    p.add_argument("--stats", action="store_true", help="Write stats JSON after processing")
    p.add_argument("--tag", help="Comma list of required tags")
    p.add_argument("--stage-min", type=int, help="Minimum stage to include")
    p.add_argument("--stage-max", type=int, help="Maximum stage to include")
    p.add_argument("--tasks-sync", action="store_true", help="Create related task when completed")
    p.add_argument("--backup", action="store_true", help="Save backup JSON before updates")
    p.add_argument("--generate-dashboard", action="store_true", help="Generate markdown dashboard")
    return p.parse_args(argv)


def headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def load_config(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fetch_cards(token: str, db_id: str, only_due: bool, today_iso: str) -> List[Dict[str, Any]]:
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload: Dict[str, Any] = {"page_size": 100}
    if only_due:
        # Filter 下次复习日期 <= today OR empty
        payload["filter"] = {
            "or": [
                {"property": "下次复习日期", "date": {"is_empty": True}},
                {"property": "下次复习日期", "date": {"on_or_before": today_iso}},
            ]
        }
    results: List[Dict[str, Any]] = []
    while True:
        r = _request_with_retry("POST", url, token, payload, timeout=30)
        if r is None:
            print("[ERROR] query failed (network/retry exceeded)")
            break
        if r.status_code != 200:
            print(f"[ERROR] query failed status={r.status_code} body={r.text[:300]}")
            break
        data = r.json()
        batch = data.get("results", [])
        results.extend(batch)
        next_cursor = data.get("next_cursor")
        if not next_cursor:
            break
        payload["start_cursor"] = next_cursor
    return results


def extract_properties(page: Dict[str, Any]) -> Dict[str, Any]:
    return page.get("properties", {})


def title_text(props: Dict[str, Any]) -> str:
    # Prefer dynamic detection of title-type property
    try:
        for name, meta in props.items():
            if isinstance(meta, dict) and meta.get("type") == "title":
                arr = meta.get("title") or []
                if arr:
                    return arr[0].get("text", {}).get("content", "")
    except Exception:
        pass
    # Fallback to legacy field name
    t = props.get("卡片标题", {})
    if isinstance(t, dict):
        arr = t.get("title") or []
        if arr:
            return arr[0].get("text", {}).get("content", "")
    return ""


def stage_value(props: Dict[str, Any]) -> int:
    st = props.get("阶段 Stage", {})
    if isinstance(st, dict):
        num = st.get("number")
        if isinstance(num, (int, float)):
            return int(num)
    return 0


def has_tag(props: Dict[str, Any], required: List[str]) -> bool:
    if not required:
        return True
    tag_prop = props.get("标签", {})
    if isinstance(tag_prop, dict):
        arr = tag_prop.get("multi_select") or []
        existing = {x.get("name") for x in arr if isinstance(x, dict)}
        return all(t in existing for t in required)
    return False


def load_quality_file(path: str) -> Dict[str, Tuple[int, float]]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        print(f"[WARN] quality-file not found: {p}")
        return {}
    mapping: Dict[str, Tuple[int, float]] = {}
    if p.suffix.lower() == ".json":
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for k, v in data.items():
                q = int(v.get("quality", 4))
                l = float(v.get("latency", -1))
                mapping[k] = (q, l)
        except Exception as e:
            print(f"[WARN] quality-file json parse error: {e}")
    else:
        import csv
        try:
            with p.open("r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    title = (row.get("title") or row.get("卡片标题") or "").strip()
                    if not title:
                        continue
                    q = int(row.get("quality", 4))
                    lat_raw = row.get("latency")
                    l = float(lat_raw) if lat_raw not in (None, "") else -1.0
                    mapping[title] = (q, l)
        except Exception as e:
            print(f"[WARN] quality-file csv parse error: {e}")
    return mapping


def ensure_tasks_entry(token: str, tasks_db: str, card_title: str, card_id: str, dry_run: bool, dynamic: Dict[str, str]):
    if not tasks_db:
        return
    title_field = dynamic.get("title", "名称")
    status_field = dynamic.get("status", "状态")
    relation_field = dynamic.get("relation", "关联复习卡")
    payload = {
        "parent": {"database_id": tasks_db},
        "properties": {
            title_field: {"title": [{"text": {"content": f"复习完成: {card_title}"}}]},
            relation_field: {"relation": [{"id": card_id}]},
            status_field: {"select": {"name": "完成"}},
        },
    }
    if dry_run:
        print(json.dumps({"create_task": payload}, ensure_ascii=False))
        return
    r = _request_with_retry("POST", "https://api.notion.com/v1/pages", token, payload, timeout=30)
    if r.status_code != 200:
        print(f"[WARN] task sync failed status={r.status_code} body={r.text[:160]}")


def write_stats(path: Path, stats: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_dashboard(md_path: Path, stats: Dict[str, Any]):
    md_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 复习统计仪表板", "", f"总处理卡片: {stats.get('processed',0)}", f"已更新: {stats.get('updated',0)}", "", "## Stage 分布", "", "| Stage | Count |", "|-------|-------|",
    ]
    for stage, cnt in sorted(stats.get("stage_distribution", {}).items()):
        lines.append(f"| {stage} | {cnt} |")
    avg_before = stats.get('avg_ease_before',0)
    avg_after = stats.get('avg_ease_after',0)
    diff = avg_after - avg_before
    # Ease diff bar (centered)
    bar_len = 20
    if avg_before > 0:
        ratio = (avg_after / avg_before) if avg_before else 1
    else:
        ratio = 1
    filled = min(bar_len, max(0, int(bar_len * ratio)))
    ease_bar = '█' * filled + '░' * (bar_len - filled)
    lines.extend([
        '', '## Ease 变化', f'平均Ease前: {avg_before:.2f}', f'平均Ease后: {avg_after:.2f}', f'变化差值: {diff:+.2f}', f'Ease 比例条: {ease_bar}', '', '## 到期与未到期', f'到期卡片数: {stats.get('due_count',0)}', f'未到期跳过: {stats.get('skipped_not_due',0)}',
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def _svg_header(width: int, height: int) -> str:
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>\n"


def generate_svg_charts(out_dir: Path, stats: Dict[str, Any]):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Stage distribution bar chart
    dist = stats.get("stage_distribution", {})
    stages = sorted(dist.keys())
    if stages:
        bar_w = 40
        gap = 10
        left_pad = 40
        bottom_pad = 30
        max_cnt = max(dist.values()) or 1
        height = 240
        width = left_pad + len(stages) * (bar_w + gap)
        svg = [_svg_header(width, height)]
        svg.append("<style> text{font-family:Segoe UI,Arial;font-size:12px;fill:#333} .axis{stroke:#888;stroke-width:1} </style>")
        # axes
        svg.append(f"<line class='axis' x1='{left_pad}' y1='10' x2='{left_pad}' y2='{height-bottom_pad}' />")
        svg.append(f"<line class='axis' x1='{left_pad}' y1='{height-bottom_pad}' x2='{width-10}' y2='{height-bottom_pad}' />")
        # bars
        x = left_pad + gap
        for s in stages:
            cnt = dist[s]
            bar_h = int((height - bottom_pad - 20) * (cnt / max_cnt))
            y = height - bottom_pad - bar_h
            svg.append(f"<rect x='{x}' y='{y}' width='{bar_w}' height='{bar_h}' fill='#4C78A8' />")
            svg.append(f"<text x='{x + bar_w/2}' y='{height-bottom_pad+18}' text-anchor='middle'>S{s}</text>")
            svg.append(f"<text x='{x + bar_w/2}' y='{y-4}' text-anchor='middle'>{cnt}</text>")
            x += bar_w + gap
        svg.append("</svg>")
        raw_stage = "\n".join(svg)
        (out_dir / "stage_distribution.svg").write_text(_minify_svg(raw_stage), encoding="utf-8")

    # Ease compare chart
    before = float(stats.get("avg_ease_before", 0) or 0)
    after = float(stats.get("avg_ease_after", 0) or 0)
    width, height = 360, 180
    svg2 = [_svg_header(width, height)]
    svg2.append("<style> text{font-family:Segoe UI,Arial;font-size:12px;fill:#333} .bar{fill:#F58518} .bar2{fill:#54A24B} </style>")
    max_val = max(before, after, 1)
    scale = (height - 50) / max_val
    # before bar
    b_h = int(before * scale)
    a_h = int(after * scale)
    svg2.append(f"<rect class='bar' x='80' y='{height-30-b_h}' width='60' height='{b_h}' />")
    svg2.append(f"<text x='110' y='{height-10}' text-anchor='middle'>Ease前 {before:.2f}</text>")
    # after bar
    svg2.append(f"<rect class='bar2' x='220' y='{height-30-a_h}' width='60' height='{a_h}' />")
    svg2.append(f"<text x='250' y='{height-10}' text-anchor='middle'>Ease后 {after:.2f}</text>")
    svg2.append("</svg>")
    raw_ease = "\n".join(svg2)
    (out_dir / "ease_compare.svg").write_text(_minify_svg(raw_ease), encoding="utf-8")


def _minify_svg(content: str) -> str:
    # Simple SVG minifier: remove newlines, duplicate spaces
    import re
    c = re.sub(r">\s+<", "><", content)  # remove inter-tag whitespace
    c = re.sub(r"\s{2,}", " ", c)
    return c.strip()

def _append_history(stats: Dict[str, Any]):
    """Append today's stats to history file for longitudinal charts."""
    history_path = Path("docs/analytics/history.json")
    history_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        history = json.loads(history_path.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            history = []
    except Exception:
        history = []
    entry = {
        "date": time.strftime("%Y-%m-%d"),
        "processed": stats.get("processed", 0),
        "updated": stats.get("updated", 0),
        "avg_ease_before": stats.get("avg_ease_before", 0),
        "avg_ease_after": stats.get("avg_ease_after", 0),
        "stage_distribution": stats.get("stage_distribution", {}),
    }
    # Replace existing date entry if present
    history = [h for h in history if h.get("date") != entry["date"]] + [entry]
    # Limit length (keep last 180 days)
    history = sorted(history, key=lambda x: x.get("date"))[-180:]
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

def _cleanup_backups(retain_days: int = 30, retain_max: int = 50):
    backup_dir = Path("automation/analytics")
    if not backup_dir.exists():
        return
    backups = sorted(backup_dir.glob("review_backup_*.json"))
    if not backups:
        return
    # Remove by age and count
    today = time.strftime("%Y-%m-%d")
    def _days_old(p: Path) -> int:
        name = p.stem.replace("review_backup_", "")
        try:
            from datetime import datetime
            dt = datetime.strptime(name, "%Y-%m-%d")
            delta = datetime.strptime(today, "%Y-%m-%d") - dt
            return delta.days
        except Exception:
            return 0
    # Filter those to keep by age
    keep = [p for p in backups if _days_old(p) <= retain_days]
    # If still too many keep latest subset
    if len(keep) > retain_max:
        keep = keep[-retain_max:]
    keep_set = {p for p in keep}
    for p in backups:
        if p not in keep_set:
            try:
                p.unlink()
            except Exception:
                pass


def patch_card(token: str, page_id: str, updates: Dict[str, Any], dry_run: bool):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    if dry_run:
        print(json.dumps({"id": page_id, "updates": updates}, ensure_ascii=False))
        return True
    r = _request_with_retry("PATCH", url, token, {"properties": updates}, timeout=30)
    if r and r.status_code == 200:
        return True
    if r:
        print(f"[WARN] patch failed id={page_id} status={r.status_code} body={r.text[:200]}")
    else:
        print(f"[WARN] patch failed id={page_id} no response")
    return False


def introspect_tasks_schema(token: str, tasks_db: str) -> Dict[str, str]:
    mapping = {"title": "名称", "status": "状态", "relation": "关联复习卡"}
    if not tasks_db:
        return mapping
    r = _request_with_retry("GET", f"https://api.notion.com/v1/databases/{tasks_db}", token, {}, timeout=30)
    if not r or r.status_code != 200:
        return mapping
    data = r.json()
    props = data.get("properties", {})
    for name, meta in props.items():
        if meta.get("type") == "title":
            mapping["title"] = name
            break
    for name, meta in props.items():
        if meta.get("type") == "select" and name.lower() in ("状态", "status", "任务状态"):
            mapping["status"] = name
            break
    for name, meta in props.items():
        if meta.get("type") == "relation":
            mapping["relation"] = name
            break
    return mapping


def build_updates(card_props: Dict[str, Any], schedule: Dict[str, Any], today_iso: str) -> Dict[str, Any]:
    return {
        "阶段 Stage": {"number": schedule["stage"]},
        "Ease": {"number": schedule["ease"]},
        "Interval": {"number": schedule["interval"]},
        "上次复习日期": {"date": {"start": today_iso}},
        "下次复习日期": {"date": {"start": schedule["next_date"]}},
        "状态": {"select": {"name": schedule["status"]}},
    }


def choose_quality(default_q: int) -> int:
    while True:
        raw = input(f"Quality (0-5)[default {default_q}]: ").strip()
        if raw == "":
            return default_q
        if raw.isdigit() and 0 <= int(raw) <= 5:
            return int(raw)
        print("Invalid. Enter 0..5.")


def main(argv=None):
    args = parse_args(argv)
    config = load_config(args.config)
    cfg_db = (config.get("review_db_id") or "").strip()
    if (not cfg_db) or cfg_db.upper().startswith("REPLACE"):
        review_db = (os.getenv("NOTION_REVIEW_DB_ID") or "").strip()
    else:
        review_db = cfg_db
    if not review_db:
        print("[ERROR] review_db_id missing (set in config or NOTION_REVIEW_DB_ID)")
        return 1
    tasks_db = config.get("tasks_db_id")
    token = os.getenv("NOTION_TOKEN", "") or os.getenv("NOTION_API_KEY", "")
    if not token:
        print("[WARN] NOTION_TOKEN/NOTION_API_KEY is empty")
    tasks_schema_map = introspect_tasks_schema(token, tasks_db) if args.tasks_sync else {}
    today_iso = args.today or date.today().isoformat()
    try:
        today_obj = date.fromisoformat(today_iso)
    except ValueError:
        print(f"[ERROR] invalid --today date: {today_iso}")
        return 1

    pages = fetch_cards(token, review_db, args.only_due, today_iso)
    print(f"[INFO] fetched review pages total={len(pages)} only_due={args.only_due}")
    quality_map = load_quality_file(args.quality_file)
    required_tags = [t.strip() for t in args.tag.split(",")] if args.tag else []
    processed = 0
    updated = 0
    due_count = 0
    skipped_not_due = 0
    ease_before_sum = 0.0
    ease_after_sum = 0.0
    stage_distribution: Dict[int, int] = {}
    backup_entries: List[Dict[str, Any]] = []
    for page in pages:
        props = extract_properties(page)
        title = title_text(props)
        stage_val = stage_value(props)
        is_due_flag = is_due(props, today_obj)
        if is_due_flag:
            due_count += 1
        if args.only_due and not is_due_flag:
            skipped_not_due += 1
            continue
        if required_tags and not has_tag(props, required_tags):
            continue
        if args.stage_min is not None and stage_val < args.stage_min:
            continue
        if args.stage_max is not None and stage_val > args.stage_max:
            continue
        if args.backup:
            backup_entries.append({"id": page.get("id"), "properties": props})
        q, lat = None, None
        if title in quality_map:
            q, lat = quality_map[title]
            if q is None:
                q = args.quality
        else:
            q = choose_quality(args.quality) if args.interactive else args.quality
        sched = schedule_review(props, quality=int(q), today=today_obj, latency=(lat if lat and lat >= 0 else None))
        ease_prop = props.get("Ease", {})
        if isinstance(ease_prop, dict) and isinstance(ease_prop.get("number"), (int, float)):
            ease_before_sum += float(ease_prop.get("number"))
        ease_after_sum += sched["ease"]
        updates = build_updates(props, sched, today_iso)
        ok = patch_card(token, page.get("id"), updates, args.dry_run)
        if ok:
            updated += 1
        processed += 1
        stage_distribution[sched["stage"]] = stage_distribution.get(sched["stage"], 0) + 1
        if args.tasks_sync and sched["status"] == "完成":
            ensure_tasks_entry(token, tasks_db, title, page.get("id"), args.dry_run, tasks_schema_map)
        if args.max and processed >= args.max:
            break
    stats = {
        "processed": processed,
        "updated": updated,
        "due_count": due_count,
        "skipped_not_due": skipped_not_due,
        "avg_ease_before": (ease_before_sum / updated) if updated else 0.0,
        "avg_ease_after": (ease_after_sum / updated) if updated else 0.0,
        "stage_distribution": stage_distribution,
    }
    if args.backup and backup_entries:
        backup_dir = Path("automation/analytics")
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"review_backup_{today_iso}.json"
        backup_path.write_text(json.dumps(backup_entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[INFO] backup saved: {backup_path}")
    if args.stats:
        stats_path = Path("automation/analytics/review_stats.json")
        write_stats(stats_path, stats)
        # Mirror into docs for static hosting
        try:
            mirror_dir = Path("docs/analytics")
            mirror_dir.mkdir(parents=True, exist_ok=True)
            mirror_copy = mirror_dir / "review_stats.json"
            mirror_copy.write_text(stats_path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as e:
            print(f"[WARN] mirror stats failed: {e}")
        print("[INFO] stats JSON written + mirrored to docs/analytics")
        _append_history(stats)
    if args.generate_dashboard:
        dash_path = Path("docs/analytics/REVIEW_DASHBOARD.md")
        charts_dir = Path("docs/analytics")
        generate_dashboard(dash_path, stats)
        generate_svg_charts(charts_dir, stats)
        # Append image references if not present
        try:
            content = dash_path.read_text(encoding="utf-8")
        except Exception:
            content = ""
        if "stage_distribution.svg" not in content or "ease_compare.svg" not in content:
            appendix = "\n\n## 可视化图表\n\n![](./stage_distribution.svg)\n\n![](./ease_compare.svg)\n"
            dash_path.write_text(content + appendix, encoding="utf-8")
        print("[INFO] dashboard + SVG charts generated")
    print(f"[DONE] processed={processed} updated={updated} dry_run={args.dry_run}")
    # Cleanup old backups after run
    _cleanup_backups()
    return 0


if __name__ == "__main__":
    sys.exit(main())
