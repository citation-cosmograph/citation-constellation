"""
citation-constellation/app/components/trajectory_chart.py
==========================================================
Career trajectory chart: BARON and HEROCON scores over time.
Shaded gap between them. Hover for year, citations, scores.
"""

import plotly.graph_objects as go
from typing import Optional
import plotly


BARON_COLOR = "#EAB308"     # amber/yellow
HEROCON_COLOR = "#22C55E"   # green
GAP_COLOR = "rgba(34, 197, 94, 0.15)"  # light green fill


def build_trajectory_chart(
    audit_data: dict,
    researcher_name: str = "",
) -> Optional[go.Figure]:
    """
    Build career trajectory chart from audit JSON data.
    Expects audit_data['trajectory'] list with year, baron, herocon, total_citations.
    """
    trajectory = audit_data.get("trajectory", [])
    if not trajectory:
        return None

    years = []
    baron_vals = []
    herocon_vals = []
    citations = []
    baron_valid = []
    herocon_valid = []

    for row in trajectory:
        y = row.get("year")
        if y is None:
            continue
        years.append(y)
        citations.append(row.get("total_citations", 0))

        b = row.get("baron")
        h = row.get("herocon")
        baron_vals.append(b)
        herocon_vals.append(h)
        if b is not None:
            baron_valid.append((y, b))
        if h is not None:
            herocon_valid.append((y, h))

    if not baron_valid:
        return None

    fig = go.Figure()

    # ── Shaded gap area (between BARON and HEROCON) ──
    if herocon_valid and baron_valid:
        gap_years = [y for y, _ in baron_valid if any(hy == y for hy, _ in herocon_valid)]
        gap_baron = [b for y, b in baron_valid if y in gap_years]
        gap_herocon = [h for y, h in herocon_valid if y in gap_years]

        if gap_years:
            fig.add_trace(go.Scatter(
                x=gap_years + gap_years[::-1],
                y=gap_herocon + gap_baron[::-1],
                fill="toself",
                fillcolor=GAP_COLOR,
                line=dict(width=0),
                showlegend=True,
                name="Gap (inner circle effect)",
                hoverinfo="skip",
            ))

    # ── BARON line ──
    bx = [y for y, _ in baron_valid]
    by = [v for _, v in baron_valid]
    fig.add_trace(go.Scatter(
        x=bx, y=by,
        mode="lines+markers",
        name="BARON",
        line=dict(color=BARON_COLOR, width=3),
        marker=dict(size=7, color=BARON_COLOR),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "BARON: %{y:.1f}%<br>"
            "<extra></extra>"
        ),
    ))

    # ── HEROCON line ──
    if herocon_valid:
        hx = [y for y, _ in herocon_valid]
        hy = [v for _, v in herocon_valid]
        fig.add_trace(go.Scatter(
            x=hx, y=hy,
            mode="lines+markers",
            name="HEROCON",
            line=dict(color=HEROCON_COLOR, width=3),
            marker=dict(size=7, color=HEROCON_COLOR),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "HEROCON: %{y:.1f}%<br>"
                "<extra></extra>"
            ),
        ))

    # ── Citation count on secondary axis ──
    fig.add_trace(go.Bar(
        x=years,
        y=citations,
        name="Cumulative citations",
        marker_color="rgba(156, 163, 175, 0.3)",
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Citations: %{y}<extra></extra>",
    ))

    # ── Layout ──
    name = researcher_name or audit_data.get("researcher", {}).get("display_name", "")
    fig.update_layout(
        title=dict(
            text=f"Career Trajectory: {name}" if name else "Career Trajectory",
            font=dict(size=16),
        ),
        xaxis=dict(title="Year", dtick=1, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(
            title="Score (%)", range=[0, 105],
            gridcolor="rgba(0,0,0,0.08)",
        ),
        yaxis2=dict(
            title="Cumulative Citations",
            overlaying="y", side="right",
            showgrid=False, range=[0, max(citations) * 1.3] if citations else [0, 100],
        ),
        legend=dict(
            yanchor="bottom", y=0.01, xanchor="right", x=0.99,
            bgcolor="rgba(255,255,255,0.8)",
        ),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=60, t=50, b=40),
        height=450,
    )

    return fig


def build_baron_comparison_trajectory(
    reports: list[dict],
) -> Optional[go.Figure]:
    """
    Overlay multiple researchers' BARON trajectories on one chart.
    """
    if not reports:
        return None

    num_reports = len(reports)
    if num_reports == 1:
        colors = plotly.colors.sample_colorscale("Turbo", [0.5])
    else:
        colors = plotly.colors.sample_colorscale("Turbo", [i / (num_reports - 1) for i in range(num_reports)])
    
    fig = go.Figure()

    for i, report in enumerate(reports):
        trajectory = report.get("trajectory", [])
        name = report.get("researcher", {}).get("display_name", f"Researcher {i+1}")
        color = colors[i]

        baron_pts = [(r["year"], r["baron"]) for r in trajectory if r.get("baron") is not None]
        if baron_pts:
            fig.add_trace(go.Scatter(
                x=[y for y, _ in baron_pts],
                y=[v for _, v in baron_pts],
                mode="lines+markers",
                name=f"{name} (BARON)",
                line=dict(color=color, width=2.5),
                marker=dict(size=6),
            ))

    fig.update_layout(
        title="BARON Trajectory Comparison",
        xaxis=dict(title="Year", gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(title="BARON Score (%)", range=[0, 105], gridcolor="rgba(0,0,0,0.08)"),
        legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=0.99),
        hovermode="x unified",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=40),
        height=450,
    )
    return fig


def build_herocon_comparison_trajectory(
    reports: list[dict],
) -> Optional[go.Figure]:
    """
    Overlay multiple researchers' HEROCON trajectories on one chart.
    """
    if not reports:
        return None

    num_reports = len(reports)
    if num_reports == 1:
        colors = plotly.colors.sample_colorscale("Turbo", [0.5])
    else:
        colors = plotly.colors.sample_colorscale("Turbo", [i / (num_reports - 1) for i in range(num_reports)])
        
    fig = go.Figure()

    for i, report in enumerate(reports):
        trajectory = report.get("trajectory", [])
        name = report.get("researcher", {}).get("display_name", f"Researcher {i+1}")
        color = colors[i]

        herocon_pts = [(r["year"], r["herocon"]) for r in trajectory if r.get("herocon") is not None]
        if herocon_pts:
            fig.add_trace(go.Scatter(
                x=[y for y, _ in herocon_pts],
                y=[v for _, v in herocon_pts],
                mode="lines+markers",
                name=f"{name} (HEROCON)",
                line=dict(color=color, width=2.5),
                marker=dict(size=6),
            ))

    fig.update_layout(
        title="HEROCON Trajectory Comparison",
        xaxis=dict(title="Year", gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(title="HEROCON Score (%)", range=[0, 105], gridcolor="rgba(0,0,0,0.08)"),
        legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=0.99),
        hovermode="x unified",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=40),
        height=450,
    )
    return fig