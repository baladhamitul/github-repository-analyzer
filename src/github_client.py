from __future__ import annotations
import os
import datetime
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests # type: ignore
from dotenv import load_dotenv # type: ignore

from src.util import ensure_dirs, cache_subdir, parse_link_header, save_json


class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, owner: Optional[str] = None, repo: Optional[str] = None):
        load_dotenv()
        ensure_dirs()
        self.owner = owner
        self.repo = repo
        self.session = requests.Session()
        token = os.getenv("GITHUB_TOKEN")
        if token:
            # GitHub accepts either "token" or "Bearer" for classic/fine-grained PATs
            self.session.headers["Authorization"] = f"token {token}"
        self.session.headers["Accept"] = "application/vnd.github+json"
        self.session.headers["User-Agent"] = "repo-analyzer/0.1"

    def _cache_path(self, endpoint: str, page_idx: int) -> Path:
        owner = self.owner or "unknown_owner"
        repo = self.repo or "unknown_repo"
        safe_ep = endpoint.strip("/").replace("/", "_")
        return cache_subdir(owner, repo) / f"{safe_ep}_p{page_idx}.json"

    def _rate_limit_error(self, resp: requests.Response) -> None:
        reset_ts = int(resp.headers.get("X-RateLimit-Reset", "0"))
        reset_dt = datetime.datetime.utcfromtimestamp(reset_ts).isoformat() + "Z"
        remaining = resp.headers.get("X-RateLimit-Remaining", "?")
        raise RuntimeError(
            f"Rate limit exceeded. Remaining={remaining}. Resets at {reset_dt}. "
            f"Set GITHUB_TOKEN in .env to avoid this."
        )

    def get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.BASE}{path}"
        resp = self.session.get(url, params=params, timeout=20)
        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            self._rate_limit_error(resp)
        if not resp.ok:
            raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    def paged(self, path: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Iterate all pages for list endpoints, cache each page to JSON.
        Returns a flat list of items.
        """
        url = f"{self.BASE}{path}"
        page_idx = 1
        items: List[Dict] = []

        while True:
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
                self._rate_limit_error(resp)
            if not resp.ok:
                raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text[:300]}")

            data = resp.json()
            save_json(self._cache_path(path, page_idx), data)

            if isinstance(data, list):
                items.extend(data)
            else:
                # Some endpoints return dicts with 'items'
                items.extend(data.get("items", []))

            links = parse_link_header(resp.headers.get("Link"))
            next_url = links.get("next")
            if not next_url:
                break
            url = next_url
            params = None  # next URL already includes query string
            page_idx += 1

        return items
