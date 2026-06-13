# Frontend Contract

This document describes everything needed to build a frontend on top of this
APK malware analysis backend.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check. Returns `{"status": "ok"}`. |
| `POST` | `/analyze` | Basic extraction + heuristic scoring only. Returns raw scores JSON (no AI). Fast (~1-2s). |
| `POST` | `/analyze/full` | Full pipeline: extraction + heuristics + 4-agent AI analysis. Returns the complete analysis JSON (see below). **Takes 15-30 seconds** — show a loading indicator. |
| `GET` | `/report/{filename}` | Downloads the PDF investigation report for a previously analyzed file. Call this *after* `/analyze/full` has completed for that file. `filename` is the **uploaded file's filename** (exact match, e.g. `test_malicious.apk`). |
| `GET` | `/reports` | Lists all previously generated PDF reports (filename, risk_level, final_risk_score, download_url). Useful for a "history" view. |

### Upload requests (`/analyze`, `/analyze/full`)

`multipart/form-data` with a single field `file` (the `.apk` to upload). Filename must end in `.apk`, max size 100MB.

Error responses (both endpoints):

| Status | Body | Condition |
|--------|------|-----------|
| `400` | `{"detail": "Only .apk files are accepted"}` | Filename doesn't end in `.apk` |
| `413` | `{"detail": "File exceeds maximum size of 100MB"}` | Upload larger than 100MB |
| `400` | `{"detail": "Invalid or corrupted APK file"}` | File could not be parsed (not a valid APK) |

### `/report/{filename}`

| Status | Condition |
|--------|-----------|
| `200` | Returns the PDF (`application/pdf`), filename `{filename}_report.pdf` |
| `404` | `{"detail": "No analysis result found for this filename"}` — `/analyze/full` was never run for this filename (or server restarted and no PDF was persisted) |

---

## `POST /analyze/full` Response Structure

Top-level object — everything from `/analyze` (heuristic fields) **plus** the AI pipeline fields (`triage`, `analysis`, `risk_assessment`, `report`, `final_risk_score`, `risk_level`).

| Field | Type | Description |
|-------|------|-------------|
| `filename` | string | Original uploaded filename |
| `size` | integer | File size in bytes |
| `package_name` | string | APK package identifier |
| `app_name` | string | App display label from the manifest |
| `permissions` | string[] | All requested Android permissions |
| `activities` | string[] | Declared activity class names |
| `services` | string[] | Declared service class names |
| `receivers` | string[] | Declared broadcast receiver class names |
| `certificates` | object[] | Signing certificate info (`{issuer, subject}`) |
| `urls_and_ips` | string[] | URLs/IPs found in DEX strings |
| `risk` | object | Permission-based heuristic risk (see below) |
| `impersonation` | object | Brand impersonation heuristic risk |
| `network_risk` | object | Network endpoint heuristic risk |
| `fingerprint_match` | object | Malware family fingerprint match |
| `triage` | object | Agent 1 — quick threat classification |
| `analysis` | object | Agent 2 — plain-English technical analysis |
| `risk_assessment` | object | Agent 3 — final synthesized risk verdict |
| `report` | object | Agent 4 — formal investigation report content (also used to build the PDF) |
| `final_risk_score` | integer (0-100) | Final AI-synthesized risk score (same as `risk_assessment.final_risk_score`) |
| `risk_level` | string | Final risk level — see [Risk Level Colors](#risk-level-colors) |

### `risk` object

| Field | Type | Description |
|-------|------|-------------|
| `permission_risk_score` | integer (0-100) | Score from flagged permissions + combo bonuses |
| `flagged_permissions` | object[] | Each `{permission, points, reason}` |
| `triggered_combos` | object[] | Each `{name, bonus, reason}` — risky permission combos detected |

### `impersonation` object

| Field | Type | Description |
|-------|------|-------------|
| `impersonation_risk_score` | integer (0-100) | Brand-impersonation heuristic score |
| `reasons` | string[] | Why it was flagged (empty if none) |

### `network_risk` object

| Field | Type | Description |
|-------|------|-------------|
| `network_risk_score` | integer (0-100) | Combined network endpoint risk score |
| `flagged_urls` | object[] | Each `{url, reasons: string[]}` |

### `fingerprint_match` object

| Field | Type | Description |
|-------|------|-------------|
| `matched_family` | string | Best-matching known malware family, or `"No significant match"` |
| `confidence` | float (0-100) | Match confidence percentage |
| `matched_permission_overlap` | string[] | Permissions shared with the matched family |
| `matched_package_pattern` | boolean | Package name matched a known pattern |
| `matched_url_pattern` | boolean | A URL/IP matched a known C2 pattern |
| `description` | string \| null | Description of matched family (`null` if no match) |
| `all_scores` | object[] | Each `{family_name, score}` — score (0-1) for every family, for debugging |

### `triage` object (Agent 1)

| Field | Type | Description |
|-------|------|-------------|
| `threat_category` | string | One of `BANKING_TROJAN`, `SPYWARE`, `RANSOMWARE`, `ADWARE`, `SMS_FRAUD`, `CREDENTIAL_STEALER`, `CLEAN`, `UNKNOWN` |
| `investigation_priority` | string | One of `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `requires_deep_analysis` | boolean | Whether deeper manual investigation is recommended |
| `primary_threat_vector` | string | One-sentence summary of the main threat mechanism |
| `target_victim_profile` | string | Who the malware likely targets |
| `triage_summary` | string | 2-3 sentence summary of why this needs attention |

### `analysis` object (Agent 2)

| Field | Type | Description |
|-------|------|-------------|
| `permission_analysis` | string | Plain-English explanation of what the permissions enable |
| `network_analysis` | string | Plain-English explanation of suspicious network indicators |
| `behavioral_pattern` | string | Likely step-by-step attack chain |
| `banking_impact` | string | Specific impact on bank accounts/customers |
| `impersonation_analysis` | string | How the app deceives users (if at all) |
| `technical_indicators` | string[] | Short list of key technical red flags |

### `risk_assessment` object (Agent 3)

| Field | Type | Description |
|-------|------|-------------|
| `final_risk_score` | integer (0-100) | Final synthesized risk score |
| `risk_level` | string | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `CLEAN` |
| `confidence_in_assessment` | string | `HIGH`, `MEDIUM`, or `LOW` |
| `score_breakdown` | object | `{heuristic_component, ai_analysis_component, fingerprint_component}` — each a string explanation |
| `verdict` | string | One-sentence executive verdict |
| `recommended_actions` | string[] | 5 short recommended actions for the fraud team |
| `customer_advisory` | string | Draft SMS/notification for affected customers (<160 chars) |

### `report` object (Agent 4 — also drives the PDF)

| Field | Type | Description |
|-------|------|-------------|
| `report_title` | string | Formal report title including app name and threat level |
| `executive_summary` | string | 3-4 sentence summary for executives |
| `threat_overview` | string | Full paragraph describing the threat |
| `technical_findings` | string | Full paragraph on technical indicators/permissions/network |
| `risk_assessment_narrative` | string | Full paragraph explaining the risk score |
| `impact_assessment` | string | Full paragraph on impact to customers/institution |
| `recommended_actions_detailed` | string[] | 5 detailed actions, each naming who should do it |
| `indicators_of_compromise` | string[] | Specific IOCs (package names, URLs, permission combos) |
| `customer_communication` | string | Full draft customer advisory message |
| `analyst_notes` | string | Additional observations/caveats |

---

## Example `/analyze/full` Response

```json
{
  "filename": "test_malicious.apk",
  "size": 864,
  "package_name": "com.sbi.update.security",
  "app_name": "SBI Bank Update",
  "permissions": [
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.SEND_SMS",
    "android.permission.SYSTEM_ALERT_WINDOW"
  ],
  "activities": [],
  "services": [],
  "receivers": [],
  "certificates": [],
  "urls_and_ips": ["http://malicious-update.top/api/steal"],
  "risk": {
    "permission_risk_score": 100,
    "flagged_permissions": [
      {"permission": "android.permission.READ_SMS", "points": 15, "reason": "Can read SMS messages, often used to steal OTPs"},
      {"permission": "android.permission.SEND_SMS", "points": 15, "reason": "Can send SMS messages, often used for premium SMS fraud"},
      {"permission": "android.permission.RECEIVE_BOOT_COMPLETED", "points": 10, "reason": "Can start automatically on device boot"},
      {"permission": "android.permission.SYSTEM_ALERT_WINDOW", "points": 20, "reason": "Can draw over other apps, often used for overlay attacks"},
      {"permission": "android.permission.BIND_ACCESSIBILITY_SERVICE", "points": 25, "reason": "Can access accessibility services, often abused for full device control"},
      {"permission": "android.permission.REQUEST_INSTALL_PACKAGES", "points": 15, "reason": "Can install other APKs, often used to drop additional malware"}
    ],
    "triggered_combos": [
      {"name": "otp_stealer_combo", "bonus": 25, "reason": "READ_SMS + RECEIVE_BOOT_COMPLETED + SEND_SMS is typical of OTP-stealing trojans"}
    ]
  },
  "impersonation": {
    "impersonation_risk_score": 35,
    "reasons": [
      "App label contains banking-related keyword(s) ['sbi', 'bank'] but package name 'com.sbi.update.security' contains suspicious term(s) ['update', 'security'] that legitimate banking apps typically do not use"
    ]
  },
  "network_risk": {
    "network_risk_score": 25,
    "flagged_urls": [
      {"url": "http://malicious-update.top/api/steal", "reasons": ["Uses non-HTTPS (plaintext HTTP) endpoint", "Uses suspicious top-level domain '.top'"]}
    ]
  },
  "fingerprint_match": {
    "matched_family": "Brata",
    "confidence": 44.99999999999999,
    "matched_permission_overlap": [
      "android.permission.BIND_ACCESSIBILITY_SERVICE",
      "android.permission.READ_SMS",
      "android.permission.SYSTEM_ALERT_WINDOW"
    ],
    "matched_package_pattern": true,
    "matched_url_pattern": false,
    "description": "Spyware/banking trojan capable of factory-resetting devices after fraud (to destroy evidence), uses accessibility services for full screen monitoring and GPS tracking.",
    "all_scores": [
      {"family_name": "Anatsa", "score": 0.3125},
      {"family_name": "SOVA", "score": 0.3125},
      {"family_name": "FluBot", "score": 0.2222222222222222},
      {"family_name": "TeaBot", "score": 0.2222222222222222},
      {"family_name": "Brata", "score": 0.44999999999999996}
    ]
  },
  "triage": {
    "threat_category": "BANKING_TROJAN",
    "investigation_priority": "CRITICAL",
    "requires_deep_analysis": true,
    "primary_threat_vector": "Steals OTPs and sensitive information via SMS and accessibility services",
    "target_victim_profile": "Banking customers, particularly those using SBI services",
    "triage_summary": "This APK poses a significant threat due to its ability to steal sensitive information and impersonate a legitimate banking app. The presence of suspicious permissions and URLs, along with a high permission risk score, warrants immediate attention. The matched family, Brata, is a known spyware and banking trojan, further emphasizing the need for a thorough investigation."
  },
  "analysis": {
    "permission_analysis": "This app can automatically start on device boot, read and send SMS messages, draw over other apps, and access accessibility services, which together allow a fraudster to steal one-time passwords (OTPs) sent via SMS, install additional malware, and potentially take full control of the device to perform transactions without the user's knowledge or consent.",
    "network_analysis": "The suspicious URL found indicates that the malware communicates with a command and control server using a non-secure HTTP endpoint with a suspicious top-level domain, suggesting a malicious infrastructure designed to steal sensitive information from victims.",
    "behavioral_pattern": "The likely attack chain involves the malware automatically starting on device boot, waiting for an SMS containing an OTP, then using accessibility services to read the OTP and send it to the command and control server, which could then use this information to perform transactions on the victim's bank account, potentially with the malware overlaying fake screens to trick the user into revealing more sensitive information.",
    "banking_impact": "The attacker can steal OTPs, allowing them to perform transactions on the victim's bank account, potentially leading to financial loss, and may also be able to access other sensitive information such as account numbers and passwords.",
    "impersonation_analysis": "This app is pretending to be a legitimate SBI Bank update, using the bank's name and potentially its branding to trick victims into installing the malware, which is a social engineering technique designed to build trust with the victim and increase the likelihood of the malware being installed.",
    "technical_indicators": ["READ_SMS", "SEND_SMS", "BIND_ACCESSIBILITY_SERVICE", "SYSTEM_ALERT_WINDOW", "REQUEST_INSTALL_PACKAGES", "non-HTTPS C2 server", "suspicious .top domain"]
  },
  "risk_assessment": {
    "final_risk_score": 98,
    "risk_level": "CRITICAL",
    "confidence_in_assessment": "HIGH",
    "score_breakdown": {
      "heuristic_component": "High Permission Risk Score and moderate Impersonation Risk Score indicate potential for significant malicious activity, while Network Risk Score is relatively low but still concerning",
      "ai_analysis_component": "Threat Category of BANKING_TROJAN and Primary Threat Vector of stealing OTPs and sensitive information via SMS and accessibility services significantly increased the risk assessment",
      "fingerprint_component": "Fingerprint match with Brata at 45% confidence, although not definitive, supports the overall malicious nature of the APK"
    },
    "verdict": "This APK poses a critical risk to bank customers' accounts and sensitive information due to its ability to steal OTPs and perform transactions",
    "recommended_actions": [
      "Block all transactions from devices with this APK installed",
      "Notify customers who have installed this app and advise them to uninstall immediately",
      "Monitor for suspicious activity on potentially affected accounts",
      "Update fraud detection rules to include indicators from this APK",
      "Collaborate with law enforcement to take down C2 servers and disrupt malware distribution"
    ],
    "customer_advisory": "Uninstall suspicious app to protect account security"
  },
  "report": {
    "report_title": "CRITICAL Threat: SBI Bank Update (com.sbi.update.security) Banking Trojan Investigation Report",
    "executive_summary": "A critical threat has been identified in the SBI Bank Update APK, which poses a significant risk to bank customers' accounts and sensitive information. The malware, classified as a banking trojan, can steal OTPs and perform transactions, potentially leading to financial loss. Immediate action is required to protect customers and prevent further malicious activity. It is recommended that all transactions from devices with this APK installed be blocked, and customers be notified to uninstall the app immediately.",
    "threat_overview": "The SBI Bank Update APK has been found to be a banking trojan, specifically matching the Brata malware family with a confidence level of 44.99999999999999%. The malware's behavioral pattern involves automatically starting on device boot, waiting for an SMS containing an OTP, and then using accessibility services to read the OTP and send it to the command and control server. This information can then be used to perform transactions on the victim's bank account, potentially with the malware overlaying fake screens to trick the user into revealing more sensitive information.",
    "technical_findings": "Technical analysis of the APK has revealed that it requests a range of permissions, including accessibility services and SMS reading capabilities, which are used to facilitate the theft of OTPs and other sensitive information. Network activity indicates communication with a command and control server, which is likely used to receive instructions and send stolen data. The malware's ability to overlay fake screens and intercept SMS messages makes it a highly sophisticated and dangerous threat.",
    "risk_assessment_narrative": "The risk score of 98/100 indicates a critical risk to bank customers' accounts and sensitive information. This risk assessment is based on the malware's ability to steal OTPs and perform transactions, which could result in significant financial loss for customers. The fact that the malware can also access other sensitive information, such as account numbers and passwords, further exacerbates the risk. The high confidence level in the malware family match and the sophistication of the malware's behavioral pattern also contribute to the critical risk assessment.",
    "impact_assessment": "The potential impact of this threat to bank customers and the institution is significant. If left unchecked, the malware could result in widespread financial loss for customers, damage to the bank's reputation, and potential regulatory penalties. The fact that the malware can access sensitive information, such as account numbers and passwords, also raises concerns about the potential for identity theft and other forms of cybercrime. It is essential that immediate action be taken to protect customers and prevent further malicious activity.",
    "recommended_actions_detailed": [
      "Block all transactions from devices with this APK installed, to be carried out by the fraud prevention team",
      "Notify customers who have installed this app and advise them to uninstall immediately, to be carried out by the customer service team",
      "Monitor for suspicious activity on potentially affected accounts, to be carried out by the fraud prevention team",
      "Update fraud detection rules to include indicators from this APK, to be carried out by the IT security team",
      "Collaborate with law enforcement to take down C2 servers and disrupt malware distribution, to be carried out by the cybersecurity team"
    ],
    "indicators_of_compromise": [
      "Package name: com.sbi.update.security",
      "URLs: command and control server URLs",
      "Permission combinations: accessibility services and SMS reading capabilities"
    ],
    "customer_communication": "Dear valued customer, we have identified a critical threat in the SBI Bank Update APK, which may have been installed on your device. This malware can steal OTPs and perform transactions, potentially leading to financial loss. We strongly advise you to uninstall the app immediately and monitor your account activity for any suspicious transactions. If you have any concerns or questions, please do not hesitate to contact our customer service team.",
    "analyst_notes": "Additional analysis is required to determine the full extent of the malware's capabilities and to identify any potential variants. It is also recommended that customers be advised to install antivirus software and keep their devices and operating systems up to date to prevent similar threats in the future."
  },
  "final_risk_score": 98,
  "risk_level": "CRITICAL"
}
```

---

## Loading State

`/analyze/full` runs the heuristic pipeline **and** 4 sequential Groq LLM calls. Total response time is **15-30 seconds**. The frontend must show a loading/progress indicator for the duration of this request — do not assume a fast response like `/analyze`.

---

## Risk Level Colors

Use `risk_level` (top-level field, also in `risk_assessment.risk_level`) to color-code the UI:

| `risk_level` | Color |
|---------------|-------|
| `CRITICAL` | Red |
| `HIGH` | Orange |
| `MEDIUM` | Yellow |
| `LOW` | Green |
| `CLEAN` | Green |

This matches the color banner used in the generated PDF report.

---

## PDF Download

After `/analyze/full` completes successfully, the PDF report can be downloaded from:

```
GET /report/{filename}
```

where `{filename}` is **exactly the filename that was uploaded** (e.g. `test_malicious.apk` → `GET /report/test_malicious.apk`). The response is `application/pdf` with `Content-Disposition` filename `{filename}_report.pdf`.

Note: filenames containing special characters (spaces, parentheses, etc.) must be URL-encoded when constructing the request URL.
