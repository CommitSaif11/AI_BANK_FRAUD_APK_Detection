# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI-based APK malware analysis tool. Accepts an uploaded APK, extracts metadata with Androguard, and runs it through several independent heuristic scorers plus a malware-family fingerprint matcher. The full JSON contract for the main endpoint is documented in `API_CONTRACT.md`.

## Commands

```bash
# Activate venv (Windows)
./venv/Scripts/python.exe -m uvicorn main:app --reload

# Run the matcher's standalone smoke test
./venv/Scripts/python.exe app/fingerprints/test_matcher.py

# Build the hand-crafted test APK (com.sbi.update.security / "SBI Bank Update")
./venv/Scripts/python.exe create_test_apk.py

# Hit the running server with a sample APK and pretty-print the response
./venv/Scripts/python.exe test_analyze.py <path-to-apk>

# Install/update deps
./venv/Scripts/python.exe -m pip install -r requirements.txt
```

## Architecture

`main.py` defines two endpoints: `GET /health` and `POST /analyze`. `/analyze` is a pipeline that runs synchronously per request:

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
