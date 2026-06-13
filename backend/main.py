import logging
import os
import tempfile
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.extraction.extractor import extract_apk_info
from app.scoring.heuristics import score_permissions
from app.scoring.impersonation import check_impersonation
from app.scoring.network_risk import check_network_risk
from app.fingerprints.matcher import match_fingerprints
from app.ai.pipeline import run_full_ai_pipeline
from app.ai.pdf_generator import generate_pdf_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="APK Malware Analysis Tool")

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

        try:
            info = extract_apk_info(tmp_path)
        except Exception:
            logger.exception("Failed to extract APK info for '%s'", file.filename)
            raise HTTPException(status_code=400, detail="Invalid or corrupted APK file")

        risk = score_permissions(info["permissions"])
        impersonation = check_impersonation(info["app_name"], info["package_name"])
        network_risk = check_network_risk(info["urls_and_ips"])
        fingerprint_match = match_fingerprints(
            info.get("permissions") or [],
            info.get("package_name") or "",
            info.get("urls_and_ips") or [],
        )

        logger.info("Analysis complete for '%s'", file.filename)

        return {
            "filename": file.filename,
            "size": len(contents),
            **info,
            "risk": risk,
            "impersonation": impersonation,
            "network_risk": network_risk,
            "fingerprint_match": fingerprint_match,
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


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
        logger.info("Analyzing '%s' (%d bytes)", file.filename, len(contents))

        try:
            info = extract_apk_info(tmp_path)
        except Exception:
            logger.exception("Failed to extract APK info for '%s'", file.filename)
            raise HTTPException(status_code=400, detail="Invalid or corrupted APK file")

        risk = score_permissions(info["permissions"])
        impersonation = check_impersonation(info["app_name"], info["package_name"])
        network_risk = check_network_risk(info["urls_and_ips"])
        fingerprint_match = match_fingerprints(
            info.get("permissions") or [],
            info.get("package_name") or "",
            info.get("urls_and_ips") or [],
        )

        analysis_json = {
            "filename": file.filename,
            "size": len(contents),
            **info,
            "risk": risk,
            "impersonation": impersonation,
            "network_risk": network_risk,
            "fingerprint_match": fingerprint_match,
        }

        logger.info("Heuristic analysis complete for '%s', starting AI pipeline", file.filename)

        ai_result = run_full_ai_pipeline(analysis_json)

        logger.info("AI pipeline complete for '%s'", file.filename)

        result = {
            **analysis_json,
            **ai_result,
        }

        ANALYSIS_RESULTS[file.filename] = result

        pdf_path = os.path.join(REPORTS_DIR, f"{file.filename}_report.pdf")
        generate_pdf_report(result, pdf_path)

        return result
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


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
