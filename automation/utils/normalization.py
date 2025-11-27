# -*- coding: utf-8 -*-
"""Normalization utilities for CSV → Notion migration."""
from __future__ import annotations
import re
import unicodedata
from datetime import datetime
from typing import List, Optional
from urllib.parse import unquote

DATE_FORMATS = ["%Y年%m月%d日", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"]

PRIORITY_MAP = {
    "高优先级": "高",
    "中优先级": "中",
    "低优先级": "低",
    "高": "高",
    "中": "中",
    "低": "低",
}

STATUS_MAP = {
    "待完成": "未开始",
    "进行中": "进行中",
    "未开始": "未开始",
    "已完成": "已完成",
    "进行": "进行中",
}

MULTI_SPLIT_PATTERN = re.compile(r"[,，;；]\s*")


def parse_date(raw: str) -> Optional[str]:
    if not raw or not raw.strip():
        return None
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    # Try digits only yyyymmdd
    if re.match(r"^\d{8}$", raw):
        try:
            dt = datetime.strptime(raw, "%Y%m%d")
            return dt.date().isoformat()
        except ValueError:
            pass
    return None


def normalize_priority(v: str) -> str:
    return PRIORITY_MAP.get(v.strip(), v.strip()) if v else ""


def normalize_status(v: str) -> str:
    return STATUS_MAP.get(v.strip(), v.strip()) if v else ""


def split_multi(raw: str) -> List[str]:
    if not raw:
        return []
    # Replace Chinese punctuation variants with comma
    cleaned = raw.replace("、", ",")
    parts = re.split(r"[,，;；]\s*", cleaned)
    return [p.strip() for p in parts if p.strip()]


def coerce_number(raw: str) -> Optional[float]:
    if raw is None:
        return None
    txt = raw.strip()
    if not txt:
        return None
    try:
        return float(txt)
    except ValueError:
        # Attempt to strip non-digit
        txt2 = re.sub(r"[^0-9.+-]", "", txt)
        try:
            return float(txt2) if txt2 else None
        except ValueError:
            return None


def decode_url(s: str) -> str:
    return unquote(s) if s else s


def strip_markdown_quotes(text: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    cleaned = []
    for ln in lines:
        if ln.startswith(">"):
            cleaned.append(ln.lstrip("> "))
        else:
            cleaned.append(ln)
    return "\n".join(cleaned)


def normalize_text_width(s: str) -> str:
    return unicodedata.normalize("NFKC", s) if s else s


def build_title(value: str) -> dict:
    return {"title": [{"text": {"content": value or "(空)"}}]}


def build_rich(value: str) -> dict:
    return {"rich_text": [{"text": {"content": value or ""}}]} if value else {"rich_text": []}

__all__ = [
    "parse_date",
    "normalize_priority",
    "normalize_status",
    "split_multi",
    "coerce_number",
    "decode_url",
    "strip_markdown_quotes",
    "normalize_text_width",
    "build_title",
    "build_rich",
]
