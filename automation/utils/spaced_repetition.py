# -*- coding: utf-8 -*-
"""Spaced repetition scheduling utilities (SM-2 inspired).

Properties expected on Notion review card pages:
- 阶段 Stage (number): repetition count / stage
- Ease (number): easiness factor >= 1.3
- Interval (number): last scheduled interval in days
- 上次复习日期 (date): last review date
- 下次复习日期 (date): next review date
- 状态 (select): 新建 / 复习 / 重置 / 完成

Usage:
from spaced_repetition import schedule_review
updated = schedule_review(card_props, quality=4, today=date.today())
"""
from __future__ import annotations
from datetime import date, timedelta
from typing import Dict, Any, Optional

MIN_EASE = 1.3

# Quality meaning reference (0-5)
# 5: 完全熟练 (perfect recall)
# 4: 基本熟练 (minor hesitation)
# 3: 勉强回忆 (struggled but correct)
# 2: 模糊 / 部分错误 (incorrect details)
# 1: 错误 (failure)
# 0: 完全陌生 (blank)

def schedule_review(props: Dict[str, Any], quality: int, today: date, latency: Optional[float] = None) -> Dict[str, Any]:
    """Compute next scheduling values.

    Args:
        props: Existing Notion properties dict (raw page properties object). Keys should include the property names used.
        quality: 0-5 integer rating of current recall performance.
        today: date of the review event.
    Returns:
        dict with fields: stage, ease, interval, next_date, status
    """
    # Extract existing numeric values safely
    def _num(prop_name: str, default: float) -> float:
        val = props.get(prop_name, {})
        if isinstance(val, dict) and "number" in val:
            return float(val["number"]) if val["number"] is not None else default
        return default

    stage = int(_num("阶段 Stage", 0))
    ease = float(_num("Ease", 2.5))
    interval = int(_num("Interval", 1))

    # Apply SM-2 style adjustments
    if quality < 3:
        # Failed recall resets stage
        stage = 0
        interval = 1
        # Penalize ease slightly
        ease = ease - 0.20
        status = "重置"
    else:
        stage += 1
        if stage == 1:
            interval = 1
        elif stage == 2:
            interval = 6
        else:
            interval = int(round(interval * ease))
        # Ease factor update formula
        ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        status = "复习"

    # Latency adjustment (optional): slower recall reduces ease slightly.
    # latency is seconds; cap influence at 12s. penalty up to 0.08.
    if latency is not None and latency >= 0 and quality >= 3:
        factor = min(latency / 12.0, 1.0)
        ease -= 0.08 * factor

    # Micro bonus for perfect fast recall
    if latency is not None and quality == 5 and latency < 3:
        ease += 0.02

    if ease < MIN_EASE:
        ease = MIN_EASE

    next_date = today + timedelta(days=interval)

    # Optionally mark completion if stage high and quality excellent
    if stage >= 8 and quality >= 4:
        status = "完成"

    return {
        "stage": stage,
        "ease": round(ease, 2),
        "interval": interval,
        "next_date": next_date.isoformat(),
        "status": status,
    }


def is_due(props: Dict[str, Any], today: date) -> bool:
    """Determine if card is due for review."""
    due_prop = props.get("下次复习日期", {})
    if isinstance(due_prop, dict):
        date_obj = due_prop.get("date") or {}
        start = date_obj.get("start")
        if not start:
            return True
        try:
            due_date = date.fromisoformat(start.split("T")[0])
            return due_date <= today
        except Exception:
            return True
    return True

__all__ = ["schedule_review", "is_due"]
