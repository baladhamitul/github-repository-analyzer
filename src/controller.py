from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

from src.github_client import GitHubClient
from src.analyzer import RepoAnalyzer
from src.filters import CommitFilter
from src.util import ensure_dirs, write_csv, EXPORTS_DIR
from src import reports  # new


class AppController:
    def __init__(self):
        ensure_dirs()
        self.client = GitHubClient()

    def _resolve_dates(self, since: Optional[str], until: Optional[str]):
        if until:
            try:
                until_dt = datetime.fromisoformat(until.replace("Z", "+00:00"))
            except Exception:
                raise ValueError(f"Invalid --until format: {until}")
        else:
            until_dt = datetime.now(timezone.utc)

        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            except Exception:
                raise ValueError(f"Invalid --since format: {since}")
        else:
            since_dt = until_dt - timedelta(days=30)
        return since_dt, until_dt

    def run_with_args(self, args):
        if "/" not in args.repo:
            raise ValueError("repo must look like owner/repo, e.g., pandas-dev/pandas")
        owner, repo = args.repo.split("/", 1)

        if not os.getenv("GITHUB_TOKEN"):
            print("⚠️  No GITHUB_TOKEN found (.env). You may hit rate limits on busy repos.")

        analyzer = RepoAnalyzer(self.client, owner, repo)

        try:
            repo_info = analyzer.fetch_repo()
        except Exception as e:
            print(f"❌ Failed to fetch repository: {e}")
            return

        try:
            languages = analyzer.fetch_languages()
        except Exception as e:
            print(f"❌ Failed to fetch languages: {e}")
            languages = {}

        print(f"📦 {owner}/{repo} — ⭐ {repo_info.get('stargazers_count')}  🍴 {repo_info.get('forks_count')}")
        print(f"🗣 languages: {', '.join(languages.keys()) or 'unknown'}")

        try:
            since_dt, until_dt = self._resolve_dates(args.since, args.until)
        except ValueError as ve:
            print(f"❌ {ve}")
            return

        print(f"⏱️  commits window: {since_dt.isoformat()} → {until_dt.isoformat()}")
        try:
            commits = analyzer.fetch_commits(since=since_dt.isoformat(), until=until_dt.isoformat())
        except Exception as e:
            print(f"❌ Failed to fetch commits: {e}")
            return

        rows = analyzer.commits_to_rows(commits)

        # Filters
        cf = CommitFilter(message_regex=args.msg, author_regex=args.author, path_regex=args.path)
        filtered = cf.apply_rows(rows)

        # Exports
        base = f"{owner}_{repo}"
        full_csv = EXPORTS_DIR / f"{base}_commits.csv"
        filt_csv = EXPORTS_DIR / f"{base}_commits_filtered.csv"
        fields = (
            "sha","date","author_name","author_email","author_login",
            "committer_name","committer_email","committer_login","message","url",
        )
        write_csv(full_csv, rows, fields)
        write_csv(filt_csv, filtered, fields)
        print(f"✅ Saved {len(rows)} commits → {full_csv}")
        print(f"✅ Saved {len(filtered)} filtered commits → {filt_csv}")

        try:
            contributors: List[Dict] = analyzer.fetch_contributors()
            contrib_rows = [
                {"login": c.get("login"), "contributions": c.get("contributions")}
                for c in contributors
            ]
            contrib_csv = EXPORTS_DIR / f"{base}_contributors.csv"
            write_csv(contrib_csv, contrib_rows, ("login", "contributions"))
            print(f"✅ Saved {len(contrib_rows)} contributors → {contrib_csv}")
        except Exception as e:
            print(f"❌ Failed to fetch contributors: {e}")
            contributors = []

        if languages:
            lang_rows = [{"language": k, "bytes": v} for k, v in languages.items()]
            lang_csv = EXPORTS_DIR / f"{base}_languages.csv"
            write_csv(lang_csv, lang_rows, ("language", "bytes"))
            print(f"✅ Saved languages → {lang_csv}")

        # Charts
        if getattr(args, "charts", False):
            print("📈 Rendering charts ...")
            p1 = reports.commits_over_time(rows, EXPORTS_DIR / f"{base}_commits_over_time.png")
            p2 = reports.top_contributors(contributors, 10, EXPORTS_DIR / f"{base}_top_contributors.png")
            p3 = reports.language_share(languages, EXPORTS_DIR / f"{base}_language_share.png")
            print(f"🖼  {p1}")
            print(f"🖼  {p2}")
            print(f"🖼  {p3}")

        print("🎉 Done.")
