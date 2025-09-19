from __future__ import annotations
import re
from typing import Dict, Iterable, List, Optional

class CommitFilter:
    def __init__(
        self,
        message_regex: Optional[str] = None,
        author_regex: Optional[str] = None,
        path_regex: Optional[str] = None,  # placeholder; needs commit-file API calls to be effective
        flags: int = re.IGNORECASE,
    ):
        self.message_re = re.compile(message_regex, flags) if message_regex else None
        self.author_re = re.compile(author_regex, flags) if author_regex else None
        self.path_re = re.compile(path_regex, flags) if path_regex else None

    def apply_rows(self, rows: Iterable[Dict]) -> List[Dict]:
        out: List[Dict] = []
        for r in rows:
            if self.message_re and not self.message_re.search(r.get("message") or ""):
                continue
            if self.author_re:
                blob = " ".join([
                    str(r.get("author_name") or ""),
                    str(r.get("author_email") or ""),
                    str(r.get("author_login") or "")
                ])
                if not self.author_re.search(blob):
                    continue
            # path filter requires augmenting rows with 'files' -> skip for now
            out.append(r)
        return out
