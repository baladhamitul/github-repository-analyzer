from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache"
EXPORTS_DIR = DATA_DIR / "exports"


def ensure_dirs() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def cache_subdir(owner: str, repo: str) -> Path:
    p = CACHE_DIR / f"{owner}_{repo}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def parse_link_header(link_header: str | None) -> Dict[str, str]:
    """
    Parse RFC5988 Link header to a dict: {'next': 'url', 'last': 'url', ...}
    """
    if not link_header:
        return {}
    parts = [p.strip() for p in link_header.split(",")]
    out: Dict[str, str] = {}
    for part in parts:
        if ";" not in part:
            continue
        url_part, *params = [x.strip() for x in part.split(";")]
        if url_part.startswith("<") and url_part.endswith(">"):
            url = url_part[1:-1]
        else:
            continue
        rel = None
        for pp in params:
            if pp.startswith('rel="') and pp.endswith('"'):
                rel = pp[5:-1]
                break
        if rel:
            out[rel] = url
    return out


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], field_order: Tuple[str, ...]) -> None:
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(field_order))
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in field_order})
