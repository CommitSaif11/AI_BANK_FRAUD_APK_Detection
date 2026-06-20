import re

BANKING_KEYWORDS = [
    "boi", "sbi", "hdfc", "icici", "bank", "upi", "pay", "axis", "kotak", "paytm",
    "pnb", "bob", "canara", "union", "phonepe", "gpay",
]

SUSPICIOUS_PACKAGE_SUFFIXES = ["update", "security", "verify", "install", "latest"]

KNOWN_PACKAGE_PREFIXES = [
    "com.boi",
    "com.sbi",
    "com.csam.icici",
    "com.snapwork.hdfc",
    "com.hdfcbank",
    "com.axis",
    "net.one97.paytm",
    "com.kotak",
    "com.upi",
]

RANDOM_PACKAGE_REGEX = re.compile(r"[a-z]*\d{3,}[a-z\d]*")


def check_impersonation(app_name: str, package_name: str) -> dict:
    reasons = []
    score = 0

    app_name_lower = (app_name or "").lower()
    package_lower = (package_name or "").lower()

    matched_keywords = [kw for kw in BANKING_KEYWORDS if kw in app_name_lower]
    if matched_keywords:
        is_known = any(package_lower.startswith(prefix) for prefix in KNOWN_PACKAGE_PREFIXES)
        if not is_known:
            score += 30
            reasons.append(
                f"App label contains banking-related keyword(s) {matched_keywords} "
                f"but package name '{package_name}' does not match any known official banking package"
            )

        matched_suffixes = [s for s in SUSPICIOUS_PACKAGE_SUFFIXES if s in package_lower]
        if matched_suffixes:
            score += 35
            reasons.append(
                f"App label contains banking-related keyword(s) {matched_keywords} "
                f"but package name '{package_name}' contains suspicious term(s) {matched_suffixes} "
                f"that legitimate banking apps typically do not use"
            )

    package_segments = package_lower.split(".")
    last_segment = package_segments[-1] if package_segments else ""
    if RANDOM_PACKAGE_REGEX.search(last_segment) or last_segment in {"app", "xyz", "test", "demo"}:
        score += 15
        reasons.append(
            f"Package name segment '{last_segment}' looks randomly generated or generic"
        )

    return {
        "impersonation_risk_score": min(score, 100),
        "reasons": reasons,
    }
