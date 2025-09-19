# GitHub Repository Analyzer

A Python application to analyze GitHub repositories: commits, contributors, languages, and activity — with regex filters and exportable reports.

Author: **Mitul Mukeshbhai Baladha**

---

## ✨ Features
- Connects to the GitHub REST API (with optional Personal Access Token).
- Fetches and exports:
  - Repository metadata (stars, forks, languages).
  - Commits (with regex filtering for messages and authors).
  - Contributors (sorted by contributions).
- Exports results as **CSV** in `data/exports/`.
- Caches raw API responses in `data/cache/`.
- CLI interface with options for repo, date range, and filters.

---

## 📦 Project Structure
```

repo-analyzer/
├─ src/                 # main code
│  ├─ app.py            # entry point (CLI)
│  ├─ controller.py     # orchestrates analysis
│  ├─ github\_client.py  # GitHub API wrapper
│  ├─ analyzer.py       # RepoAnalyzer logic
│  ├─ filters.py        # regex filtering
│  ├─ util.py           # helpers (caching, CSV)
│  └─ ...               # (future: reports, gui, tests)
├─ data/
│  ├─ cache/            # cached raw API responses
│  └─ exports/          # generated CSVs
├─ .env.example         # sample environment file
├─ requirements.txt     # dependencies
├─ pyproject.toml       # config (pytest etc.)
├─ README.md            # project docs
└─ LICENSE              # MIT License

````

---

## 🚀 Quickstart

### 1. Clone and enter the project
```bash
git clone https://github.com/your-username/repo-analyzer.git
cd repo-analyzer
````

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get a GitHub Token

Without authentication, GitHub only allows \~60 requests/hour per IP, which is too low for analyzing busy repos.
With a **Personal Access Token (PAT)**, you get up to 5000 requests/hour.

Steps:

1. Log in to [GitHub](https://github.com/).
2. Go to **Settings → Developer settings → Personal access tokens**.

   * Classic: **Tokens (classic)** → *Generate new token (classic)*.
   * Fine-grained: **Fine-grained tokens** → *Generate new token*.
3. Select:

   * **Expiration**: choose a safe expiry (30–90 days is fine).
   * **Access**:

     * For public repos, select **Public repositories** only.
     * Permissions: `Metadata (Read)` and `Contents (Read)` are enough.
4. Generate and copy the token (`ghp_...` string).

⚠️ Keep your token secret — don’t commit it to GitHub!

### 5. Configure token in `.env`

```bash
cp .env.example .env
```

Edit `.env` and add your token:

```
GITHUB_TOKEN=ghp_your_token_here
```

---

## 🛠 Usage

Run the analyzer with:

```bash
python -m src.app [owner/repo] [options]
```

### Examples

* Analyze default repo (`pandas-dev/pandas`, last 30 days):

```bash
python -m src.app
```

* Custom repo with time window:

```bash
python -m src.app matplotlib/matplotlib --since 2025-08-01 --until 2025-09-06T23:59:59Z
```

* Filter commits by message (regex: fix/bug/hotfix):

```bash
python -m src.app pandas-dev/pandas --since 2025-08-01 --msg "fix|bug|hotfix"
```

* Filter commits by author name/email/login:

```bash
python -m src.app pandas-dev/pandas --since 2025-08-01 --author "joris|wes"
```

---

## 📂 Outputs

Exports are written to `data/exports/`:

* `*_commits.csv` → all commits in the window.
* `*_commits_filtered.csv` → commits matching regex filters.
* `*_contributors.csv` → contributors list with contributions count.
* `*_languages.csv` → languages used in the repo.

---

## 🔧 Development Notes

* **Caching**: raw API pages saved in `data/cache/owner_repo/`.
* **Pagination**: fetches up to 100 items per page, follows `Link` headers automatically.
* **Error handling**: warns when rate limits hit; instructs to use `GITHUB_TOKEN`.
* **Extensible**: designed to add charts (`reports.py`) and GUI later.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👤 Author

**Mitul Mukeshbhai Baladha**
Master of engineering in Computer Science student at Gisma University of Applied Sciences