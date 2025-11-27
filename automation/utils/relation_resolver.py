# -*- coding: utf-8 -*-
"""Relation resolution cache for Notion migration."""
from __future__ import annotations
import json
import os
import time
from typing import Dict, Optional
import requests

NOTION_VERSION = "2022-06-28"

class RelationResolver:
    def __init__(self, token: str, cache_path: str):
        self.token = token
        self.cache_path = cache_path
        self._cache: Dict[str, str] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}
        else:
            self._cache = {}

    def save(self):
        tmp = self.cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.cache_path)

    def ensure(self, title: str, db_id: str) -> Optional[str]:
        """Return page ID for title, create if missing."""
        norm_title = title.strip()
        if not norm_title:
            return None
        if norm_title in self._cache:
            return self._cache[norm_title]
        page_id = self._search(norm_title)
        if page_id:
            self._cache[norm_title] = page_id
            return page_id
        created_id = self._create_minimal(norm_title, db_id)
        if created_id:
            self._cache[norm_title] = created_id
        return created_id

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _search(self, query: str) -> Optional[str]:
        url = "https://api.notion.com/v1/search"
        body = {"query": query, "filter": {"value": "page", "property": "object"}, "page_size": 5}
        try:
            r = requests.post(url, headers=self._headers(), json=body, timeout=20)
            if r.status_code != 200:
                return None
            data = r.json()
            for res in data.get("results", []):
                props = res.get("properties", {})
                if res.get("object") == "page":
                    # Accept first match
                    return res.get("id")
        except Exception:
            return None
        return None

    def _create_minimal(self, title: str, db_id: str) -> Optional[str]:
        url = "https://api.notion.com/v1/pages"
        body = {
            "parent": {"database_id": db_id},
            "properties": {"名称": {"title": [{"text": {"content": title}}]}},
        }
        try:
            r = requests.post(url, headers=self._headers(), json=body, timeout=30)
            if r.status_code == 200:
                return r.json().get("id")
        except Exception:
            return None
        return None

# Convenience factory

def build_relation_resolver(token: str, cache_path: str) -> RelationResolver:
    return RelationResolver(token=token, cache_path=cache_path)
