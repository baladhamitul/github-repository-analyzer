from __future__ import annotations
from typing import Dict, List, Optional

from src.github_client import GitHubClient


class RepoAnalyzer:
    def __init__(self, client: GitHubClient, owner: str, repo: str):
        # ensure client knows owner/repo for cache paths
        client.owner, client.repo = owner, repo
        self.client = client
        self.owner = owner
        self.repo = repo

    # ----- fetchers -----
    def fetch_repo(self) -> Dict:
        return self.client.get(f"/repos/{self.owner}/{self.repo}")

    def fetch_languages(self) -> Dict[str, int]:
        return self.client.get(f"/repos/{self.owner}/{self.repo}/languages")

    def fetch_contributors(self) -> List[Dict]:
        # per_page not supported here; GitHub uses default=30; paged() follows Link headers
        return self.client.paged(f"/repos/{self.owner}/{self.repo}/contributors")

    def fetch_commits(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None,
        author: Optional[str] = None,
        path: Optional[str] = None,
    ) -> List[Dict]:
        params: Dict[str, str] = {}
        if since:
            params["since"] = since  # ISO 8601
        if until:
            params["until"] = until
        if author:
            params["author"] = author
        if path:
            params["path"] = path
        # improvement: request larger pages to reduce total API calls
        params["per_page"] = "100"
        return self.client.paged(f"/repos/{self.owner}/{self.repo}/commits", params=params)

    # ----- transforms -----
    def commits_to_rows(self, commits: List[Dict]) -> List[Dict]:
        """
        Flatten commit JSON into a simple row dict for CSV/DF.
        """
        rows: List[Dict] = []
        for c in commits:
            sha = c.get("sha")
            commit = c.get("commit", {})
            author = c.get("author") or {}
            committer = c.get("committer") or {}
            commit_author = commit.get("author") or {}
            commit_committer = commit.get("committer") or {}
            message = (commit.get("message") or "").splitlines()[0][:500]

            rows.append(
                {
                    "sha": sha,
                    "date": commit_author.get("date"),
                    "author_name": commit_author.get("name"),
                    "author_email": commit_author.get("email"),
                    "author_login": author.get("login"),
                    "committer_name": commit_committer.get("name"),
                    "committer_email": commit_committer.get("email"),
                    "committer_login": committer.get("login"),
                    "message": message,
                    "url": c.get("html_url"),
                }
            )
        return rows
