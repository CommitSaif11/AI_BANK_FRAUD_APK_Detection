import os
from pathlib import Path

KEYWORDS = [
    "accessibility", "overlay", "sms", "inject", "hook", "keylog", "steal",
    "password", "credential", "bank", "payment", "otp", "admin"
]
MAX_LENGTH = 3000

def extract_suspicious_code(jadx_output_dir: str) -> str:
    """
    Extracts suspicious Java code snippets from the JADX output directory.

    Args:
        jadx_output_dir: The path to the directory containing decompiled Java files.

    Returns:
        A single string containing the concatenated content of suspicious files,
        truncated to a maximum length. Returns an empty string if no relevant
        files are found.
    """
    if not jadx_output_dir or not Path(jadx_output_dir).is_dir():
        return ""

    suspicious_files = []
    for root, _, files in os.walk(jadx_output_dir):
        for file in files:
            if file.endswith(".java"):
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    hits = sum(keyword in content.lower() for keyword in KEYWORDS)
                    if hits > 0:
                        suspicious_files.append({"path": file_path, "hits": hits, "content": content})
                except Exception:
                    # Ignore files that can't be read
                    continue

    if not suspicious_files:
        return ""

    # Sort files by the number of keyword hits in descending order
    suspicious_files.sort(key=lambda x: x["hits"], reverse=True)

    # Combine content, prioritizing files with more hits
    combined_content = ""
    for file_info in suspicious_files:
        header = f"// File: {file_info['path'].relative_to(jadx_output_dir)}\n"
        if len(combined_content) + len(header) + len(file_info['content']) > MAX_LENGTH:
            remaining_len = MAX_LENGTH - len(combined_content) - len(header)
            if remaining_len > 100: # Only add if there's enough space for a meaningful snippet
                combined_content += header + file_info['content'][:remaining_len] + "\n// ... (truncated)\n"
            break
        else:
            combined_content += header + file_info['content'] + "\n\n"

    return combined_content.strip()
