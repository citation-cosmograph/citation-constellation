"""
citation-constellation/app/components/score_panel.py
=====================================================
Score breakdown: donut chart + summary metrics.
"""

import plotly.graph_objects as go
from typing import Optional


CATEGORY_COLORS = {
    "self_citations": "#EF4444",
    "direct_coauthor_citations": "#F97316",
    "transitive_coauthor_citations": "#3B82F6",
    "same_dept_citations": "#EC4899",
    "same_institution_citations": "#A855F7",
    "same_parent_org_citations": "#06B6D4",
    "external_citations": "#22C55E",
    "unknown_citations": "#9CA3AF",
}

CATEGORY_LABELS = {
    "self_citations": "Self",
    "direct_coauthor_citations": "Direct co-author",
    "transitive_coauthor_citations": "Transitive co-author",
    "same_dept_citations": "Same department",
    "same_institution_citations": "Same institution",
    "same_parent_org_citations": "Same parent org",
    "external_citations": "External",
    "unknown_citations": "Unknown",
}


def build_score_donut(audit_data: dict) -> Optional[go.Figure]:
    """Build donut chart showing citation classification distribution."""
    score = audit_data.get("score", {})
    breakdown = score.get("breakdown", {})
    if not breakdown:
        return None

    labels, values, colors = [], [], []
    for key, label in CATEGORY_LABELS.items():
        val = breakdown.get(key, 0)
        if val > 0:
            labels.append(label)
            values.append(val)
            colors.append(CATEGORY_COLORS.get(key, "#999"))

    if not values:
        return None

    baron = score.get("baron_score", score.get("baron_v03", score.get("baron_v02", 0)))
    herocon = score.get("herocon_score", score.get("herocon_v03", score.get("herocon_v02", None)))

    center_text = f"BARON<br><b>{baron:.1f}%</b>"
    if herocon is not None:
        center_text += f"<br>HEROCON<br><b>{herocon:.1f}%</b>"

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>%{value} citations (%{percent})<extra></extra>",
    )])

    fig.update_layout(
        annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=14, showarrow=False)],
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=400,
        paper_bgcolor="white",
    )
    return fig


def format_score_summary(audit_data: dict) -> str:
    """Format score summary as markdown for display."""
    score = audit_data.get("score", {})
    breakdown = score.get("breakdown", {})
    researcher = audit_data.get("researcher", {})

    baron = score.get("baron_score", score.get("baron_v03", score.get("baron_v02", 0)))
    herocon = score.get("herocon_score", score.get("herocon_v03", score.get("herocon_v02", None)))
    phase = score.get("phase", audit_data.get("version", "?"))

    lines = [
        f"### {researcher.get('display_name', 'Unknown Researcher')}",
        f"**ORCID:** {researcher.get('orcid', 'N/A')} · **OpenAlex:** {researcher.get('openalex_id', 'N/A')} · **Works:** {researcher.get('works_count', '?')}",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| **BARON** | **{baron:.1f}%** |",
    ]
    if herocon is not None:
        gap = herocon - baron
        lines.append(f"| **HEROCON** | **{herocon:.1f}%** |")
        lines.append(f"| Gap (HEROCON − BARON) | {gap:.1f}% |")

    lines.extend([
        f"| Total citations | {breakdown.get('total_citations', '?')} |",
        f"| Classifiable | {breakdown.get('classifiable_citations', '?')} ({breakdown.get('data_quality_pct', '?')}%) |",
        f"| Reliability | **{breakdown.get('reliability', '?')}** |",
        f"| Phase | {phase} |",
    ])

    return "\n".join(lines)
