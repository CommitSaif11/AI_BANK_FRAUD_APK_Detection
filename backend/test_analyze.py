import json
import sys

import requests

API_URL = "http://127.0.0.1:8000/analyze"


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_analyze.py <path-to-apk>")
        sys.exit(1)

    apk_path = sys.argv[1]

    with open(apk_path, "rb") as f:
        files = {"file": (apk_path.split("/")[-1].split("\\")[-1], f, "application/vnd.android.package-archive")}
        response = requests.post(API_URL, files=files)

    print(f"Status code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)


if __name__ == "__main__":
    main()
