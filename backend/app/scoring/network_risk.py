import re

SUSPICIOUS_TLDS = [".tk", ".xyz", ".top", ".ml", ".ga", ".cf", ".gq"]

IP_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def check_network_risk(urls_and_ips: list) -> dict:
    flagged = []
    score = 0

    for entry in urls_and_ips:
        reasons = []

        if entry.lower().startswith("http://"):
            reasons.append("Uses non-HTTPS (plaintext HTTP) endpoint")
            score += 10

        host = re.sub(r"^https?://", "", entry, flags=re.IGNORECASE).split("/")[0]

        if IP_REGEX.match(host):
            reasons.append("Uses a raw IP address as an endpoint instead of a domain")
            score += 15
        else:
            for tld in SUSPICIOUS_TLDS:
                if host.lower().endswith(tld):
                    reasons.append(f"Uses suspicious top-level domain '{tld}'")
                    score += 15
                    break

        if reasons:
            flagged.append({"url": entry, "reasons": reasons})

    return {
        "network_risk_score": min(score, 100),
        "flagged_urls": flagged,
    }
