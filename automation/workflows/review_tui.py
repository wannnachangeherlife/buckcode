# -*- coding: utf-8 -*-
"""Terminal TUI to review due cards and capture quality + latency.

Generates a CSV usable by --quality-file for batch scheduling later.

Usage:
$env:NOTION_TOKEN="secret_xxx"
python automation/workflows/review_tui.py --config automation/utils/notion_migration_config.json --out data/qualities.csv --limit 30

Controls:
ENTER 显示卡片内容后开始计时，答出后再次 ENTER 停止计时。
1-5 / 0 输入质量得分；(空回车=默认4)。
Q 退出保存。

CSV columns: title,quality,latency
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
import requests

NOTION_VERSION = "2022-06-28"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Interactive review TUI")
    p.add_argument("--config", required=True, help="Path to config json")
    p.add_argument("--out", required=True, help="Output CSV path")
    p.add_argument("--limit", type=int, help="Limit number of cards")
    p.add_argument("--today", help="Override today ISO date")
    return p.parse_args(argv)


def headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def load_config(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fetch_due(token: str, db_id: str, today_iso: str) -> List[Dict[str, Any]]:
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {
        "filter": {
            "or": [
                {"property": "下次复习日期", "date": {"is_empty": True}},
                {"property": "下次复习日期", "date": {"on_or_before": today_iso}},
            ]
        },
        "page_size": 50,
    }
    results: List[Dict[str, Any]] = []
    while True:
        r = requests.post(url, headers=headers(token), json=payload, timeout=30)
        if r.status_code != 200:
            print(f"[ERROR] query failed status={r.status_code} body={r.text[:200]}")
            break
        data = r.json()
        batch = data.get("results", [])
        results.extend(batch)
        nxt = data.get("next_cursor")
        if not nxt:
            break
        payload["start_cursor"] = nxt
        if len(results) >= 200:
            break
    return results


def title_text(props: Dict[str, Any]) -> str:
    t = props.get("卡片标题", {})
    if isinstance(t, dict):
        arr = t.get("title") or []
        if arr:
            return arr[0].get("text", {}).get("content", "")
    return ""


def main(argv=None):
    args = parse_args(argv)
    token = os.getenv("NOTION_TOKEN", "") or os.getenv("NOTION_API_KEY", "")
    if not token:
        print("[ERROR] NOTION_TOKEN/NOTION_API_KEY missing")
        return 1
    cfg = load_config(args.config)
    review_db = cfg.get("review_db_id")
    if not review_db:
        print("[ERROR] review_db_id missing in config")
        return 1
    today_iso = args.today or time.strftime("%Y-%m-%d")
    pages = fetch_due(token, review_db, today_iso)
    cards = []
    for p in pages:
        props = p.get("properties", {})
        cards.append({"id": p.get("id"), "title": title_text(props)})
    if args.limit:
        cards = cards[:args.limit]
    if not cards:
        print("[INFO] no due cards")
        return 0
    print(f"[INFO] due cards loaded: {len(cards)}")
    rows: List[Dict[str, Any]] = []
    for idx, c in enumerate(cards, 1):
        print(f"\n==== [{idx}/{len(cards)}] {c['title']} ====")
        input("按 ENTER 显示并开始计时...")
        start = time.time()
        input("回忆完毕后按 ENTER 停止计时...")
        latency = time.time() - start
        val = input("输入质量(0-5, 回车默认4, Q退出): ").strip().upper()
        if val == 'Q':
            print("[INFO] 用户中断，保存已收集数据")
            break
        if val == '':
            quality = 4
        elif val.isdigit() and 0 <= int(val) <= 5:
            quality = int(val)
        else:
            print("无效输入，使用默认4")
            quality = 4
        rows.append({"title": c['title'], "quality": quality, "latency": round(latency,2)})
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title','quality','latency'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"[DONE] written {len(rows)} rows -> {out_path}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
