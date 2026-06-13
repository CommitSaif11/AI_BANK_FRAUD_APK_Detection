import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.fingerprints.matcher import match_fingerprints

# Permissions overlapping heavily with Anatsa's typical_permissions.
test_permissions = [
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.INTERNET",
]

test_package_name = "com.docscanner.pdfapp"

test_urls = [
    "http://malicious-update.top/api",
]

result = match_fingerprints(test_permissions, test_package_name, test_urls)

print(json.dumps(result, indent=2))
