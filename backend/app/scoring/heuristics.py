RISKY_PERMISSIONS = {
    "android.permission.READ_SMS": (15, "Can read SMS messages, often used to steal OTPs"),
    "android.permission.SEND_SMS": (15, "Can send SMS messages, often used for premium SMS fraud"),
    "android.permission.RECEIVE_BOOT_COMPLETED": (10, "Can start automatically on device boot"),
    "android.permission.SYSTEM_ALERT_WINDOW": (20, "Can draw over other apps, often used for overlay attacks"),
    "android.permission.BIND_ACCESSIBILITY_SERVICE": (25, "Can access accessibility services, often abused for full device control"),
    "android.permission.REQUEST_INSTALL_PACKAGES": (15, "Can install other APKs, often used to drop additional malware"),
}

COMBO_RULES = [
    {
        "name": "otp_stealer_combo",
        "permissions": {
            "android.permission.READ_SMS",
            "android.permission.RECEIVE_BOOT_COMPLETED",
            "android.permission.SEND_SMS",
        },
        "bonus": 25,
        "reason": "READ_SMS + RECEIVE_BOOT_COMPLETED + SEND_SMS is typical of OTP-stealing trojans",
    },
]


def score_permissions(permissions: list) -> dict:
    perm_set = set(permissions)

    flagged = []
    score = 0
    for perm, (points, reason) in RISKY_PERMISSIONS.items():
        if perm in perm_set:
            flagged.append({"permission": perm, "points": points, "reason": reason})
            score += points

    triggered_combos = []
    for combo in COMBO_RULES:
        if combo["permissions"].issubset(perm_set):
            triggered_combos.append({
                "name": combo["name"],
                "bonus": combo["bonus"],
                "reason": combo["reason"],
            })
            score += combo["bonus"]

    return {
        "permission_risk_score": min(score, 100),
        "flagged_permissions": flagged,
        "triggered_combos": triggered_combos,
    }
