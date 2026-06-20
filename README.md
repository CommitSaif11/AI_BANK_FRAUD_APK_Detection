# ThreatLens — AI-Powered APK Malware Analysis Platform

**ThreatLens** is a full-stack APK malware analysis platform that combines static reverse engineering, multi-layer heuristic scoring, malware family fingerprinting, and a 4-agent AI pipeline to produce comprehensive threat intelligence reports. Built for the **Bank of India**, **Department of Financial Services**, and **IIT Hyderabad**.

Upload any `.apk` file and ThreatLens will:

1. **Reverse engineer** the APK using apktool and JADX to extract decompiled Java source code.
2. **Extract metadata** (permissions, activities, services, receivers, certificates, embedded URLs/IPs) with Androguard.
3. **Score risk heuristics** across three independent dimensions — permission abuse, bank impersonation, and network indicators — and match against a database of known malware families.
4. **Extract suspicious code snippets** from decompiled source, scanning for keywords like `sms`, `keylog`, `steal`, `overlay`, `credential`, `bank`, `otp`, and more.
5. **Run a 4-agent Groq LLM pipeline** (Triage → Analyst → Synthesizer → Reporter) using real decompiled code and heuristic data to produce a plain-English threat assessment.
6. **Generate a formal PDF investigation report** with color-coded risk banners, IOCs, executive summary, and customer advisory.

---

## Table of Contents

- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#1-clone-the-repository)
  - [Clone the Repository](#1-clone-the-repository)
  - [Backend Setup](#2-backend-setup-fastapi)
  - [Frontend Setup](#3-frontend-setup-react--vite)
- [Using the App](#4-using-the-app)
- [API Endpoints](#5-api-endpoints)
- [Architecture](#6-architecture)
  - [Heuristic Pipeline](#heuristic-pipeline)
  - [AI Pipeline (4-Agent System)](#ai-pipeline-4-agent-system)
  - [Malware Family Fingerprinting](#malware-family-fingerprinting)
  - [PDF Report Generation](#pdf-report-generation)
- [Project Structure](#7-project-structure)
- [Frontend Details](#8-frontend-details)
- [Configuration Reference](#9-configuration-reference)
- [Common Issues & Troubleshooting](#10-common-issues--troubleshooting)
- [Building for Production](#11-building-for-production)

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI | REST API with async request handling |
| Runtime | Python 3.10+ (3.11 recommended) | Core backend runtime |
| APK Analysis | Androguard 4.0.1 | Permission, manifest, and certificate extraction |
| Reverse Engineering | apktool + JADX | Bytecode decompilation to Java source |
| AI Engine | Groq SDK (`llama-3.3-70b-versatile`) | 4-agent threat intelligence pipeline |
| PDF Generation | ReportLab | Formal investigation report rendering |
| Server | Uvicorn | ASGI application server |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 19 | UI components and state management |
| Build Tool | Vite 8 | Development server and production bundling |
| HTTP Client | Axios | REST API communication |
| Styling | Custom CSS3 | Dark-mode design system with animations |

---

## Prerequisites

Make sure these are installed before you start:

| Tool | Version | Check with |
|------|---------|------------|
| Python | 3.10+ (3.11 recommended) | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | comes with Node | `npm --version` |
| Java | JDK 8+ (required for apktool & JADX) | `java -version` |
| Git | any recent version | `git --version` |

You will also need a **free Groq API key** for the AI pipeline — get one at [console.groq.com](https://console.groq.com/keys).

---

## 1. Clone the repository

```bash
git clone https://github.com/CommitSaif11/AI_BANK_FRAUD_APK_Detection.git
cd bank_fraud_apk_detection
```

---

## 2. Backend setup (FastAPI)

### 2.0 Install analysis tools (required)

The backend requires `apktool` and `jadx` to reverse engineer APKs. **These are NOT included in the repository** and must be downloaded manually.

1. Create a `backend/tools/` folder (if it doesn't exist).
2. Download `apktool` from [apktool.org](https://apktool.org/) and rename the JAR file to `apktool.jar`. Place it in `backend/tools/`.
3. Download the `jadx-1.5.5.zip` (or newer) release from [skylot/jadx](https://github.com/skylot/jadx/releases), extract it, and place the contents in `backend/tools/jadx/`.

Your `backend/tools/` directory should look like:
```
backend/tools/
├── apktool.jar
└── jadx/
    ├── bin/
    │   ├── jadx
    │   └── jadx.bat
    └── lib/
        └── ...
```

### 2.1 Create and activate a virtual environment

From the project root:

```bash
cd backend
python -m venv venv
```

Activate it:

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (cmd):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

Your prompt should now show `(venv)` at the start of the line.

### 2.2 Install dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, Androguard, the Groq SDK, ReportLab (PDF generation), and all other dependencies (~58 packages total).

### 2.3 Configure environment variables

Create or edit `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> **Warning:** Never commit your real `GROQ_API_KEY` to git. If a real key was ever committed, rotate it immediately in the [Groq console](https://console.groq.com/keys).

### 2.4 Run the backend dev server

```bash
uvicorn main:app --reload
```

You should see:

```
INFO:     Will watch for changes in these directories: ['...\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
Groq client initialized successfully
INFO:     Application startup complete.
```

The backend is now running at **http://localhost:8000**.

### 2.5 Verify the backend works

In a second terminal:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok"}
```

You can also run the included test APK against the full pipeline:

```bash
python test_analyze.py test_malicious.apk
```

---

## 3. Frontend setup (React + Vite)

Open a **new terminal** (keep the backend running in the first one).

### 3.1 Install dependencies

```bash
cd frontend
npm install
```

### 3.2 Configure environment variables

The frontend reads the backend URL from `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

This file is already committed with the correct value for local development — no changes needed unless your backend runs on a different host/port.

### 3.3 Run the frontend dev server

```bash
npm run dev
```

You should see:

```
  VITE ready in ~250 ms
  ➜  Local:   http://localhost:5173/
```

Open that URL in your browser.

---

## 4. Using the app

### User journey

1. **Splash screen (3 seconds)** — An animated intro displays the ThreatLens logo alongside partner logos (Bank of India, IIT Hyderabad, DFS).

2. **Upload page** — The main landing page with:
   - A **drag-and-drop zone** (or click to browse) for uploading `.apk` files (max 100 MB).
   - A **"Try Demo" button** that loads a pre-bundled malicious test APK (`test_malicious.apk`) directly from the browser — no file needed. This lets you see the full analysis pipeline in action immediately.
   - A **"How it works"** section showing the 4-step analysis flow with animated step indicators.
   - **Stats counters** (15+ permissions tracked, 5 malware families, 4 AI agents, 98/100 max risk score).
   - **Feature cards** describing each analysis capability (Static Analysis, Heuristic Scoring, 4-Agent AI Pipeline, PDF Reports).

3. **Loading page (~15-30 seconds)** — While the backend processes the APK:
   - A spinning loader with the uploaded filename displayed.
   - A **progress bar** that fills over ~25 seconds.
   - **4 agent status cards** that update in real-time: each agent transitions from pending (gray) → active (blue with pulse animation) → done (green checkmark) as the pipeline progresses.
   - Subtext indicating the current stage (manifest parsing → permission analysis → code decompilation → AI triage → synthesis → report generation).

4. **Results page** — A comprehensive multi-section dashboard:
   - **Header bar:** Filename, "Download PDF Report" button, and "Analyze Another APK" button.
   - **Risk score badge:** Large color-coded score (CRITICAL = red pulse, HIGH = red, MEDIUM = amber, LOW = green) with metadata (package name, app name, threat category, matched malware family).
   - **Agent pipeline strip:** 4-column visualization showing all agents completed (Triage → Code Analyst → Risk Synthesis → Report Writer).
   - **AI Pipeline Breakdown:** 2x2 grid of detailed agent output cards, each with a colored left border and the full output from that agent.
   - **Risk score cards:** Three cards for Permission Risk, Impersonation Risk, and Network Risk, each with a progress bar and numeric score.
   - **Two-column analysis section:**
     - Left: Flagged permissions list with triggered combo badges (e.g., OTP-stealer pattern).
     - Right: Tabbed AI analysis (Threat Analysis, Network Analysis, Impersonation Analysis).
   - **Fingerprint match:** Animated SVG circle showing confidence percentage, matched malware family name, and description.
   - **Executive summary and recommended actions** from the AI pipeline.

5. Click **"Download PDF Report"** to download the formal investigation report as a PDF.

6. Click **"Analyze Another APK"** to reset and upload a different file.

---

## 5. API Endpoints

| Endpoint | Method | Description | Response Time |
|----------|--------|-------------|---------------|
| `/health` | GET | Liveness check — returns `{"status": "ok"}` | Instant |
| `/analyze` | POST | Heuristic analysis only (steps 1-3). Returns risk scoring, flagged permissions, and fingerprint matches. | 1-2 seconds |
| `/analyze/full` | POST | Full pipeline (steps 1-6) including AI analysis and PDF generation. | 15-30 seconds |
| `/reports` | GET | List all generated PDF report filenames. | Instant |
| `/report/{filename}` | GET | Download a generated PDF report. Generates on-demand if not cached. | 2-5 seconds |

### Request format

Both `/analyze` and `/analyze/full` accept a `multipart/form-data` POST with a single `file` field containing the `.apk` file.

### Response format (`/analyze/full`)

```json
{
  "filename": "suspicious_app.apk",
  "size": 1048576,
  "package_name": "com.example.app",
  "app_name": "Example App",
  "permissions": ["android.permission.READ_SMS", "..."],
  "activities": ["..."],
  "services": ["..."],
  "receivers": ["..."],
  "certificates": [{"issuer": "...", "subject": "..."}],
  "urls_and_ips": ["http://malicious.top/api"],
  "risk": {
    "permission_risk_score": 65,
    "flagged_permissions": ["READ_SMS", "BIND_ACCESSIBILITY_SERVICE"],
    "triggered_combos": ["OTP-stealer: READ_SMS + RECEIVE_BOOT_COMPLETED + SEND_SMS"]
  },
  "impersonation": {
    "impersonation_risk_score": 40,
    "reasons": ["Package name contains banking keyword 'sbi'"]
  },
  "network_risk": {
    "network_risk_score": 25,
    "flagged_urls": ["http://malicious.top/api (suspicious TLD .top)"]
  },
  "fingerprint_match": {
    "matched_family": "Brata",
    "confidence": 72.5,
    "matched_permission_overlap": ["BIND_ACCESSIBILITY_SERVICE", "READ_SMS"],
    "description": "Spyware and wiper targeting Brazilian and Italian banks"
  },
  "ai_analysis": {
    "triage": {
      "threat_category": "Banking Trojan",
      "investigation_priority": "CRITICAL",
      "primary_threat_vector": "SMS interception + credential overlay",
      "target_victim_profile": "Online banking users",
      "triage_summary": "..."
    },
    "analysis": {
      "permission_analysis": "...",
      "network_analysis": "...",
      "behavioral_pattern": "...",
      "banking_impact": "...",
      "impersonation_analysis": "...",
      "technical_indicators": "..."
    },
    "risk_assessment": {
      "final_risk_score": 92,
      "risk_level": "CRITICAL",
      "verdict": "...",
      "recommended_actions": ["..."],
      "customer_advisory": "..."
    },
    "report": {
      "report_title": "...",
      "executive_summary": "...",
      "threat_overview": "...",
      "indicators_of_compromise": "...",
      "customer_communication": "..."
    }
  }
}
```

---

## 6. Architecture

### Heuristic Pipeline

When an APK is uploaded, three independent scorers evaluate it:

**Permission Risk Scorer** (`app/scoring/heuristics.py`)
- Checks 8 high-risk Android permissions, each with a weighted point value:
  - `READ_SMS` (15 pts), `RECEIVE_SMS` (15 pts), `SEND_SMS` (10 pts)
  - `BIND_ACCESSIBILITY_SERVICE` (25 pts), `SYSTEM_ALERT_WINDOW` (20 pts)
  - `REQUEST_INSTALL_PACKAGES` (15 pts), `RECEIVE_BOOT_COMPLETED` (10 pts)
  - `READ_CONTACTS` (10 pts)
- Detects combo patterns: the **OTP-stealer** rule adds +25 points if the APK requests `READ_SMS` + `RECEIVE_BOOT_COMPLETED` + `SEND_SMS` together.

**Impersonation Scorer** (`app/scoring/impersonation.py`)
- Checks app labels against banking keywords (`sbi`, `hdfc`, `bank`, `upi`, `pay`, etc.).
- Matches package names against known official banking package prefixes (`com.sbi`, `com.csam.icici`, etc.).
- Flags suspicious suffixes (`update`, `security`, `verify`, `install`, `latest`).
- Detects random/generic package name segments via regex.

**Network Risk Scorer** (`app/scoring/network_risk.py`)
- Flags HTTP (non-HTTPS) URLs (+10 pts each).
- Flags raw IP address endpoints (+15 pts each).
- Flags suspicious TLDs: `.tk`, `.xyz`, `.top`, `.ml`, `.ga`, `.cf`, `.gq` (+15 pts each).

### AI Pipeline (4-Agent System)

After heuristic scoring, the full pipeline runs four specialized Groq LLM agents sequentially, each receiving the outputs of all prior agents plus the raw APK data and decompiled code snippets:

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Agent 1: Triage** | Quick threat classification and priority assignment | APK metadata + heuristic scores + code snippets | `threat_category`, `investigation_priority`, `primary_threat_vector`, `target_victim_profile`, `triage_summary` |
| **Agent 2: Analyst** | Deep behavioral analysis using decompiled code | APK data + triage result + code snippets | `permission_analysis`, `network_analysis`, `behavioral_pattern`, `banking_impact`, `impersonation_analysis`, `technical_indicators` |
| **Agent 3: Synthesizer** | Risk score synthesis and verdict | All prior outputs + heuristic scores | `final_risk_score` (0-100), `risk_level` (CRITICAL/HIGH/MEDIUM/LOW/CLEAN), `verdict`, `recommended_actions`, `customer_advisory` |
| **Agent 4: Reporter** | Formal investigation report writing | All prior outputs | `report_title`, `executive_summary`, `threat_overview`, `indicators_of_compromise`, `customer_communication` |

Each agent call includes:
- **3 retry attempts** with 5-second backoff on Groq rate-limit (429) errors.
- **3-second pause** between agents to avoid cascading rate limits.
- **JSON parsing fallback** — if the LLM returns invalid JSON, a retry is attempted with a "raw JSON only" prompt suffix, then a fallback dict with an `"error"` key is returned.

All agents use the `llama-3.3-70b-versatile` model via Groq.

### Malware Family Fingerprinting

The fingerprint matcher (`app/fingerprints/matcher.py`) compares the APK against 5 known malware families stored in `app/fingerprints/db.json`:

| Family | Type | Key Indicators |
|--------|------|----------------|
| **Anatsa** | Banking trojan | Accessibility abuse, package installer requests, scanner/cleaner app disguise |
| **SOVA** | Banking trojan (overlay) | SMS interception, boot persistence, Chrome/update impersonation |
| **FluBot** | SMS worm/spreader | Contact harvesting, SMS sending, voicemail/shipping app disguise |
| **TeaBot** | Credential stealer | Accessibility abuse, overlay attacks, QR/VPN app disguise |
| **Brata** | Spyware + wiper | Location tracking, camera access, security/WhatsApp impersonation |

Matching uses a **weighted Jaccard similarity** algorithm:
- Permission overlap: **0.5 weight**
- Package name regex match: **0.3 weight**
- C2 URL pattern regex match: **0.2 weight**

A confidence score below 20% is reported as "No significant match."

### PDF Report Generation

The PDF generator (`app/ai/pdf_generator.py`) renders the Agent 4 output into a formal investigation report using ReportLab:
- Color-coded risk banner (red for CRITICAL/HIGH, amber for MEDIUM, green for LOW).
- Sections: Executive Summary, Threat Overview, Technical Findings, Indicators of Compromise, Customer Communication.
- Reports are saved to `backend/generated_reports/` and served via `GET /report/{filename}`.

---

## 7. Project Structure

```
bank_fraud_apk_detection/
├── backend/
│   ├── main.py                     # FastAPI app: CORS config, all endpoints
│   ├── requirements.txt            # Python dependencies (~58 packages)
│   ├── .env                        # GROQ_API_KEY (not committed with real secrets)
│   ├── test_analyze.py             # CLI test script for the analysis pipeline
│   ├── test_malicious.apk          # Sample malicious APK for testing
│   ├── tools/                      # External tools (manually downloaded, gitignored)
│   │   ├── apktool.jar
│   │   └── jadx/
│   ├── app/
│   │   ├── extraction/
│   │   │   ├── extractor.py        # Androguard-based metadata extraction
│   │   │   ├── reverse_engineer.py # apktool + JADX subprocess orchestration
│   │   │   └── code_extractor.py   # Suspicious keyword scanner for decompiled Java
│   │   ├── scoring/
│   │   │   ├── heuristics.py       # Permission risk scoring + combo rules
│   │   │   ├── impersonation.py    # Banking impersonation detection
│   │   │   └── network_risk.py     # URL/IP/TLD risk analysis
│   │   ├── fingerprints/
│   │   │   ├── db.json             # 5 malware family signatures
│   │   │   └── matcher.py          # Weighted Jaccard fingerprint matching
│   │   └── ai/
│   │       ├── config.py           # Groq client initialization + model config
│   │       ├── pipeline.py         # 4-agent orchestration (sequential with rate-limit pacing)
│   │       ├── agent1_triage.py    # Threat classification and priority
│   │       ├── agent2_analyst.py   # Behavioral deep-dive analysis
│   │       ├── agent3_synthesizer.py # Risk score synthesis and verdict
│   │       ├── agent4_reporter.py  # Formal report generation
│   │       └── pdf_generator.py    # ReportLab PDF rendering
│   └── generated_reports/          # PDF output directory (gitignored)
├── frontend/
│   ├── index.html                  # HTML entry point
│   ├── package.json                # React 19, Axios, Vite 8
│   ├── vite.config.js              # Dev proxy (/api → localhost:8000)
│   ├── .env                        # VITE_API_URL=http://localhost:8000
│   ├── public/
│   │   ├── test_malicious.apk      # Demo APK served to browser for "Try Demo" button
│   │   ├── favicon.svg             # ThreatLens favicon
│   │   └── icons.svg               # Partner/feature icons
│   └── src/
│       ├── main.jsx                # React entry point
│       ├── App.jsx                 # App state machine, page routing, API calls
│       ├── index.css               # Design system: CSS variables, animations, responsive
│       ├── components/
│       │   ├── SplashScreen.jsx    # Animated 3-second intro with partner logos
│       │   ├── Navbar.jsx          # Fixed top bar with ThreatLens branding
│       │   └── Footer.jsx          # Fixed bottom bar with credits and copyright
│       └── pages/
│           ├── UploadPage.jsx      # Drag-drop zone, demo button, feature cards, stats
│           ├── LoadingPage.jsx     # Spinner, progress bar, agent status cards
│           └── ResultsPage.jsx    # Full results dashboard (7 sections)
└── README.md
```

---

## 8. Frontend Details

### Component hierarchy

```
App.jsx (state: page, selectedFile, analysisData, error, loadingStep)
├── SplashScreen (3-sec animated intro, auto-dismisses)
├── Navbar (fixed top bar: ThreatLens logo + "4-Agent AI Pipeline" badge)
├── Page transitions (fade-in/out)
│   ├── UploadPage
│   │   ├── Stats bar (4 animated counters)
│   │   ├── Hero grid (2-column desktop, stacked mobile)
│   │   │   ├── Left: heading, description, "How it works" 4-step flow
│   │   │   └── Right: drag-drop upload zone + "Try Demo" button
│   │   └── Feature cards (4-card grid)
│   ├── LoadingPage
│   │   ├── Filename display + spinner
│   │   ├── Stage subtext (6 loading stages)
│   │   ├── Agent status cards (4-card grid: pending → active → done)
│   │   └── Progress bar (animated 95% fill over 25s)
│   └── ResultsPage
│       ├── Header (filename + PDF download + reset)
│       ├── Risk score badge + metadata
│       ├── Agent pipeline status strip
│       ├── AI Pipeline Breakdown (2x2 agent detail cards)
│       ├── Risk score cards (3: permission, impersonation, network)
│       ├── Two-column: flagged permissions + tabbed AI analysis
│       ├── Fingerprint match (animated SVG circle + family info)
│       └── Executive summary + recommended actions
└── Footer (fixed bottom bar: credits + copyright)
```

### State management

The app uses React state in `App.jsx` with a simple page-based state machine:

| State | Type | Purpose |
|-------|------|---------|
| `showSplash` | boolean | Controls splash screen visibility (auto-hides after 3s) |
| `page` | string | Current page: `"upload"`, `"loading"`, or `"results"` |
| `selectedFile` | File | The APK file object (from input, drag-drop, or demo fetch) |
| `analysisData` | object | Full API response from `/analyze/full` |
| `error` | string | Error message to display on the upload page |
| `loadingStep` | number | 0-5, increments every 4s to drive loading stage text |
| `visible` | boolean | Page fade-in/out animation control |

### Design system

The frontend uses a custom dark-mode CSS design system defined in `index.css`:

```css
--bg-primary: #0a0e1a     /* Deep navy background */
--bg-secondary: #0f1628   /* Slightly lighter navy */
--bg-card: rgba(255,255,255,0.03)  /* Translucent card surfaces */
--text-primary: #f1f5f9   /* Near-white text */
--text-secondary: #94a3b8 /* Muted gray text */
--blue: #3b82f6            /* Primary accent */
--red: #ef4444             /* Critical/high risk */
--amber: #f59e0b           /* Medium risk */
--green: #22c55e           /* Low risk / success */
```

Key animations:
- `fadeInUp` — Elements slide up and fade in (0.6s ease).
- `pulse-blue` — Pulsing blue glow on the upload zone.
- `pulseGlowRed` — Pulsing red glow on CRITICAL risk scores.
- `spin` — Rotating spinner on the loading page.
- `slideInRight` — Right-slide entrance animation.

Responsive breakpoint at 900px — grids stack to single column on mobile.

---

## 9. Configuration Reference

### Backend environment (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Your Groq API key for the LLM pipeline |

### Frontend environment (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

### CORS configuration

The backend allows all origins for development and internal deployment:

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers=["*"]
```

---

## 10. Common issues & troubleshooting

**Backend won't start / "Fatal error in launcher"**
The virtual environment's executables may have a broken path (e.g., after moving the project folder). Fix:
```bash
.\venv\Scripts\python.exe -m pip install --force-reinstall --no-deps uvicorn
```

**Frontend shows "Analysis failed. Make sure the backend is running."**
- Confirm the backend terminal shows `Application startup complete.` and is listening on port 8000.
- Confirm `frontend/.env` has `VITE_API_URL=http://localhost:8000`.
- Check the backend terminal for errors — a 400 means the APK is invalid/corrupted.

**CORS errors in the browser console**
The backend has CORS middleware enabled for all origins (`main.py`). If you still see CORS errors, restart uvicorn after any `main.py` change — `--reload` sometimes doesn't pick up middleware changes cleanly.

**429 / rate limit errors from Groq**
The AI pipeline includes retry-with-backoff (3 attempts, 5s wait) and a 3-second pause between each of the 4 agents. If you still hit limits consistently:
- Your Groq account/tier may need a higher rate limit.
- You can switch the model in `app/ai/config.py` to a smaller model (e.g., `llama3-8b-8192`).

**"No analysis data available." on results page**
This means `analysisData` is `null` — usually caused by the API call failing silently. Check the browser console and backend terminal for the actual error.

**apktool or JADX not found**
Make sure `backend/tools/apktool.jar` and `backend/tools/jadx/bin/jadx` (or `jadx.bat` on Windows) exist. These must be downloaded manually — see [section 2.0](#20-install-analysis-tools-required).

**Java not found**
Both apktool and JADX require Java (JDK 8+). Verify with `java -version`. On Windows, ensure `JAVA_HOME` is set and Java is in your `PATH`.

---

## 11. Building for production

### Frontend

```bash
cd frontend
npm run build
```

Output goes to `frontend/dist/`. Set `VITE_API_URL` to your deployed backend URL before building:
- Via a `frontend/.env.production` file, or
- Via your hosting provider's environment variable settings.

The `dist/` folder contains static files that can be served by any web server (nginx, Apache, Vercel, Netlify, etc.).

### Backend

The backend can be deployed behind Gunicorn/Uvicorn on any cloud provider (EC2, Heroku, Railway, etc.):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Requirements for deployment:
- `backend/tools/apktool.jar` and `backend/tools/jadx/` must be present.
- Java (JDK 8+) must be installed on the server.
- `GROQ_API_KEY` must be set as an environment variable or in `.env`.
- The `backend/generated_reports/` directory must be writable (for PDF output).
