"""
citation-constellation/app/confirmation.py
============================================
Paper discard confirmation workflow.

When confirm_discard=True and ORCID validation flags works,
the pipeline pauses and returns a list for user review.

CLI mode: prints numbered list, accepts "1-5,8,12" or "all" or "none"
UI mode: returns structured data for Gradio checkbox rendering
"""

from typing import Optional


def format_flagged_works_for_display(flagged_works: list[dict]) -> list[dict]:
    """
    Format flagged works from OrcidValidator into a display-friendly list.

    Each entry has: index, openalex_id, title, year, reason, affiliations
    """
    display = []
    for i, fw in enumerate(flagged_works):
        w = fw.get("work", {})
        title = w.get("title", "Untitled")
        if len(title) > 80:
            title = title[:77] + "..."
        display.append({
            "index": i + 1,
            "openalex_id": w.get("id", "").replace("https://openalex.org/", ""),
            "title": title,
            "year": w.get("publication_year", "?"),
            "reason": fw.get("reason", "Unknown reason"),
            "affiliations": fw.get("unknown_affiliations", []),
        })
    return display


def format_since_excluded_for_display(since_excluded: list[dict]) -> list[dict]:
    """Format works excluded by --since for display."""
    display = []
    for i, w in enumerate(since_excluded):
        title = w.get("title", "Untitled")
        if len(title) > 80:
            title = title[:77] + "..."
        display.append({
            "index": i + 1,
            "openalex_id": w.get("id", "").replace("https://openalex.org/", ""),
            "title": title,
            "year": w.get("publication_year", "?"),
        })
    return display


def parse_cli_selection(input_str: str, total: int) -> list[int]:
    """
    Parse CLI selection input into list of 0-based indices.

    Accepts:
        "all"       → all indices
        "none"      → empty list (keep all)
        "1,3,5"     → specific indices
        "1-5,8,12"  → ranges and individual indices
    """
    input_str = input_str.strip().lower()
    if input_str == "all":
        return list(range(total))
    if input_str in ("none", ""):
        return []

    indices = set()
    for part in input_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                start, end = int(start.strip()), int(end.strip())
                for i in range(start, end + 1):
                    if 1 <= i <= total:
                        indices.add(i - 1)  # convert to 0-based
            except ValueError:
                continue
        else:
            try:
                i = int(part)
                if 1 <= i <= total:
                    indices.add(i - 1)
            except ValueError:
                continue

    return sorted(indices)


def apply_exclusions(
    works_to_use: list[dict],
    flagged_works: list[dict],
    exclude_indices: list[int],
) -> list[dict]:
    """
    Apply user-selected exclusions to the works list.

    exclude_indices: 0-based indices into flagged_works that the user
    wants to EXCLUDE from scoring.
    """
    if not exclude_indices:
        return works_to_use  # keep everything

    exclude_ids = set()
    for i in exclude_indices:
        if i < len(flagged_works):
            w = flagged_works[i].get("work", {})
            wid = w.get("id", "")
            if wid:
                exclude_ids.add(wid)

    return [w for w in works_to_use if w.get("id", "") not in exclude_ids]
