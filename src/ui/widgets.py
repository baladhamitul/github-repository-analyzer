from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

from types import SimpleNamespace
from src.controller import AppController


def launch_gui():
    app = tk.Tk()
    app.title("GitHub Repository Analyzer")
    app.geometry("560x360")

    frm = ttk.Frame(app, padding=12)
    frm.pack(fill="both", expand=True)

    # Inputs
    repo_var = tk.StringVar(value="pandas-dev/pandas")
    since_var = tk.StringVar()
    until_var = tk.StringVar()
    msg_var = tk.StringVar()
    author_var = tk.StringVar()
    charts_var = tk.BooleanVar(value=True)

    def row(label, var, row_i):
        ttk.Label(frm, text=label).grid(column=0, row=row_i, sticky="w", pady=4)
        e = ttk.Entry(frm, textvariable=var, width=50)
        e.grid(column=1, row=row_i, sticky="we", pady=4)
        return e

    app.grid_columnconfigure(1, weight=1)
    frm.grid_columnconfigure(1, weight=1)

    row("owner/repo", repo_var, 0)
    row("since (ISO)", since_var, 1)
    row("until (ISO)", until_var, 2)
    row("message regex", msg_var, 3)
    row("author regex", author_var, 4)
    ttk.Checkbutton(frm, text="Render charts", variable=charts_var).grid(column=1, row=5, sticky="w", pady=4)

    out_text = tk.Text(frm, height=8)
    out_text.grid(column=0, row=7, columnspan=2, sticky="nsew", pady=8)
    frm.grid_rowconfigure(7, weight=1)

    ctrl = AppController()

    def analyze():
        out_text.delete("1.0", tk.END)
        args = SimpleNamespace(
            repo=repo_var.get().strip(),
            since=since_var.get().strip() or None,
            until=until_var.get().strip() or None,
            msg=msg_var.get().strip() or None,
            author=author_var.get().strip() or None,
            path=None,        # future
            charts=charts_var.get(),
            gui=False,
        )
        try:
            # Capture prints by temporarily redirecting stdout? Keep it simple: run and inform user
            ctrl.run_with_args(args)
            out_text.insert(tk.END, "Done. Check data/exports/ for outputs.\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn = ttk.Button(frm, text="Analyze", command=analyze)
    btn.grid(column=1, row=6, sticky="e", pady=6)

    app.mainloop()
