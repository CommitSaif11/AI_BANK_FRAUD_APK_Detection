import json
from datetime import date

from app.ai.config import groq_client

SYSTEM_PROMPT = (
    "You are a professional cybersecurity report writer at a tier-1 bank. You write "
    "formal, structured investigation reports for the fraud prevention team, senior "
    "management, and compliance officers. Reports must be clear, professional, and "
    "actionable. Always respond in valid JSON only."
)

USER_PROMPT_TEMPLATE = """Write a complete formal APK threat investigation report based on all findings below.

BASIC INFO:
File: {filename}
Package: {package_name}
App Name: {app_name}
Analysis Date: {analysis_date}

RISK VERDICT:
Final Risk Score: {final_risk_score}/100
Risk Level: {risk_level}
Verdict: {verdict}

THREAT DETAILS:
Category: {threat_category}
Matched Malware Family: {matched_family} ({confidence}% confidence)
Behavioral Pattern: {behavioral_pattern}
Banking Impact: {banking_impact}

RECOMMENDED ACTIONS: {recommended_actions}

Respond with ONLY this JSON:

{{
"report_title": "Formal report title including app name and threat level",
"executive_summary": "3-4 sentences for bank executives — what was found, how serious, what to do immediately",
"threat_overview": "Full paragraph describing the threat in detail for the fraud team",
"technical_findings": "Full paragraph covering technical indicators, permissions, network activity",
"risk_assessment_narrative": "Full paragraph explaining the risk score and what it means in practice",
"impact_assessment": "Full paragraph on potential impact to bank customers and the institution",
"recommended_actions_detailed": ["Detailed action 1 with who should do it", "Detailed action 2", "Detailed action 3", "Detailed action 4", "Detailed action 5"],
"indicators_of_compromise": ["list of specific IOCs: package names, URLs, permission combos"],
"customer_communication": "Full draft customer advisory message",
"analyst_notes": "Any additional observations or caveats about this analysis"
}}"""

FALLBACK_RESULT = {
    "report_title": "",
    "executive_summary": "",
    "threat_overview": "",
    "technical_findings": "",
    "risk_assessment_narrative": "",
    "impact_assessment": "",
    "recommended_actions_detailed": [],
    "indicators_of_compromise": [],
    "customer_communication": "",
    "analyst_notes": "",
    "error": "Failed to parse Groq response as JSON after retry.",
}


def _build_user_prompt(analysis_json: dict, triage_result: dict, analyst_result: dict, synthesizer_result: dict) -> str:
    fingerprint_match = analysis_json.get("fingerprint_match", {})

    return USER_PROMPT_TEMPLATE.format(
        filename=analysis_json.get("filename"),
        package_name=analysis_json.get("package_name"),
        app_name=analysis_json.get("app_name"),
        analysis_date=date.today().isoformat(),
        final_risk_score=synthesizer_result.get("final_risk_score"),
        risk_level=synthesizer_result.get("risk_level"),
        verdict=synthesizer_result.get("verdict"),
        threat_category=triage_result.get("threat_category"),
        matched_family=fingerprint_match.get("matched_family"),
        confidence=fingerprint_match.get("confidence"),
        behavioral_pattern=analyst_result.get("behavioral_pattern"),
        banking_impact=analyst_result.get("banking_impact"),
        recommended_actions=json.dumps(synthesizer_result.get("recommended_actions", [])),
    )


def _call_groq(user_prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1500,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def run_reporter_agent(analysis_json: dict, triage_result: dict, analyst_result: dict, synthesizer_result: dict) -> dict:
    user_prompt = _build_user_prompt(analysis_json, triage_result, analyst_result, synthesizer_result)

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
