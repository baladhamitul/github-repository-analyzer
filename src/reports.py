from __future__ import annotations
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt # type: ignore
import matplotlib.dates as mdates # type: ignore

from src.util import EXPORTS_DIR


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# -------- Commits over time (line) --------
def commits_over_time(rows: Iterable[Dict], out_path: Optional[Path] = None) -> Path:
    """
    Line chart of commits per day. High-DPI, date-aware ticks, grid, and a
    peak annotation for readability. No explicit colors used.
    """
    counts: Dict[datetime, int] = Counter()

    for r in rows:
        ds = r.get("date")
        if not ds:
            continue
        try:
            dt = datetime.fromisoformat(ds.replace("Z", "+00:00")).date()
            counts[datetime(dt.year, dt.month, dt.day)] += 1
        except Exception:
            continue

    out_path = out_path or (EXPORTS_DIR / "commits_over_time.png")
    _ensure_parent(out_path)

    plt.figure(figsize=(11, 6.5), dpi=200)
    if not counts:
        plt.title("Commits Over Time (no data)")
        plt.savefig(out_path, bbox_inches="tight")
        plt.close()
        return out_path

    dates = sorted(counts.keys())
    vals = [counts[d] for d in dates]

    plt.plot(dates, vals, marker="o", linewidth=2, markersize=5)
    plt.title("Commits Over Time")
    plt.xlabel("Date")
    plt.ylabel("Commits")

    # Nice date ticks & formatting
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    plt.grid(True, linestyle="--", alpha=0.3)

    # Annotate the max point
    max_idx = max(range(len(vals)), key=lambda i: vals[i])
    plt.annotate(
        f"peak: {vals[max_idx]}",
        xy=(dates[max_idx], vals[max_idx]),
        xytext=(10, 10),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", shrinkA=0, shrinkB=0, lw=1),
    )

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    return out_path


# -------- Top contributors (horizontal bar) --------
def top_contributors(contribs: Iterable[Dict], k: int = 10, out_path: Optional[Path] = None) -> Path:
    """
    Horizontal bar chart of top-k contributors. Sorted, value labels, grid.
    """
    contribs = list(contribs)
    contribs.sort(key=lambda x: x.get("contributions", 0), reverse=True)
    subset = contribs[:k]

    labels = [c.get("login") or "unknown" for c in subset]
    values = [int(c.get("contributions") or 0) for c in subset]

    out_path = out_path or (EXPORTS_DIR / "top_contributors.png")
    _ensure_parent(out_path)

    plt.figure(figsize=(11, 6.5), dpi=200)
    if not labels:
        plt.title("Top Contributors (no data)")
        plt.savefig(out_path, bbox_inches="tight")
        plt.close()
        return out_path

    # Horizontal bars for readability with long labels
    y_pos = list(range(len(labels)))
    plt.barh(y_pos, values)
    plt.yticks(y_pos, labels)
    plt.gca().invert_yaxis()  # largest on top
    plt.title(f"Top {len(labels)} Contributors")
    plt.xlabel("Contributions")
    plt.grid(axis="x", linestyle="--", alpha=0.3)

    # Value labels at bar ends
    for i, v in enumerate(values):
        plt.text(v, i, f" {v}", va="center")

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    return out_path


# -------- Language share (smart pie) --------
def language_share(languages: Dict[str, int], out_path: Optional[Path] = None, top_n: int = 8) -> Path:
    """
    Pie chart of language bytes. Collapses minor languages into 'Other', adds
    percentages, equal aspect, and clean layout.
    """
    out_path = out_path or (EXPORTS_DIR / "language_share.png")
    _ensure_parent(out_path)

    plt.figure(figsize=(8.5, 8.5), dpi=200)

    if not languages:
        plt.title("Language Share (no data)")
        plt.savefig(out_path, bbox_inches="tight")
        plt.close()
        return out_path

    # Sort & collapse into "Other" for readability
    items = sorted(languages.items(), key=lambda kv: kv[1], reverse=True)
    top = items[:top_n]
    other_sum = sum(v for _, v in items[top_n:])
    if other_sum > 0:
        top.append(("Other", other_sum))

    labels = [k for k, _ in top]
    sizes = [int(v) for _, v in top]

    # Small explode on largest slice (purely visual, no specific colors)
    explode = [0.08] + [0] * (len(sizes) - 1)

    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        explode=explode,
        pctdistance=0.8,
    )
    plt.title("Language Share")
    plt.gca().set_aspect("equal")  # perfect circle

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    return out_path
