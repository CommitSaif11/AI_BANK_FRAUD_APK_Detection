import json
import time

import groq

from app.ai.config import groq_client

SYSTEM_PROMPT = (
    "You are a cybersecurity triage specialist at a bank's fraud prevention unit. "
    "You analyze mobile APK threat data and classify threats quickly and accurately. "
    "You always respond in valid JSON only — no explanation, no markdown, no backticks. "
    "Just raw JSON."
)

USER_PROMPT_TEMPLATE = """Analyze this APK analysis data and perform triage classification.

APK DATA:
{apk_data}

Respond with ONLY this JSON structure, no other text:

{{
"threat_category": "one of: BANKING_TROJAN, SPYWARE, RANSOMWARE, ADWARE, SMS_FRAUD, CREDENTIAL_STEALER, CLEAN, UNKNOWN",
"investigation_priority": "one of: CRITICAL, HIGH, MEDIUM, LOW",
"requires_deep_analysis": true or false,
"primary_threat_vector": "one short sentence describing the main threat mechanism",
"target_victim_profile": "who is likely targeted by this malware",
"triage_summary": "2-3 sentences maximum summarizing why this needs attention"
}}"""

FALLBACK_RESULT = {
    "threat_category": "UNKNOWN",
    "investigation_priority": "MEDIUM",
    "requires_deep_analysis": True,
    "primary_threat_vector": "",
    "target_victim_profile": "",
    "triage_summary": "Triage agent failed to produce a valid response.",
    "error": "Failed to parse Groq response as JSON after retry.",
}


def _call_groq(user_prompt: str) -> str:
    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=500,
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


def run_triage_agent(analysis_json: dict, code_snippet: str = "") -> dict:
    apk_data = json.dumps(analysis_json, indent=2)
    user_prompt = USER_PROMPT_TEMPLATE.format(apk_data=apk_data)

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
