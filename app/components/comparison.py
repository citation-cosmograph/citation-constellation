"""
citation-constellation/app/components/comparison.py
====================================================
Side-by-side comparison of multiple researcher audit reports.
"""

import pandas as pd
from typing import Optional


def build_comparison_table(reports: list[dict]) -> Optional[pd.DataFrame]:
    """
    Build a comparison table from multiple audit JSON reports.
    Returns a DataFrame with one row per researcher.
    """
    if not reports:
        return None

    rows = []
    for report in reports:
        researcher = report.get("researcher", {})
        score = report.get("score", {})
        breakdown = score.get("breakdown", {})

        baron = score.get("baron_score", score.get("baron_v03", score.get("baron_v02", 0)))
        herocon = score.get("herocon_score", score.get("herocon_v03", score.get("herocon_v02", None)))
        gap = (herocon - baron) if herocon is not None else None

        rows.append({
            "Researcher": researcher.get("display_name", "Unknown"),
            "ORCID": researcher.get("orcid", "N/A"),
            "Works": researcher.get("works_count", "?"),
            "Total Citations": breakdown.get("total_citations", "?"),
            "BARON": f"{baron:.1f}%",
            "HEROCON": f"{herocon:.1f}%" if herocon is not None else "—",
            "Gap": f"{gap:.1f}%" if gap is not None else "—",
            "Reliability": breakdown.get("reliability", "?"),
            "Data Quality": f"{breakdown.get('data_quality_pct', '?')}%",
            "Self-cite %": f"{breakdown.get('self_citation_pct', '?')}%",
            "External %": f"{breakdown.get('external_pct', '?')}%",
        })

    return pd.DataFrame(rows)


def parse_multiple_reports(json_contents: list[str]) -> tuple[list[dict], list[str]]:
    """
    Parse multiple JSON strings into report dicts.
    Returns (valid_reports, error_messages).
    """
    import json

    reports = []
    errors = []

    for i, content in enumerate(json_contents):
        try:
            data = json.loads(content)
            # Validate it looks like a BARON/HEROCON audit file
            if "score" not in data and "researcher" not in data:
                errors.append(f"File {i+1}: Does not appear to be a BARON/HEROCON audit report (missing 'score' or 'researcher' fields).")
                continue
            reports.append(data)
        except json.JSONDecodeError as e:
            errors.append(f"File {i+1}: Invalid JSON — {str(e)[:100]}")

    return reports, errors
