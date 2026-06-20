# API Contract: `/analyze`

## Endpoint

```
POST /analyze
```

### Request

`multipart/form-data` with a single field:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file upload | yes | The APK file to analyze. Filename must end in `.apk`. Max size 100MB. |

### Error Responses

| Status | Body | Condition |
|--------|------|-----------|
| `400` | `{"detail": "Only .apk files are accepted"}` | Filename doesn't end in `.apk` |
| `413` | `{"detail": "File exceeds maximum size of 100MB"}` | Upload larger than 100MB |
| `400` | `{"detail": "Invalid or corrupted APK file"}` | File could not be parsed by Androguard (not a valid ZIP/APK) |

---

## Success Response (`200 OK`)

Top-level JSON object:

| Field | Type | Description |
|-------|------|-------------|
| `filename` | string | Original uploaded filename |
| `size` | integer | File size in bytes |
| `package_name` | string | APK package identifier (e.g. `com.boi.update.security`) |
| `app_name` | string | App display label from the manifest |
| `permissions` | array of strings | All requested permissions (e.g. `android.permission.READ_SMS`) |
| `activities` | array of strings | Declared activity class names |
| `services` | array of strings | Declared service class names |
| `receivers` | array of strings | Declared broadcast receiver class names |
| `certificates` | array of objects | Signing certificate info (see [Certificate Object](#certificate-object)) |
| `urls_and_ips` | array of strings | URLs and raw IP addresses found in DEX string data |
| `risk` | object | Permission-based heuristic risk score (see [Risk Object](#risk-object)) |
| `impersonation` | object | Brand impersonation risk (see [Impersonation Object](#impersonation-object)) |
| `network_risk` | object | Network endpoint risk (see [Network Risk Object](#network-risk-object)) |
| `fingerprint_match` | object | Malware family fingerprint match (see [Fingerprint Match Object](#fingerprint-match-object)) |

---

### Certificate Object

Each entry in `certificates`:

| Field | Type | Description |
|-------|------|-------------|
| `issuer` | string | Human-readable certificate issuer (DN) |
| `subject` | string | Human-readable certificate subject (DN) |

---

### Risk Object (`risk`)

| Field | Type | Description |
|-------|------|-------------|
| `permission_risk_score` | integer (0-100) | Combined score from flagged permissions + combo bonuses, capped at 100 |
| `flagged_permissions` | array of objects | Each: `{"permission": string, "points": integer, "reason": string}` — risky permissions found and why |
| `triggered_combos` | array of objects | Each: `{"name": string, "bonus": integer, "reason": string}` — risky permission combinations detected (e.g. OTP-stealer pattern) |

---

### Impersonation Object (`impersonation`)

| Field | Type | Description |
|-------|------|-------------|
| `impersonation_risk_score` | integer (0-100) | Score based on brand-impersonation heuristics |
| `reasons` | array of strings | Human-readable explanations for each flag raised (empty if none) |

---

### Network Risk Object (`network_risk`)

| Field | Type | Description |
|-------|------|-------------|
| `network_risk_score` | integer (0-100) | Combined score from flagged URLs/IPs, capped at 100 |
| `flagged_urls` | array of objects | Each: `{"url": string, "reasons": array of strings}` — URLs/IPs flagged for non-HTTPS, raw IP endpoints, or suspicious TLDs |

---

### Fingerprint Match Object (`fingerprint_match`)

| Field | Type | Description |
|-------|------|-------------|
| `matched_family` | string | Name of the best-matching known malware family, or `"No significant match"` if confidence < 20% |
| `confidence` | float (0-100) | Combined match score as a percentage |
| `matched_permission_overlap` | array of strings | Permissions shared between the APK and the matched family's typical permission set |
| `matched_package_pattern` | boolean | Whether the package name matched a known pattern for the (best-scoring) family |
| `matched_url_pattern` | boolean | Whether any extracted URL/IP matched a known C2 pattern for the (best-scoring) family |
| `description` | string or null | Description of the matched family; `null` if `matched_family` is `"No significant match"` |
| `all_scores` | array of objects | Each: `{"family_name": string, "score": float (0-1)}` — combined score for every family in the database, for transparency/debugging |

---

## Example Response

```json
{
  "filename": "test_malicious.apk",
  "size": 864,
  "package_name": "com.boi.update.security",
  "app_name": "BOI Bank Update",
  "permissions": [
    "android.permission.READ_SMS",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_BOOT_COMPLETED"
  ],
  "activities": [],
  "services": [],
  "receivers": [],
  "certificates": [],
  "urls_and_ips": ["http://malicious-update.top/api/steal"],
  "risk": {
    "permission_risk_score": 100,
    "flagged_permissions": [
      {
        "permission": "android.permission.READ_SMS",
        "points": 15,
        "reason": "Can read SMS messages, often used to steal OTPs"
      }
    ],
    "triggered_combos": [
      {
        "name": "otp_stealer_combo",
        "bonus": 25,
        "reason": "READ_SMS + RECEIVE_BOOT_COMPLETED + SEND_SMS is typical of OTP-stealing trojans"
      }
    ]
  },
  "impersonation": {
    "impersonation_risk_score": 0,
    "reasons": []
  },
  "network_risk": {
    "network_risk_score": 25,
    "flagged_urls": [
      {
        "url": "http://malicious-update.top/api/steal",
        "reasons": [
          "Uses non-HTTPS (plaintext HTTP) endpoint",
          "Uses suspicious top-level domain '.top'"
        ]
      }
    ]
  },
  "fingerprint_match": {
    "matched_family": "Brata",
    "confidence": 45.0,
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
      {"family_name": "Brata", "score": 0.45}
    ]
  }
}
```
