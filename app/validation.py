"""
citation-constellation/app/validation.py
==========================================
Input validation for ORCID, OpenAlex IDs, and other parameters.
Returns (is_valid, cleaned_value_or_error_message).
"""

import re
from datetime import datetime


# ============================================================
# ORCID Validation
# ============================================================

ORCID_PATTERN = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def _orcid_checksum(orcid: str) -> bool:
    """Validate ORCID check digit using ISO 7064 Mod 11,2."""
    digits = orcid.replace("-", "")
    total = 0
    for char in digits[:-1]:
        total = (total + int(char)) * 2
    check = (12 - (total % 11)) % 11
    expected = "X" if check == 10 else str(check)
    return digits[-1] == expected


def validate_orcid(value: str) -> tuple[bool, str]:
    """Validate ORCID format and checksum. Returns (ok, cleaned_or_error)."""
    value = value.strip()
    # Strip URL prefix if pasted as URL
    value = value.replace("https://orcid.org/", "").replace("http://orcid.org/", "")
    if not ORCID_PATTERN.match(value):
        return False, (
            "Invalid ORCID format. Expected: 0000-0000-0000-0000 "
            "(four groups of four digits separated by hyphens, "
            "last character may be X)."
        )
    if not _orcid_checksum(value):
        return False, (
            f"ORCID checksum failed for '{value}'. "
            "Please double-check the ID — one or more digits may be wrong."
        )
    return True, value


# ============================================================
# OpenAlex ID Validation
# ============================================================

OPENALEX_AUTHOR_PATTERN = re.compile(r"^A\d{3,15}$")


def validate_openalex_id(value: str) -> tuple[bool, str]:
    """Validate OpenAlex author ID format. Returns (ok, cleaned_or_error)."""
    value = value.strip()
    # Strip URL prefix if pasted as URL
    value = value.replace("https://openalex.org/", "")
    if not OPENALEX_AUTHOR_PATTERN.match(value):
        return False, (
            "Invalid OpenAlex author ID format. Expected: 'A' followed by digits "
            "(e.g., A5100390903). You can find your OpenAlex ID at openalex.org."
        )
    return True, value


# ============================================================
# Identifier Detection (auto-detect ORCID vs OpenAlex)
# ============================================================

def validate_identifier(value: str) -> tuple[bool, str, str]:
    """
    Auto-detect and validate an identifier.
    Returns (ok, cleaned_or_error, id_type) where id_type is 'orcid' or 'openalex'.
    """
    value = value.strip()
    if not value:
        return False, "Please enter an ORCID or OpenAlex author ID.", ""

    # Try ORCID first (has hyphens or starts with digit)
    cleaned = value.replace("https://orcid.org/", "").replace("http://orcid.org/", "")
    if "-" in cleaned or cleaned[0].isdigit():
        ok, result = validate_orcid(cleaned)
        return ok, result, "orcid"

    # Try OpenAlex
    cleaned = value.replace("https://openalex.org/", "")
    if cleaned.startswith("A"):
        ok, result = validate_openalex_id(cleaned)
        return ok, result, "openalex"

    return False, (
        "Could not recognize identifier format. "
        "Enter an ORCID (e.g., 0000-0000-0000-0000) or "
        "OpenAlex ID (e.g., A5100390903)."
    ), ""


# ============================================================
# Other Parameter Validation
# ============================================================

def validate_since_year(value) -> tuple[bool, str]:
    """Validate --since year parameter."""
    if value is None or value == "" or value == 0:
        return True, ""  # optional field
    try:
        year = int(value)
    except (ValueError, TypeError):
        return False, f"'{value}' is not a valid year. Enter a four-digit year (e.g., 2010)."
    current_year = datetime.now().year
    if year < 1900 or year > current_year:
        return False, f"Year must be between 1900 and {current_year}."
    return True, str(year)


def validate_depth(value) -> tuple[bool, str]:
    """Validate co-author graph depth."""
    try:
        depth = int(value)
    except (ValueError, TypeError):
        return False, "Depth must be 1, 2, or 3."
    if depth not in (1, 2, 3):
        return False, "Depth must be 1, 2, or 3."
    return True, str(depth)


# ============================================================
# Name Cleaning (strip academic titles for filenames)
# ============================================================

TITLE_PREFIXES = [
    "Professor ", "Prof. ", "Prof ",
    "Doctor ", "Dr. ", "Dr ",
    "Associate Professor ", "Assoc. Prof. ",
    "Assistant Professor ", "Asst. Prof. ",
]


def strip_title(name: str) -> str:
    """Remove academic title prefixes from a display name."""
    for prefix in TITLE_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    return name.strip()


def sanitize_filename(name: str) -> str:
    """Convert a display name to a safe filename component."""
    name = strip_title(name)
    # Replace spaces and special chars with hyphens
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s]+", "-", name)
    return name.strip("-")
