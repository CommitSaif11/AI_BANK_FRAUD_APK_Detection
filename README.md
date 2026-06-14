# ThreatLens

ThreatLens is an APK malware analysis tool built with FastAPI (backend) and React + Vite (frontend). Upload an `.apk` file and it:

1. Reverse engineers the APK (apktool + jadx) to extract decompiled code.
2. Extracts metadata (permissions, certs, URLs/IPs) with Androguard.
3. Scores heuristics (permissions, impersonation, network indicators) and checks fingerprint matches.
4. Extracts suspicious code snippets from the decompiled JADX output.
5. Runs a 4-agent Groq LLM pipeline (Triage, Analysis, Synthesis, Report) using real decompiled code to produce a plain-English risk verdict.
6. Generates a formal PDF investigation report.

### API Endpoints
- `POST /analyze` — Steps 1-3 only. Returns heuristic risk scoring and fingerprint matches in seconds.
- `POST /analyze/full` — All steps (1-6) including the full AI pipeline and code analysis. Takes ~30 seconds.

---

## Prerequisites

Make sure these are installed before you start:

| Tool | Version | Check with |
|---|---|---|
| Python | 3.10+ (3.11 recommended) | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | comes with Node | `npm --version` |
| Java | JDK 8+ (required for apktool & jadx) | `java -version` |
| Git | any recent version | `git --version` |

You will also need a **free Groq API key** for the AI pipeline — get one at [console.groq.com](https://console.groq.com/keys).

---

## 1. Clone the repository

```bash
git clone <repo-url>
cd AI_BANK_FRAUD_APK_Detection
```

---

## 2. Backend setup (FastAPI)

### 2.0 Install Analysis Tools (Required)
The backend requires `apktool` and `jadx` to reverse engineer APKs. **These are NOT included in the git repository.**

1. Create a `backend/tools/` folder.
2. Download `apktool` from [apktool.org](https://apktool.org/) and rename the JAR file to `apktool.jar`. Place it in `backend/tools/`.
3. Download the `jadx-1.5.5.zip` (or newer) release from [skylot/jadx](https://github.com/skylot/jadx/releases), extract it, and place the contents in `backend/tools/jadx/`.

### 2.1 Create and activate a virtual environment

From the `backend/` folder:

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

This installs FastAPI, Androguard, the Groq SDK, reportlab (PDF generation), and everything else needed.

### 2.3 Configure environment variables

The backend reads its Groq API key from a `.env` file inside `backend/`. Create/edit `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ **Important:** Never commit your real `GROQ_API_KEY` to git. If you're setting this up fresh, make sure `backend/.env` contains your own key and is not pushed publicly. If a real key was ever committed to this repo, rotate it in the Groq console immediately.

### 2.4 Run the backend dev server

```bash
uvicorn main:app --reload
```

You should see:

```
INFO:     Will watch for changes in these directories: ['...\\backend']
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

You should see something like:

```
  VITE ready in ~250 ms
  ➜  Local:   http://localhost:5173/
```

Open that URL in your browser.

---

## 4. Using the app

1. With **both** the backend (`localhost:8000`) and frontend (`localhost:5173`) running, open the frontend URL in your browser.
2. On the upload page, drag-and-drop or choose an `.apk` file (max 100MB). A sample malicious test APK is provided at `backend/test_malicious.apk`.
3. The app switches to a loading screen while the backend:
   - Extracts and scores the APK (~1-2 seconds)
   - Runs the 4-agent AI pipeline (~15-30 seconds, due to sequential Groq calls with built-in rate-limit pacing)
4. The results page shows the risk score, breakdown by category, flagged permissions/URLs, malware family fingerprint match, and AI-written analysis.
5. Click **"Download PDF Report"** to get the formal investigation report.
6. Click **"Analyze Another APK"** to reset and upload a different file.

---

## 5. Project structure

```
AI_BANK_FRAUD_APK_Detection/
├── backend/
│   ├── main.py                 # FastAPI app, CORS config, /analyze endpoints
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # GROQ_API_KEY (not committed with real secrets)
│   ├── tools/                  # Must manually download apktool.jar and jadx/ here
│   │   ├── apktool.jar
│   │   └── jadx/
│   ├── app/
│   │   ├── extraction/         # Metadata (Androguard), Decompilation tools, Code scanner
│   │   │   ├── extractor.py
│   │   │   ├── reverse_engineer.py
│   │   │   └── code_extractor.py
│   │   ├── scoring/            # Permission / impersonation / network risk heuristics
│   │   ├── fingerprints/       # Malware family fingerprint matcher + db.json
│   │   └── ai/                 # 4-agent Groq pipeline receiving code snippets + PDF report
│   │       ├── pipeline.py
│   │       ├── agent1_triage.py
│   │       ├── agent2_analyst.py
│   │       ├── agent3_synthesizer.py
│   │       └── agent4_reporter.py
│   ├── generated_reports/      # PDF reports written here (gitignored)
│   └── test_malicious.apk      # Sample APK for testing
└── frontend/
    ├── src/
    │   ├── App.jsx             # App state, navigation, API calls
    │   ├── components/Navbar.jsx
    │   └── pages/
    │       ├── UploadPage.jsx
    │       ├── LoadingPage.jsx
    │       └── ResultsPage.jsx
    ├── vite.config.js          # Dev proxy config
    └── .env                    # VITE_API_URL
```

---

## 6. Common issues & troubleshooting

**Backend won't start / "Fatal error in launcher"**
The virtual environment's executables may have a broken path (e.g. after moving the project folder). Fix by reinstalling uvicorn inside the venv:
```bash
.\venv\Scripts\python.exe -m pip install --force-reinstall --no-deps uvicorn
```

**Frontend shows "Analysis failed. Make sure the backend is running."**
- Confirm the backend terminal shows `Application startup complete.` and is listening on port 8000.
- Confirm `frontend/.env` has `VITE_API_URL=http://localhost:8000`.
- Check the backend terminal for errors — a 400 means the APK is invalid/corrupted.

**CORS errors in the browser console**
The backend has CORS middleware enabled for all origins/methods (`main.py`). If you still see CORS errors, restart uvicorn after any `main.py` change — `--reload` sometimes doesn't pick up middleware changes cleanly.

**429 / rate limit errors from Groq**
The AI pipeline already includes retry-with-backoff (3 attempts, 5s wait) and a 3-second pause between each of the 4 agents. If you still hit limits consistently, your Groq account/tier may need a higher rate limit, or you can switch the model in `app/ai/*.py` and `app/ai/config.py` to a smaller model (e.g. `llama3-8b-8192`).

**"No analysis data available." on results page**
This means `analysisData` is `null` — usually caused by the API call failing silently. Check the browser console and backend terminal for the actual error.

---

## 7. Building for production (frontend)

```bash
cd frontend
npm run build
```

Output goes to `frontend/dist/`. Set `VITE_API_URL` to your deployed backend URL before building (e.g. via a `.env.production` file or your hosting provider's environment variable settings).
