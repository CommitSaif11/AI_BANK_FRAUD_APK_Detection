import re

from androguard.misc import AnalyzeAPK

URL_IP_REGEX = re.compile(
    r"(?:https?://[^\s\"'<>]+)|"
    r"(?:\b(?:\d{1,3}\.){3}\d{1,3}\b)"
)


def extract_apk_info(apk_path: str) -> dict:
    a, d, dx = AnalyzeAPK(apk_path)

    cert_info = []
    for cert in a.get_certificates():
        cert_info.append({
            "issuer": cert.issuer.human_friendly,
            "subject": cert.subject.human_friendly,
        })

    urls_ips = set()
    for dex in d:
        for string in dex.get_strings():
            for match in URL_IP_REGEX.findall(str(string)):
                urls_ips.add(match)

    return {
        "package_name": a.get_package(),
        "app_name": a.get_app_name(),
        "permissions": a.get_permissions(),
        "activities": a.get_activities(),
        "services": a.get_services(),
        "receivers": a.get_receivers(),
        "certificates": cert_info,
        "urls_and_ips": sorted(urls_ips),
    }
