import json
import os
import re

# Load the fingerprint database once at module import time, not on every call.
_DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")
with open(_DB_PATH, "r", encoding="utf-8") as f:
    _FINGERPRINT_DB = json.load(f)


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    # Jaccard similarity = size of intersection / size of union.
    # If both sets are empty, union is empty too -> define similarity as 0.
    union = set_a | set_b
    if not union:
        return 0.0
    intersection = set_a & set_b
    return len(intersection) / len(union)


def _matches_any_pattern(value: str, patterns: list) -> bool:
    for pattern in patterns:
        if re.search(pattern, value):
            return True
    return False


def match_fingerprints(extracted_permissions: list, package_name: str, extracted_urls: list) -> dict:
    # Normalize inputs in case empty lists / None are passed in.
    extracted_permissions = extracted_permissions or []
    extracted_urls = extracted_urls or []
    package_name = package_name or ""

    extracted_perm_set = set(extracted_permissions)

    all_scores = []
    best_entry = None
    best_score = -1.0
    best_permission_overlap = []
    best_package_match = False
    best_url_match = False

    for entry in _FINGERPRINT_DB:
        typical_perm_set = set(entry.get("typical_permissions", []))

        # a. Permission similarity via Jaccard index.
        permission_similarity = _jaccard_similarity(extracted_perm_set, typical_perm_set)
        permission_overlap = sorted(extracted_perm_set & typical_perm_set)

        # b. Package name match: does package_name match any known pattern for this family?
        package_match = _matches_any_pattern(package_name, entry.get("package_name_patterns", []))

        # c. URL/C2 match: does any extracted URL match any known C2 pattern for this family?
        c2_patterns = entry.get("known_c2_patterns", [])
        url_match = any(_matches_any_pattern(url, c2_patterns) for url in extracted_urls)

        # Combine the three signals using fixed weights.
        combined_score = (
            permission_similarity * 0.5
            + (1.0 if package_match else 0.0) * 0.3
            + (1.0 if url_match else 0.0) * 0.2
        )

        all_scores.append({
            "family_name": entry["family_name"],
            "score": combined_score,
        })

        if combined_score > best_score:
            best_score = combined_score
            best_entry = entry
            best_permission_overlap = permission_overlap
            best_package_match = package_match
            best_url_match = url_match

    confidence = best_score * 100 if best_entry is not None else 0.0

    if confidence < 20:
        return {
            "matched_family": "No significant match",
            "confidence": confidence,
            "matched_permission_overlap": best_permission_overlap,
            "matched_package_pattern": best_package_match,
            "matched_url_pattern": best_url_match,
            "description": None,
            "all_scores": all_scores,
        }

    return {
        "matched_family": best_entry["family_name"],
        "confidence": confidence,
        "matched_permission_overlap": best_permission_overlap,
        "matched_package_pattern": best_package_match,
        "matched_url_pattern": best_url_match,
        "description": best_entry["description"],
        "all_scores": all_scores,
    }
