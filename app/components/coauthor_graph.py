"""
citation-constellation/app/components/coauthor_graph.py
========================================================
Interactive force-directed co-author network graph using Plotly.

Nodes colored by distance: target=gold, depth-1=crimson, depth-2=steelblue.
Node size by shared papers. Edges by strength. Hover for details.
"""

import plotly.graph_objects as go
import networkx as nx
from typing import Optional


# ── Color scheme ──
COLORS = {
    0: "#FFD700",     # gold — target researcher
    1: "#DC143C",     # crimson — direct co-authors
    2: "#4682B4",     # steel blue — transitive co-authors
}
EDGE_COLOR = "rgba(150, 150, 150, 0.3)"
EDGE_HIGHLIGHT = "rgba(220, 20, 60, 0.6)"

# ── Size scaling ──
MIN_NODE_SIZE = 8
MAX_NODE_SIZE = 40
TARGET_NODE_SIZE = 50


def build_coauthor_graph(audit_data: dict, max_nodes: int = 150) -> Optional[go.Figure]:
    """
    Build an interactive co-author network graph from audit JSON data.

    Expects audit_data to contain 'coauthor_graph' with 'nodes' and 'edges'.
    For large networks (>max_nodes), only the top co-authors by strength are shown.
    Returns a plotly Figure or None if no graph data.
    """
    graph_data = audit_data.get("coauthor_graph")
    if not graph_data:
        return None

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        return None

    # ── Prune large graphs: keep target + top N by distance then strength ──
    total_before = len(nodes)
    if len(nodes) > max_nodes:
        # Always keep target (distance 0) and all depth-1
        target_nodes = [n for n in nodes if n.get("distance_from_target", 99) == 0]
        depth1_nodes = [n for n in nodes if n.get("distance_from_target", 99) == 1]
        depth2_nodes = [n for n in nodes if n.get("distance_from_target", 99) == 2]

        # Sort depth-2 by coauthorship strength (via edges) and take top N
        remaining_slots = max_nodes - len(target_nodes) - len(depth1_nodes)
        if remaining_slots > 0 and depth2_nodes:
            # Build a strength lookup from edges
            strength_lookup = {}
            for e in edges:
                strength_lookup[e["author_a"]["id"]] = max(
                    strength_lookup.get(e["author_a"]["id"], 0), e.get("strength", 0)
                )
                strength_lookup[e["author_b"]["id"]] = max(
                    strength_lookup.get(e["author_b"]["id"], 0), e.get("strength", 0)
                )
            depth2_nodes.sort(
                key=lambda n: strength_lookup.get(n["author_id"], 0), reverse=True
            )
            depth2_nodes = depth2_nodes[:remaining_slots]

        nodes = target_nodes + depth1_nodes + depth2_nodes

        # Filter edges to only include visible nodes
        visible_ids = {n["author_id"] for n in nodes}
        edges = [
            e for e in edges
            if e["author_a"]["id"] in visible_ids and e["author_b"]["id"] in visible_ids
        ]

    # Build networkx graph for layout
    G = nx.Graph()
    for node in nodes:
        G.add_node(node["author_id"], **node)
    for edge in edges:
        G.add_edge(
            edge["author_a"]["id"],
            edge["author_b"]["id"],
            weight=edge.get("strength", 1),
            shared_papers=edge.get("shared_papers", 1),
        )

    # Force-directed layout — use faster algorithm for large graphs
    try:
        if len(G.nodes) > 80:
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G, k=2.0, iterations=80, seed=42, weight="weight")
    except Exception:
        pos = nx.random_layout(G, seed=42)

    # Compute node sizes based on shared papers (for depth-1 nodes)
    max_papers = 1
    for node in nodes:
        co = node.get("coauthorship", {})
        papers = co.get("shared_papers", 0)
        if papers > max_papers:
            max_papers = papers

    # ── Build edge traces ──
    edge_traces = []
    for edge in edges:
        a_id = edge["author_a"]["id"]
        b_id = edge["author_b"]["id"]
        if a_id in pos and b_id in pos:
            x0, y0 = pos[a_id]
            x1, y1 = pos[b_id]
            strength = edge.get("strength", 1)
            width = max(0.5, min(4, strength / 2))
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode="lines",
                line=dict(width=width, color=EDGE_COLOR),
                hoverinfo="none",
                showlegend=False,
            ))

    # ── Build node traces (one per distance level for legend) ──
    traces_by_distance = {}
    for node in nodes:
        aid = node["author_id"]
        if aid not in pos:
            continue

        dist = node.get("distance_from_target", 99)
        color = COLORS.get(dist, "#999999")
        x, y = pos[aid]
        name = node.get("name", "Unknown")
        role = node.get("role", "")
        co = node.get("coauthorship", {})
        papers = co.get("shared_papers", 0)
        strength = co.get("strength", 0)

        # Node size
        if dist == 0:
            size = TARGET_NODE_SIZE
        elif dist == 1 and max_papers > 0:
            size = MIN_NODE_SIZE + (papers / max_papers) * (MAX_NODE_SIZE - MIN_NODE_SIZE)
        else:
            size = MIN_NODE_SIZE

        # Hover text
        hover_parts = [f"<b>{name}</b>"]
        if dist == 0:
            hover_parts.append("Target Researcher")
        else:
            hover_parts.append(f"Distance: {dist}")
        if papers:
            hover_parts.append(f"Shared papers: {papers}")
        if strength:
            hover_parts.append(f"Strength: {strength:.2f}")
        if co.get("last_collab_year"):
            hover_parts.append(f"Last collab: {co['last_collab_year']}")
        hover = "<br>".join(hover_parts)

        if dist not in traces_by_distance:
            label = {0: "Target", 1: "Direct co-authors", 2: "Transitive co-authors"}.get(dist, f"Depth {dist}")
            traces_by_distance[dist] = {
                "x": [], "y": [], "size": [], "hover": [],
                "color": color, "label": label,
            }

        traces_by_distance[dist]["x"].append(x)
        traces_by_distance[dist]["y"].append(y)
        traces_by_distance[dist]["size"].append(size)
        traces_by_distance[dist]["hover"].append(hover)

    # ── Assemble figure ──
    fig = go.Figure()

    # Add edges first (behind nodes)
    for trace in edge_traces:
        fig.add_trace(trace)

    # Add nodes by distance (for legend grouping)
    for dist in sorted(traces_by_distance.keys()):
        td = traces_by_distance[dist]
        fig.add_trace(go.Scatter(
            x=td["x"], y=td["y"],
            mode="markers",
            marker=dict(
                size=td["size"],
                symbol="star",
                color=td["color"],
                line=dict(width=1, color="white"),
                opacity=0.9,
            ),
            text=td["hover"],
            hoverinfo="text",
            name=td["label"],
        ))

    # ── Layout ──
    researcher_name = audit_data.get("researcher", {}).get("display_name", "Researcher")
    summary = graph_data.get("summary", {})
    subtitle = (
        f"{summary.get('direct_coauthors', '?')} direct · "
        f"{summary.get('transitive_coauthors', '?')} transitive · "
        f"{summary.get('total_edges', '?')} edges"
    )
    if total_before > len(nodes):
        subtitle += f" · showing top {len(nodes)}/{total_before} nodes"

    fig.update_layout(
        title=dict(
            text=f"Co-Author Network: {researcher_name}<br><sup>{subtitle}</sup>",
            font=dict(size=16),
        ),
        showlegend=True,
        legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.8)", bordercolor="rgba(0,0,0,0.1)", borderwidth=1,
        ),
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
        plot_bgcolor="rgba(248,249,250,1)",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20),
        height=600,
    )

    return fig
