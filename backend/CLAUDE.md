# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI-based APK malware analysis tool. Accepts an uploaded APK, extracts metadata with Androguard, and runs it through several independent heuristic scorers plus a malware-family fingerprint matcher. A second-stage GenAI layer (4 sequential Groq LLM agents) turns the raw heuristic output into a triage classification, plain-English analyst writeup, final risk verdict, and a formal PDF investigation report. The full JSON contract for `/analyze` is documented in `API_CONTRACT.md`.

## Commands

```bash
# Run the dev server (Windows venv)
./venv/Scripts/python.exe -m uvicorn main:app --reload

# Run the matcher's standalone smoke test
./venv/Scripts/python.exe app/fingerprints/test_matcher.py

# Build the hand-crafted test APK (com.boi.update.security / "BOI Bank Update")
./venv/Scripts/python.exe create_test_apk.py

# Hit the running server with a sample APK and pretty-print the response
./venv/Scripts/python.exe test_analyze.py <path-to-apk>

# Install/update deps
./venv/Scripts/python.exe -m pip install -r requirements.txt
```

**Important:** `uvicorn` must be restarted (or run with `--reload`) after editing `main.py` or any `app/ai/*` module — a stale process serving old code is a common source of "it worked in code but not via the endpoint" confusion.

## Architecture

### Heuristic pipeline (`POST /analyze`)

Runs synchronously per request:

1. **Validate & save** — reject non-`.apk` filenames and files over 100MB; write upload to a uuid-prefixed temp file (always cleaned up in a `finally` block).
2. **Extract** (`app/extraction/extractor.py::extract_apk_info`) — runs Androguard's `AnalyzeAPK` to pull `package_name`, `app_name`, `permissions`, `activities`/`services`/`receivers`, signing `certificates`, and `urls_and_ips` (regex-scanned from DEX strings). Any exception here is caught and returned as `400 Invalid or corrupted APK file`.
3. **Score** — three independent scorers, each consuming a slice of the extracted data and returning their own dict:
   - `app/scoring/heuristics.py::score_permissions` — `permission_risk_score` from `RISKY_PERMISSIONS` point table + `COMBO_RULES` (e.g. the READ_SMS+RECEIVE_BOOT_COMPLETED+SEND_SMS OTP-stealer combo).
   - `app/scoring/impersonation.py::check_impersonation` — `impersonation_risk_score` from `BANKING_KEYWORDS` in the app label vs. `KNOWN_PACKAGE_PREFIXES`/`SUSPICIOUS_PACKAGE_SUFFIXES` in the package name.
   - `app/scoring/network_risk.py::check_network_risk` — `network_risk_score` from `SUSPICIOUS_TLDS`, raw-IP endpoints, and non-HTTPS URLs.
4. **Fingerprint match** (`app/fingerprints/matcher.py::match_fingerprints`) — loads `app/fingerprints/db.json` once at module import. For each known family, combines Jaccard similarity of permission sets (weight 0.5), package-name regex match (0.3), and C2-URL regex match (0.2) into a single confidence score; below 20% confidence returns `matched_family: "No significant match"`.
5. All five results (`info`, `risk`, `impersonation`, `network_risk`, `fingerprint_match`) are merged into one JSON response — see `API_CONTRACT.md` for the exact schema.

Each scorer/matcher module is self-contained (own constants/tables, no shared state) and is wired into `main.py` only at the final assembly step — add new heuristics by creating a new module under `app/scoring/` and merging its output dict into the `/analyze` response.

To extend the fingerprint database, edit `app/fingerprints/db.json` (array of `{family_name, description, typical_permissions, package_name_patterns, known_c2_patterns, source_reference}`) — no code changes needed.

### GenAI layer (`app/ai/`)

`app/ai/config.py` loads `GROQ_API_KEY` from `.env` (via `python-dotenv`) and exports a shared `groq_client`. All agents use model `llama-3.3-70b-versatile` (the originally-specified `llama-3.1-70b-versatile` is decommissioned on Groq — do not revert to it).

Each agent module (`agent1_triage.py`, `agent2_analyst.py`, `agent3_synthesizer.py`, `agent4_reporter.py`) follows the same shape:
- A `SYSTEM_PROMPT` + `USER_PROMPT_TEMPLATE` instructing the model to return raw JSON only (no markdown/backticks).
- A `_call_groq(...)` helper that retries up to 3 times with `time.sleep(5)` between attempts if Groq raises `groq.RateLimitError` (429).
- A `run_*_agent(...)` function that calls `_call_groq`, `json.loads()`s the response, retries once with an "IMPORTANT: respond with raw JSON only" suffix if parsing fails, and falls back to a hardcoded default dict (with an `"error"` key) if both attempts fail.

`app/ai/pipeline.py::run_full_ai_pipeline(analysis_json)` chains all four agents in sequence (each consumes the prior agents' outputs), printing progress after each stage with a `time.sleep(3)` pause between agent calls to avoid 429s, and returns a combined dict: `{triage, analysis, risk_assessment, report, final_risk_score, risk_level}`.

`app/ai/pdf_generator.py::generate_pdf_report(full_pipeline_result, output_path)` renders the agent-4 report into a formatted PDF (reportlab) with a color-coded risk banner (red/orange/yellow/green by `risk_level`). Note the top-of-file `hashlib.md5` monkeypatch — required because this environment's OpenSSL build rejects reportlab's `usedforsecurity=` kwarg; keep it if reportlab is touched.

### Full pipeline endpoints (`main.py`)

- `POST /analyze/full` — runs the heuristic pipeline above, then `run_full_ai_pipeline`, merges everything into one response (~15-30s due to 4 sequential Groq calls), stores the result in the in-memory `ANALYSIS_RESULTS` dict keyed by filename, and writes the PDF to `generated_reports/{filename}_report.pdf`.
- `GET /reports` — lists every `*_report.pdf` in `generated_reports/` (persists across restarts), enriched with `risk_level`/`final_risk_score` from `ANALYSIS_RESULTS` when available (in-memory, so resets on restart).
- `GET /report/{filename}` — serves `generated_reports/{filename}_report.pdf` if present, else regenerates it from `ANALYSIS_RESULTS` (404 if neither exists).

`generated_reports/` is gitignored (regenerable artifacts).
