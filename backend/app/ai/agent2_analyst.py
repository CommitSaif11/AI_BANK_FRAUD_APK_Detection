import json
import time

import groq

from app.ai.config import groq_client, GROQ_MODEL

SYSTEM_PROMPT = (
    "You are a senior malware analyst specializing in Android banking trojans. "
    "You explain technical findings in clear language that bank fraud investigators "
    "and non-technical stakeholders can understand. You always respond in valid JSON "
    "only — no markdown, no backticks, just raw JSON."
)

USER_PROMPT_TEMPLATE = """You are analyzing a suspicious Android APK. Here is the technical data extracted from it:

PACKAGE NAME: {package_name}
APP DISPLAY NAME: {app_name}
PERMISSIONS REQUESTED: {permissions}
FLAGGED PERMISSION REASONS: {flagged_permissions}
DANGEROUS COMBOS DETECTED: {triggered_combos}
SUSPICIOUS URLS FOUND: {urls_and_ips}
FLAGGED NETWORK INDICATORS: {flagged_urls}
FINGERPRINT MATCH: {fingerprint_match}
TRIAGE CLASSIFICATION: {triage_classification}

Respond with ONLY this JSON structure:

{{
"permission_analysis": "Plain English explanation of what the requested permissions mean together — what can this app actually DO with these permissions? Focus on what a fraudster could do to a bank customer.",
"network_analysis": "Plain English explanation of the suspicious URLs/IPs found — what do these indicate about the malware infrastructure?",
"behavioral_pattern": "Based on permissions + network indicators + fingerprint match, describe the likely attack chain: how would this malware actually attack a victim step by step?",
"banking_impact": "Specific impact on banking customers — what can the attacker steal or do to bank accounts?",
"impersonation_analysis": "Is this app pretending to be a legitimate app or bank? Explain the deception technique used.",
"code_analysis": "what suspicious logic was found in the actual code",
"technical_indicators": ["list", "of", "key", "technical", "red", "flags", "as", "short", "strings"]
}}"""

FALLBACK_RESULT = {
    "permission_analysis": "",
    "network_analysis": "",
    "behavioral_pattern": "",
    "banking_impact": "",
    "impersonation_analysis": "",
    "code_analysis": "",
    "technical_indicators": [],
    "error": "Failed to parse Groq response as JSON after retry.",
}


def _build_user_prompt(analysis_json: dict, triage_result: dict) -> str:
    risk = analysis_json.get("risk", {})
    network_risk = analysis_json.get("network_risk", {})
    fingerprint_match = analysis_json.get("fingerprint_match", {})

    fingerprint_summary = {
        "matched_family": fingerprint_match.get("matched_family"),
        "confidence": fingerprint_match.get("confidence"),
    }

    triage_classification = {
        "threat_category": triage_result.get("threat_category"),
        "primary_threat_vector": triage_result.get("primary_threat_vector"),
    }

    return USER_PROMPT_TEMPLATE.format(
        package_name=analysis_json.get("package_name"),
        app_name=analysis_json.get("app_name"),
        permissions=json.dumps(analysis_json.get("permissions", [])),
        flagged_permissions=json.dumps(risk.get("flagged_permissions", [])),
        triggered_combos=json.dumps(risk.get("triggered_combos", [])),
        urls_and_ips=json.dumps(analysis_json.get("urls_and_ips", [])),
        flagged_urls=json.dumps(network_risk.get("flagged_urls", [])),
        fingerprint_match=json.dumps(fingerprint_summary),
        triage_classification=json.dumps(triage_classification),
    )


def _call_groq(user_prompt: str) -> str:
    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                max_tokens=1000,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except groq.RateLimitError:
            if attempt == 2:
                raise
            time.sleep(5)


def run_analyst_agent(analysis_json: dict, triage_result: dict, code_snippet: str = "") -> dict:
    user_prompt = _build_user_prompt(analysis_json, triage_result)

    if code_snippet:
        user_prompt += f"\n\nDECOMPILED CODE SNIPPETS (suspicious files only):\n{code_snippet}"

    try:
        content = _call_groq(user_prompt)
        return json.loads(content)
    except (json.JSONDecodeError, Exception):
        pass

    retry_prompt = user_prompt + "\n\nIMPORTANT: respond with raw JSON only, absolutely no other text."
    try:
        content = _call_groq(retry_prompt)
        return json.loads(content)
    except (json.JSONDecodeError, Exception):
        return FALLBACK_RESULT
