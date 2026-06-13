import json
import time

import groq

from app.ai.config import groq_client

SYSTEM_PROMPT = (
    "You are a chief cybersecurity risk officer at a major bank. You synthesize "
    "threat intelligence into final risk verdicts with clear scoring justification. "
    "Your risk scores must be consistent, defensible, and explainable to bank "
    "executives and regulators. Always respond in valid JSON only."
)

USER_PROMPT_TEMPLATE = """Synthesize all analysis data below into a final risk assessment for this APK.

HEURISTIC SCORES (from automated rules engine):
Permission Risk Score: {permission_risk_score}/100
Network Risk Score: {network_risk_score}/100
Impersonation Risk Score: {impersonation_risk_score}/100
Fingerprint Match: {matched_family} at {confidence}% confidence

TRIAGE RESULT:
Threat Category: {threat_category}
Investigation Priority: {investigation_priority}
Primary Threat Vector: {primary_threat_vector}

ANALYST FINDINGS:
Behavioral Pattern: {behavioral_pattern}
Banking Impact: {banking_impact}
Technical Indicators: {technical_indicators}

Based on ALL of the above, respond with ONLY this JSON:

{{
"final_risk_score": a number 0-100,
"risk_level": "one of: CRITICAL, HIGH, MEDIUM, LOW, CLEAN",
"confidence_in_assessment": "one of: HIGH, MEDIUM, LOW",
"score_breakdown": {{
"heuristic_component": "explanation of how heuristic scores contributed",
"ai_analysis_component": "explanation of how AI analysis adjusted the score",
"fingerprint_component": "explanation of how family matching contributed"
}},
"verdict": "One clear sentence verdict a bank executive can act on immediately",
"recommended_actions": [
"Action 1 for bank fraud team",
"Action 2",
"Action 3",
"Action 4",
"Action 5"
],
"customer_advisory": "Draft SMS/notification the bank can send to customers who may have installed this app — keep it under 160 characters, clear and non-alarming"
}}"""

FALLBACK_RESULT = {
    "final_risk_score": 50,
    "risk_level": "MEDIUM",
    "confidence_in_assessment": "LOW",
    "score_breakdown": {
        "heuristic_component": "",
        "ai_analysis_component": "",
        "fingerprint_component": "",
    },
    "verdict": "",
    "recommended_actions": [],
    "customer_advisory": "",
    "error": "Failed to parse Groq response as JSON after retry.",
}


def _build_user_prompt(analysis_json: dict, triage_result: dict, analyst_result: dict) -> str:
    risk = analysis_json.get("risk", {})
    network_risk = analysis_json.get("network_risk", {})
    impersonation = analysis_json.get("impersonation", {})
    fingerprint_match = analysis_json.get("fingerprint_match", {})

    return USER_PROMPT_TEMPLATE.format(
        permission_risk_score=risk.get("permission_risk_score"),
        network_risk_score=network_risk.get("network_risk_score"),
        impersonation_risk_score=impersonation.get("impersonation_risk_score"),
        matched_family=fingerprint_match.get("matched_family"),
        confidence=fingerprint_match.get("confidence"),
        threat_category=triage_result.get("threat_category"),
        investigation_priority=triage_result.get("investigation_priority"),
        primary_threat_vector=triage_result.get("primary_threat_vector"),
        behavioral_pattern=analyst_result.get("behavioral_pattern"),
        banking_impact=analyst_result.get("banking_impact"),
        technical_indicators=json.dumps(analyst_result.get("technical_indicators", [])),
    )


def _call_groq(user_prompt: str) -> str:
    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=800,
                temperature=0.1,
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


def run_synthesizer_agent(analysis_json: dict, triage_result: dict, analyst_result: dict) -> dict:
    user_prompt = _build_user_prompt(analysis_json, triage_result, analyst_result)

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
