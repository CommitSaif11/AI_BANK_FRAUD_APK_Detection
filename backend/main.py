import logging
import os
import tempfile
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.extraction.extractor import extract_apk_info
from app.extraction.reverse_engineer import decompile_apk
from app.scoring.heuristics import score_permissions
from app.scoring.impersonation import check_impersonation
from app.scoring.network_risk import check_network_risk
from app.fingerprints.matcher import match_fingerprints
from app.ai.pipeline import run_full_ai_pipeline
from app.ai.pdf_generator import generate_pdf_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="APK Malware Analysis Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

# In-memory store for full pipeline results, keyed by uploaded filename.
ANALYSIS_RESULTS = {}

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".apk"):
        raise HTTPException(status_code=400, detail="Only .apk files are accepted")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        logger.warning("Rejected '%s': file too large (%d bytes)", file.filename, len(contents))
        raise HTTPException(status_code=413, detail="File exceeds maximum size of 100MB")

    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(contents)

    try:
        logger.info("Analyzing '%s' (%d bytes)", file.filename, len(contents))

        # 1. Reverse engineer the APK
        logger.info("Step 1: Reverse engineering APK with apktool and JADX...")
        apktool_dir, jadx_dir = decompile_apk(tmp_path)
        if not apktool_dir or not jadx_dir:
            logger.error("Failed to decompile APK '%s'", file.filename)
            raise HTTPException(status_code=500, detail="Failed to decompile APK.")
        logger.info("Reverse engineering complete.")
        logger.info(f"  - Apktool output: {apktool_dir}")
        logger.info(f"  - JADX output: {jadx_dir}")


        # 2. Extract metadata with Androguard
        logger.info("Step 2: Extracting metadata with Androguard...")
        try:
            info = extract_apk_info(tmp_path)
        except Exception:
            logger.exception("Failed to extract APK info for '%s'", file.filename)
            raise HTTPException(status_code=400, detail="Invalid or corrupted APK file")
        logger.info("Metadata extraction complete.")

        # 3. Score and analyze
        logger.info("Step 3: Scoring and fingerprinting...")
        risk = score_permissions(info["permissions"])
        impersonation = check_impersonation(info["app_name"], info["package_name"])
        network_risk = check_network_risk(info["urls_and_ips"])
        fingerprint_match = match_fingerprints(
            info.get("permissions") or [],
            info.get("package_name") or "",
            info.get("urls_and_ips") or [],
        )
        logger.info("Scoring complete for '%s'", file.filename)

        return {
            "filename": file.filename,
            "size": len(contents),
            **info,
            "risk": risk,
            "impersonation": impersonation,
            "network_risk": network_risk,
            "fingerprint_match": fingerprint_match,
            "apktool_output_path": apktool_dir,
            "jadx_output_path": jadx_dir,
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        # Decompiled files are in a temp folder managed by the OS or cleaned up by the decompile_apk function on failure.
        # If successful, we might want to manage cleanup differently, but for now, this is ok.



@app.post("/analyze/full")
async def analyze_full(file: UploadFile = File(...)):
    # NOTE: This endpoint runs the heuristic analysis plus 4 sequential AI
    # (Groq) calls. Expect ~15-30 seconds response time.
    if not file.filename.lower().endswith(".apk"):
        raise HTTPException(status_code=400, detail="Only .apk files are accepted")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        logger.warning("Rejected '%s': file too large (%d bytes)", file.filename, len(contents))
        raise HTTPException(status_code=413, detail="File exceeds maximum size of 100MB")

    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(contents)

    try:
        logger.info("Starting full analysis for '%s'", file.filename)

        # 1. Reverse engineer the APK
        logger.info("Step 1: Reverse engineering APK with apktool and JADX...")
        apktool_dir, jadx_dir = decompile_apk(tmp_path)
        if not apktool_dir or not jadx_dir:
            logger.error("Failed to decompile APK '%s'", file.filename)
            raise HTTPException(status_code=500, detail="Failed to decompile APK.")
        logger.info("Reverse engineering complete.")
        logger.info(f"  - Apktool output: {apktool_dir}")
        logger.info(f"  - JADX output: {jadx_dir}")

        # 2. Extract metadata
        logger.info("Step 2: Extracting metadata with Androguard...")
        try:
            info = extract_apk_info(tmp_path)
        except Exception:
            logger.exception("Failed to extract APK info for '%s'", file.filename)
            raise HTTPException(status_code=400, detail="Invalid or corrupted APK file")
        logger.info("Metadata extraction complete.")

        # 3. Score and analyze (heuristics)
        logger.info("Step 3: Scoring and fingerprinting...")
        risk = score_permissions(info["permissions"])
        impersonation = check_impersonation(info["app_name"], info["package_name"])
        network_risk = check_network_risk(info["urls_and_ips"])
        fingerprint_match = match_fingerprints(
            info.get("permissions") or [],
            info.get("package_name") or "",
            info.get("urls_and_ips") or [],
        )
        logger.info("Scoring complete.")

        # 4. Build initial analysis JSON for the AI pipeline
        analysis_json = {
            "filename": file.filename,
            "size": len(contents),
            **info,
            "risk": risk,
            "impersonation": impersonation,
            "network_risk": network_risk,
            "fingerprint_match": fingerprint_match,
            "apktool_output_path": apktool_dir,
            "jadx_output_path": jadx_dir,
        }

        # 5. Run AI pipeline
        logger.info("Step 5: Running AI analysis pipeline...")
        try:
            ai_results = run_full_ai_pipeline(analysis_json, jadx_dir=jadx_dir)
        except Exception as e:
            logger.exception("AI pipeline failed for '%s'", file.filename)
            raise HTTPException(status_code=500, detail=f"AI pipeline failed: {e}")
        logger.info("AI analysis complete.")

        # 6. Combine all results
        full_result = {
            **analysis_json,
            "ai_analysis": ai_results,
        }

        # Store result for PDF generation
        ANALYSIS_RESULTS[file.filename] = full_result
        logger.info("Full analysis complete for '%s'", file.filename)

        return full_result
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        # Decompiled files are in a temp folder managed by the OS or cleaned up by the decompile_apk function on failure.


@app.get("/reports")
def list_reports():
    reports = []
    for entry in os.scandir(REPORTS_DIR):
        if entry.is_file() and entry.name.endswith("_report.pdf"):
            filename = entry.name[: -len("_report.pdf")]
            result = ANALYSIS_RESULTS.get(filename, {})
            reports.append(
                {
                    "filename": filename,
                    "risk_level": result.get("risk_level"),
                    "final_risk_score": result.get("final_risk_score"),
                    "download_url": f"/report/{filename}",
                }
            )
    return {"reports": reports}


@app.get("/report/{filename}")
def get_report(filename: str):
    pdf_path = os.path.join(REPORTS_DIR, f"{filename}_report.pdf")

    if not os.path.exists(pdf_path):
        result = ANALYSIS_RESULTS.get(filename)
        if result is None:
            raise HTTPException(status_code=404, detail="No analysis result found for this filename")
        generate_pdf_report(result, pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{filename}_report.pdf",
    )
