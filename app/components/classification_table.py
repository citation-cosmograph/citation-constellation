"""
citation-constellation/app/components/classification_table.py
==============================================================
Sortable citation classification table for Gradio Dataframe.
Includes export helpers for Excel and JSON download.
"""

import json
import os
import tempfile
from io import BytesIO
from typing import Optional

import pandas as pd


def build_classification_dataframe(audit_data: dict, max_rows: int = 500) -> Optional[pd.DataFrame]:
    """
    Build a pandas DataFrame from audit classifications for display.
    Returns None if no classifications found.
    Limits to max_rows for UI performance (full data is in the JSON download).
    """
    classifications = audit_data.get("classifications", [])
    if not classifications:
        return None

    total = len(classifications)
    show = classifications[:max_rows]

    rows = []
    for cls in show:
        citing = cls.get("citing_work", {})
        cited = cls.get("cited_work", {})

        # Build compact rationale from classification + key metadata
        classification = cls.get("classification", "?")
        meta = cls.get("metadata", {})
        short_rationale = _compact_rationale(classification, meta)

        rows.append({
            "Citing Paper": _truncate(citing.get("title", "Unknown"), 50),
            "Year": citing.get("year", ""),
            "Cited Paper": _truncate(cited.get("title", "Unknown"), 45),
            "Class": classification,
            "Conf.": f"{cls.get('confidence', 0):.0%}",
            "Detail": short_rationale,
        })

    df = pd.DataFrame(rows)
    if total > max_rows:
        df = pd.concat([df, pd.DataFrame([{
            "Citing Paper": f"... {total - max_rows} more (see JSON)",
            "Year": "", "Cited Paper": "", "Class": "",
            "Conf.": "", "Detail": "",
        }])], ignore_index=True)
    return df


def build_classification_summary(audit_data: dict) -> Optional[pd.DataFrame]:
    """Build a compact summary table of classification counts."""
    score = audit_data.get("score", {})
    breakdown = score.get("breakdown", {})
    if not breakdown:
        return None

    herocon_weights = score.get("herocon_weights", {})

    categories = [
        ("Self", "self_citations", "SELF"),
        ("Direct co-author", "direct_coauthor_citations", "DIRECT_COAUTHOR"),
        ("Transitive co-author", "transitive_coauthor_citations", "TRANSITIVE_COAUTHOR"),
        ("Same department", "same_dept_citations", "SAME_DEPT"),
        ("Same institution", "same_institution_citations", "SAME_INSTITUTION"),
        ("Same parent org", "same_parent_org_citations", "SAME_PARENT_ORG"),
        ("External", "external_citations", "EXTERNAL"),
        ("Unknown", "unknown_citations", "UNKNOWN"),
    ]

    rows = []
    total = breakdown.get("total_citations", 0)
    for label, key, weight_key in categories:
        count = breakdown.get(key, 0)
        if count > 0:
            pct = count / total * 100 if total > 0 else 0
            weight = herocon_weights.get(weight_key, "—")
            if weight_key == "UNKNOWN":
                weight = "excluded"
            rows.append({
                "Category": label,
                "Count": count,
                "% of Total": f"{pct:.1f}%",
                "HEROCON Weight": weight,
            })

    return pd.DataFrame(rows)


# ============================================================
# Export Helpers
# ============================================================

def export_classifications_excel(audit_data: dict) -> Optional[str]:
    """
    Export full classifications + summary to an Excel file with two sheets.
    Returns filepath or None.
    """
    classifications = audit_data.get("classifications", [])
    if not classifications:
        return None

    # Full classification rows (no truncation for export)
    cls_rows = []
    for cls in classifications:
        citing = cls.get("citing_work", {})
        cited = cls.get("cited_work", {})
        meta = cls.get("metadata", {})

        # Citing authors as comma-separated names
        citing_authors = ", ".join(
            a.get("name", "") for a in citing.get("authors", [])
        )

        cls_rows.append({
            "Citing Paper": citing.get("title", "Unknown"),
            "Citing Year": citing.get("year", ""),
            "Citing Authors": citing_authors,
            "Cited Paper": cited.get("title", "Unknown"),
            "Cited Year": cited.get("year", ""),
            "Classification": cls.get("classification", ""),
            "Confidence": cls.get("confidence", ""),
            "Phase": cls.get("phase_detected", ""),
            "Rationale": cls.get("rationale", ""),
            "Closest Author": meta.get("closest_author_name", ""),
            "Closest Author ID": meta.get("closest_author_id", ""),
            "Institution": meta.get("citing_institution", ""),
        })

    cls_df = pd.DataFrame(cls_rows)

    # Summary sheet
    summary_df = build_classification_summary(audit_data)

    # Write to temp Excel file
    tmpdir = os.environ.get("GRADIO_TEMP_DIR", tempfile.gettempdir())
    os.makedirs(tmpdir, exist_ok=True)

    researcher_name = audit_data.get("researcher", {}).get("display_name", "researcher")
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in researcher_name)
    filepath = os.path.join(tmpdir, f"{safe_name}_citations.xlsx")

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        cls_df.to_excel(writer, sheet_name="All Citations", index=False)
        if summary_df is not None:
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

    return filepath


def export_classifications_json(audit_data: dict) -> Optional[str]:
    """
    Export classifications as a clean JSON file.
    Returns filepath or None.
    """
    classifications = audit_data.get("classifications", [])
    if not classifications:
        return None

    tmpdir = os.environ.get("GRADIO_TEMP_DIR", tempfile.gettempdir())
    os.makedirs(tmpdir, exist_ok=True)

    researcher_name = audit_data.get("researcher", {}).get("display_name", "researcher")
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in researcher_name)
    filepath = os.path.join(tmpdir, f"{safe_name}_citations.json")

    export = {
        "researcher": audit_data.get("researcher", {}),
        "score_summary": audit_data.get("score", {}).get("breakdown", {}),
        "total_classifications": len(classifications),
        "classifications": classifications,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    return filepath


# ============================================================
# Internal Helpers
# ============================================================

def _compact_rationale(classification: str, meta: dict) -> str:
    """Short rationale for table display — keeps things narrow."""
    if classification == "SELF":
        return "Self-citation"
    elif classification == "DIRECT_COAUTHOR":
        name = meta.get("closest_author_name") or ""
        if name:
            return f"Co-author: {_truncate(name, 25)}"
        return "Direct co-author"
    elif classification == "TRANSITIVE_COAUTHOR":
        dist = meta.get("graph_distance", 2)
        name = meta.get("closest_author_name") or ""
        if name:
            return f"Transitive (d={dist}): {_truncate(name, 20)}"
        return f"Transitive co-author (d={dist})"
    elif classification == "SAME_DEPT":
        inst = meta.get("citing_institution", "")
        return f"Same dept: {_truncate(inst, 25)}" if inst else "Same department"
    elif classification == "SAME_INSTITUTION":
        inst = meta.get("citing_institution", "")
        return f"Same inst: {_truncate(inst, 25)}" if inst else "Same institution"
    elif classification == "SAME_PARENT_ORG":
        inst = meta.get("citing_institution", "")
        return f"Same org: {_truncate(inst, 25)}" if inst else "Same parent org"
    elif classification == "UNKNOWN":
        return "Insufficient data"
    elif classification == "EXTERNAL":
        return "External"
    return classification


def _truncate(text, max_len: int) -> str:
    if not text:
        return "Unknown"
    text = str(text)
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text
