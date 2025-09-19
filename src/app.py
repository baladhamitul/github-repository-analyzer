from __future__ import annotations

import argparse
from src.controller import AppController

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="GitHub Repository Analyzer")
    p.add_argument("repo", nargs="?", default="pandas-dev/pandas",
                   help="owner/repo (default: pandas-dev/pandas)")
    p.add_argument("--since", help="ISO date/time (e.g. 2025-08-01 or 2025-08-01T00:00:00Z)")
    p.add_argument("--until", help="ISO date/time")
    p.add_argument("--msg", help="regex for commit message")
    p.add_argument("--author", help="regex for author name/email/login")
    p.add_argument("--path", help="regex for file path (becomes active once commit-file fetch is added)")
    p.add_argument("--charts", action="store_true", help="render charts (PNG) into data/exports/")
    p.add_argument("--gui", action="store_true", help="launch minimal Tkinter GUI")
    return p.parse_args()

def main():
    args = parse_args()
    if args.gui:
        from src.ui.widgets import launch_gui
        launch_gui()
        return
    print("🔍 GitHub Repository Analyzer starting...")
    AppController().run_with_args(args)

if __name__ == "__main__":
    main()
