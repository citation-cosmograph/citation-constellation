"""
citation-constellation/phase2.py
=================================
Phase 2: Co-Author Network Detection

Builds on Phase 1 by constructing a co-authorship graph from the
target researcher's publications. Citations are then classified
based on the graph distance between the citing author and the target:

    Distance 0 → SELF              (target is an author on the citing work)
    Distance 1 → DIRECT_COAUTHOR   (citing author shared ≥1 paper with target)
    Distance 2 → TRANSITIVE_COAUTHOR (citing author is a co-author's co-author)
    No path   → EXTERNAL           (no co-authorship connection found)

This phase introduces HEROCON scoring alongside BARON. BARON remains
binary (in-group=0, external=1), while HEROCON gives graduated partial
credit to co-author citations using configurable weights.

The pipeline shows progressive scores: first the Phase 1 (self-citation)
score, then the Phase 2 (co-author) score with the delta, so the user
can see exactly how much their score dropped at each detection step.

Important limitation: the co-author graph is built ONLY from the target
researcher's own publications. Co-author A's other collaborators are
invisible unless they also appear on the target's papers. This makes
the graph a conservative undercount of the true transitive network.

Usage:
    python phase2.py --orcid 0000-0000-0000-0000
    python phase2.py --orcid 0000-0000-0000-0000 --depth 3
    python phase2.py --orcid 0000-0000-0000-0000 --trajectory
    python phase2.py --orcid 0000-0000-0000-0000 --export results.json

Requirements:
    pip install -r requirements.txt
"""

import asyncio
import json
import math
import time
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

from models import (
    Researcher, Work, Citation, CitationClassification,
    CoAuthorEdge, ScoreBreakdown, ScoreResult,
    HEROCON_WEIGHTS, compute_herocon_score, load_herocon_weights, DISCLAIMER,
    parse_author, parse_work, parse_work_authors,
)
from client import OpenAlexClient
from audit import AuditLog
from orcid_validate import OrcidValidator


# ============================================================
# Co-Author Graph
# ============================================================

class CoAuthorGraph:
    """
    Undirected weighted co-authorship graph.

    Nodes are authors (OpenAlex IDs). Edges represent co-authorship,
    weighted by the number of shared papers and recency of collaboration.
    The graph is built incrementally by calling add_paper() for each
    of the target researcher's publications.

    The graph stores edges in both directions (adj[a][b] and adj[b][a])
    for efficient BFS traversal, but they represent the same relationship.

    Key operations:
      - add_paper(): Register all pairwise co-authorships from a paper
      - bfs(): Compute shortest-path distances from target to all reachable nodes
      - top_coauthors(): Get the most prolific collaborators for audit display
    """

    def __init__(self):
        self.adj: dict[str, dict[str, CoAuthorEdge]] = defaultdict(dict)
        self.names: dict[str, str] = {}  # author_id → display_name

    def add_paper(self, author_ids, author_names, year, work_id):
        """
        Register all pairwise co-authorship edges from a single paper.

        For a paper with N authors, this creates N×(N-1)/2 edges
        (or updates existing edges with new shared paper count and year).

        Args:
            author_ids: List of OpenAlex author IDs on this paper.
            author_names: Parallel list of author display names.
            year: Publication year (for collaboration recency tracking).
            work_id: OpenAlex work ID (logged in edge metadata).
        """
        # Record author names for display purposes
        for i, aid in enumerate(author_ids):
            if i < len(author_names):
                self.names[aid] = author_names[i]

        # Create/update edges for every pair of co-authors
        for i in range(len(author_ids)):
            for j in range(i + 1, len(author_ids)):
                a, b = author_ids[i], author_ids[j]
                self._add_edge(a, b, year, work_id)

    def _add_edge(self, a, b, year, work_id):
        """
        Create or update an edge between two authors.

        Edges are stored in both directions for BFS efficiency.
        Each call increments shared_papers and updates the year range.
        """
        for src, dst in [(a, b), (b, a)]:
            if dst not in self.adj[src]:
                self.adj[src][dst] = CoAuthorEdge(author_a_id=src, author_b_id=dst)
            edge = self.adj[src][dst]
            edge.shared_papers += 1
            edge.shared_work_ids.append(work_id)
            if year:
                if edge.first_collab_year is None or year < edge.first_collab_year:
                    edge.first_collab_year = year
                if edge.last_collab_year is None or year > edge.last_collab_year:
                    edge.last_collab_year = year

    def bfs(self, start, max_depth=2):
        """
        Breadth-first search from a starting node up to max_depth hops.

        Returns a dict mapping each reachable author_id to their shortest
        distance from the start node. The start node itself has distance 0.

        Args:
            start: Starting author ID (typically the target researcher).
            max_depth: Maximum number of hops to traverse (1, 2, or 3).

        Returns:
            Dict[str, int] mapping author_id → distance from start.
        """
        visited = {start: 0}
        queue = [start]
        while queue:
            next_q = []
            for node in queue:
                depth = visited[node]
                if depth >= max_depth:
                    continue  # Don't expand beyond max_depth
                for neighbor in self.adj.get(node, {}):
                    if neighbor not in visited:
                        visited[neighbor] = depth + 1
                        next_q.append(neighbor)
            queue = next_q
        return visited

    def get_edge(self, a, b):
        """Get the edge between two authors, or None if no edge exists."""
        return self.adj.get(a, {}).get(b)

    @property
    def node_count(self):
        """Total number of unique authors in the graph."""
        return len(self.adj)

    @property
    def edge_count(self):
        """Total number of unique co-authorship edges (undirected)."""
        seen = set()
        count = 0
        for src, neighbors in self.adj.items():
            for dst in neighbors:
                pair = tuple(sorted([src, dst]))
                if pair not in seen:
                    seen.add(pair)
                    count += 1
        return count

    def top_coauthors(self, target_id, n=10):
        """
        Get the top N co-authors by shared paper count.

        Args:
            target_id: The target researcher's OpenAlex ID.
            n: Number of top co-authors to return.

        Returns:
            List of (author_id, display_name, CoAuthorEdge) tuples,
            sorted by shared_papers descending.
        """
        edges = []
        for nid, edge in self.adj.get(target_id, {}).items():
            edges.append((nid, self.names.get(nid, nid), edge))
        edges.sort(key=lambda x: -x[2].shared_papers)
        return edges[:n]


# ============================================================
# Classifiers
# ============================================================

class SelfCitationClassifier:
    """
    Phase 1 classifier (used as the first pass in Phase 2's progressive display).

    Identical to phase1.SelfCitationClassifier — duplicated here to avoid
    a circular import and to keep Phase 2 self-contained.
    """

    def __init__(self, target_id):
        self.target_id = target_id

    def classify(self, citing_work, cited_work):
        """Classify a citation as SELF or NON_SELF based on author ID match."""
        is_self = self.target_id in citing_work.author_ids
        return CitationClassification(
            citing_work_id=citing_work.openalex_id,
            cited_work_id=cited_work.openalex_id,
            classification="SELF" if is_self else "NON_SELF",
            confidence=1.0, phase_detected=1,
            metadata={"matching_author_ids": [self.target_id] if is_self else []},
        )


class CoAuthorClassifier:
    """
    Phase 2 classifier: uses the co-author graph to classify citations.

    For each citation, finds the closest co-author among the citing work's
    authors (by graph distance from the target researcher). Classification
    is based on this shortest distance:

        Distance 0 → SELF
        Distance 1 → DIRECT_COAUTHOR
        Distance 2 → TRANSITIVE_COAUTHOR (if within max_depth)
        No path    → EXTERNAL

    For DIRECT_COAUTHOR classifications, the metadata includes the
    co-authorship strength (shared papers × recency decay) and the
    specific collaboration history — all logged in the audit trail.
    """

    def __init__(self, target_id, graph, max_depth=2):
        """
        Args:
            target_id: Target researcher's OpenAlex ID.
            graph: The constructed CoAuthorGraph.
            max_depth: Maximum graph depth for in-group classification.
        """
        self.target_id = target_id
        self.graph = graph
        self.distances = graph.bfs(target_id, max_depth)
        self.max_depth = max_depth

    def classify(self, citing_work, cited_work):
        """
        Classify a single citation based on co-author graph distance.

        Scans all authors on the citing work to find the one closest
        to the target researcher in the co-author graph. The closest
        distance determines the classification.

        Args:
            citing_work: The paper that contains the citation.
            cited_work: The target researcher's paper being cited.

        Returns:
            CitationClassification with appropriate label and metadata.
        """
        # Find the closest co-author among the citing work's authors
        best_distance = None
        best_author_id = None
        for aid in citing_work.author_ids:
            dist = self.distances.get(aid)
            if dist is not None and (best_distance is None or dist < best_distance):
                best_distance = dist
                best_author_id = aid

        # Assign classification based on shortest graph distance
        if best_distance == 0:
            cls = "SELF"
        elif best_distance == 1:
            cls = "DIRECT_COAUTHOR"
        elif best_distance is not None and best_distance <= self.max_depth:
            cls = "TRANSITIVE_COAUTHOR"
        else:
            cls = "EXTERNAL"

        # Build metadata for the audit trail
        meta = {
            "closest_author_id": best_author_id,
            "closest_author_name": self.graph.names.get(best_author_id, ""),
            "graph_distance": best_distance,
        }

        # For direct co-authors, include the full collaboration record
        if best_distance == 1 and best_author_id:
            edge = self.graph.get_edge(self.target_id, best_author_id)
            if edge:
                meta["shared_papers"] = edge.shared_papers
                meta["coauthor_strength"] = round(edge.strength, 3)
                meta["last_collab_year"] = edge.last_collab_year

        return CitationClassification(
            citing_work_id=citing_work.openalex_id,
            cited_work_id=cited_work.openalex_id,
            classification=cls,
            confidence=1.0 if best_distance is not None else 0.9,
            phase_detected=2, metadata=meta,
        )


# ============================================================
# Trajectory Computation
# ============================================================

def compute_trajectory(classifications, target_works, citing_works, herocon_weights=None):
    """
    Compute cumulative BARON and HEROCON scores by year.

    Groups citations by the year they were received, then computes
    running cumulative scores. This shows how a researcher's metrics
    evolve over their career.

    Only includes citations from years within the researcher's actual
    publication timeline (earliest target work year onward) to avoid
    counting pre-career citations that might result from name collisions.

    Years with fewer than 3 cumulative citations show "—" instead of
    a score, since percentages are meaningless with so few data points.

    Args:
        classifications: List of CitationClassification objects.
        target_works: Dict of the researcher's own works.
        citing_works: Dict of works that cite the researcher.
        herocon_weights: Optional custom HEROCON weights.

    Returns:
        List of dicts with keys: year, total_citations, baron, herocon, [note].
    """
    # All classification labels that count as "in-group" for BARON
    IN_GROUP = {
        "SELF", "DIRECT_COAUTHOR", "TRANSITIVE_COAUTHOR",
        "SAME_DEPT", "SAME_INSTITUTION", "SAME_PARENT_ORG",
        "VENUE_SELF_GOVERNANCE", "VENUE_EDITOR_COAUTHOR",
        "VENUE_EDITOR_AFFIL", "VENUE_COMMITTEE",
    }

    # Determine the researcher's career start (earliest publication year)
    target_years = [
        w.publication_year for w in target_works.values()
        if w.publication_year
    ]
    if not target_years:
        return []
    earliest_pub_year = min(target_years)

    # Group citations by year (only from the researcher's active years onward)
    by_year = defaultdict(list)
    for cls in classifications:
        cw = citing_works.get(cls.citing_work_id)
        year = cw.publication_year if cw else None
        if year and year >= earliest_pub_year:
            by_year[year].append(cls)

    if not by_year:
        return []

    # Compute cumulative scores year by year
    years = sorted(by_year.keys())
    cumulative = []
    trajectory = []

    for year in years:
        cumulative.extend(by_year[year])
        total = len(cumulative)

        # Skip score computation for very small sample sizes
        if total < 3:
            trajectory.append({
                "year": year, "total_citations": total,
                "baron": None, "herocon": None, "note": "too few citations",
            })
            continue

        ext = sum(1 for c in cumulative if c.classification not in IN_GROUP)
        baron = ext / total * 100
        herocon = compute_herocon_score(cumulative, weights=herocon_weights)

        trajectory.append({
            "year": year, "total_citations": total,
            "baron": round(baron, 1), "herocon": round(herocon, 1),
        })

    return trajectory


# ============================================================
# Phase 2 Pipeline
# ============================================================

class Phase2Pipeline:
    """
    End-to-end Phase 2 pipeline: ingest → graph → classify → score → audit.

    Extends Phase 1 by constructing a co-author graph and using graph
    distance for classification. Shows progressive scores (Phase 1 baseline
    then Phase 2 refinement) to make the detection process transparent.
    """

    def __init__(self, console, verbose=False, max_depth=2,
                 skip_orcid=False, show_trajectory=False, since_year=None,
                 herocon_weights=None):
        self.console = console
        self.verbose = verbose
        self.max_depth = max_depth
        self.skip_orcid = skip_orcid
        self.show_trajectory = show_trajectory
        self.since_year = since_year
        self.herocon_weights = herocon_weights or HEROCON_WEIGHTS

        # Pipeline state
        self.researcher = None
        self.target_works = {}
        self.citing_works = {}
        self.citations = []
        self.classifications = []
        self.graph = CoAuthorGraph()
        self.orcid_result = None
        self.trajectory = []

    async def run(self, identifier):
        """
        Execute the full Phase 2 pipeline.

        Returns:
            Tuple of (ScoreResult, AuditLog).
        """
        start = time.time()
        self.audit = AuditLog(identifier, phase=2)

        async with OpenAlexClient() as client:

            # ── Step 1: Resolve author ──
            self.console.print("\n[bold cyan]Step 1/8:[/] Resolving author...")
            raw_author = await client.get_author(identifier)
            self.researcher = parse_author(raw_author)
            self.audit.log_researcher(self.researcher)
            self.console.print(
                f"  Found: [bold]{self.researcher.display_name}[/] "
                f"({self.researcher.works_count} works, "
                f"{self.researcher.cited_by_count} citations)"
            )

            # ── Step 2: Fetch all works ──
            self.console.print("\n[bold cyan]Step 2/8:[/] Fetching works...")
            with Progress(
                SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                BarColumn(), TextColumn("{task.completed}/{task.total}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Works", total=self.researcher.works_count)
                def works_cb(done, total):
                    progress.update(task, completed=done, total=total)
                raw_works = await client.get_works_by_author(
                    self.researcher.openalex_id, progress_callback=works_cb
                )

            # ── Step 3: ORCID cross-validation + --since filtering ──
            if not self.skip_orcid and self.researcher.orcid:
                self.console.print("\n[bold cyan]Step 3/8:[/] ORCID cross-validation...")
                validator = OrcidValidator(self.console)
                self.orcid_result = await validator.validate(
                    self.researcher.orcid, raw_works, since_year=self.since_year
                )
                raw_works = self.orcid_result.works_to_use
            elif self.since_year:
                self.console.print(f"\n[bold cyan]Step 3/8:[/] Filtering works since {self.since_year}...")
                before = len(raw_works)
                raw_works = [
                    w for w in raw_works
                    if not w.get("publication_year") or w["publication_year"] >= self.since_year
                ]
                self.console.print(f"  {before - len(raw_works)} work(s) before {self.since_year} excluded")
            elif not self.researcher.orcid:
                self.console.print("\n[bold cyan]Step 3/8:[/] ORCID skipped (no ORCID on profile)")
            else:
                self.console.print("\n[bold cyan]Step 3/8:[/] ORCID skipped (--no-orcid-check)")

            # Parse raw works into typed Work objects
            for rw in raw_works:
                wid = rw.get("id", "").replace("https://openalex.org/", "")
                self.target_works[wid] = parse_work(rw, is_target=True)

            # ── Step 4: Build co-author graph ──
            self.console.print("\n[bold cyan]Step 4/8:[/] Building co-author graph...")
            for wid, work in self.target_works.items():
                self.graph.add_paper(
                    work.author_ids, work.author_names,
                    work.publication_year, wid,
                )
            distances = self.graph.bfs(self.researcher.openalex_id, self.max_depth)
            direct = sum(1 for d in distances.values() if d == 1)
            transitive = sum(1 for d in distances.values() if d == 2)
            self.console.print(
                f"  Graph: {self.graph.node_count} authors, {self.graph.edge_count} edges\n"
                f"  Network: {direct} direct, {transitive} transitive co-authors"
            )

            # ── Step 5: Fetch incoming citations ──
            cited_works = {wid: w for wid, w in self.target_works.items() if w.cited_by_count > 0}
            total_expected = sum(w.cited_by_count for w in cited_works.values())
            self.console.print(
                f"\n[bold cyan]Step 5/8:[/] Fetching incoming citations "
                f"(~{total_expected} across {len(cited_works)} works)..."
            )
            with Progress(
                SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                BarColumn(), TextColumn("{task.completed}/{task.total} works"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Citations", total=len(cited_works))
                def cite_cb(done, total):
                    progress.update(task, completed=done, total=total)
                citing_map = await client.get_citing_works_batch(
                    list(cited_works.keys()), progress_callback=cite_cb
                )

            # Build citation links
            for cited_wid, raw_citers in citing_map.items():
                for rc in raw_citers:
                    cw = parse_work(rc, is_target=False)
                    self.citing_works[cw.openalex_id] = cw
                    self.citations.append(Citation(
                        citing_work_id=cw.openalex_id,
                        cited_work_id=cited_wid,
                        citation_year=cw.publication_year,
                    ))
            self.console.print(
                f"  {len(self.citing_works)} citing works, {len(self.citations)} citation links"
            )

            # ── Step 6: Progressive Classification ──
            # Show scores at each detection step so the user can see the impact
            self.console.print("\n[bold cyan]Step 6/8:[/] Classifying citations (progressive)...\n")

            # 6a: Self-citation pass (Phase 1 baseline)
            self_classifier = SelfCitationClassifier(self.researcher.openalex_id)
            self_only_cls = []
            for cit in self.citations:
                citing_w = self.citing_works.get(cit.citing_work_id)
                cited_w = self.target_works.get(cit.cited_work_id)
                if citing_w and cited_w:
                    self_only_cls.append(self_classifier.classify(citing_w, cited_w))

            # Display Step 1 score (self-citation baseline)
            total = len(self_only_cls)
            self_count = sum(1 for c in self_only_cls if c.classification == "SELF")
            non_self = total - self_count
            step1_baron = non_self / total * 100 if total > 0 else 0
            self.console.print(
                f"  [dim]Step 1 — Self-citation detection:[/]"
            )
            self.console.print(
                f"    BARON  [bold yellow]{step1_baron:.1f}%[/]"
                f"                      [dim]({self_count} self-citations removed)[/]\n"
            )

            # 6b: Co-author pass (Phase 2 — the main classification)
            coauthor_classifier = CoAuthorClassifier(
                self.researcher.openalex_id, self.graph, self.max_depth,
            )
            for cit in self.citations:
                citing_w = self.citing_works.get(cit.citing_work_id)
                cited_w = self.target_works.get(cit.cited_work_id)
                if citing_w and cited_w:
                    cls = coauthor_classifier.classify(citing_w, cited_w)
                    self.classifications.append(cls)

            # Display Step 2 score with delta from Step 1
            ext2 = sum(1 for c in self.classifications if c.classification == "EXTERNAL")
            coauth = sum(1 for c in self.classifications
                        if c.classification in ("DIRECT_COAUTHOR", "TRANSITIVE_COAUTHOR"))
            step2_baron = ext2 / total * 100 if total > 0 else 0
            step2_herocon = compute_herocon_score(self.classifications, weights=self.herocon_weights)
            delta = step1_baron - step2_baron
            self.console.print(
                f"  [dim]Step 2 — Co-author network:[/]"
            )
            self.console.print(
                f"    BARON  [bold yellow]{step2_baron:.1f}%[/]  [red]↓{delta:.1f}%[/]"
                f"    HEROCON  [bold green]{step2_herocon:.1f}%[/]"
                f"    [dim]({coauth} co-author citations detected)[/]"
            )

            # ── Step 7: Final score summary ──
            self.console.print(f"\n[bold cyan]Step 7/8:[/] Final score...\n")
            self.console.print(
                f"  ─── [bold]Final[/] ─────────────────────────────"
            )
            self.console.print(
                f"    BARON  [bold yellow]{step2_baron:.1f}%[/]"
                f"             HEROCON  [bold green]{step2_herocon:.1f}%[/]"
            )
            self.console.print(
                f"    Gap    [dim]{step2_herocon - step2_baron:.1f}%[/]\n"
            )

            # Optional: compute career trajectory
            if self.show_trajectory:
                self.trajectory = compute_trajectory(
                    self.classifications, self.target_works, self.citing_works,
                    herocon_weights=self.herocon_weights,
                )

            # ── Step 8: Compute full result and save audit ──
            self.console.print(f"[bold cyan]Step 8/8:[/] Finalizing...")
            score = self._compute_score(time.time() - start, client.api_calls, distances)

            self.audit.log_works(self.target_works, label="target")
            self.audit.log_works(self.citing_works, label="citing")
            self.audit.log_citations(self.citations)
            self.audit.log_classifications(
                self.classifications, self.target_works, self.citing_works
            )
            self.audit.log_coauthor_graph(self.graph, self.researcher.openalex_id, self.max_depth)
            self.audit.log_score(score)
            self.audit.log_ingestion(score.ingestion_stats)
            if self.orcid_result:
                self.audit.doc["orcid_validation"] = self.orcid_result.to_dict()
            if self.trajectory:
                self.audit.doc["trajectory"] = self.trajectory

            self.console.print("Done.\n")
            return score, self.audit

    def _compute_score(self, elapsed, api_calls, distances):
        """
        Compute the full BARON v0.2 and HEROCON v0.2 scores.

        Phase 2 breakdown includes four categories:
            SELF, DIRECT_COAUTHOR, TRANSITIVE_COAUTHOR, EXTERNAL
        """
        breakdown = ScoreBreakdown(total_citations=len(self.classifications))
        for cls in self.classifications:
            c = cls.classification
            if c == "SELF":
                breakdown.self_citations += 1
            elif c == "DIRECT_COAUTHOR":
                breakdown.direct_coauthor_citations += 1
            elif c == "TRANSITIVE_COAUTHOR":
                breakdown.transitive_coauthor_citations += 1
            else:
                breakdown.external_citations += 1

        baron = breakdown.pct(breakdown.external_citations)
        herocon = compute_herocon_score(self.classifications, weights=self.herocon_weights)

        # Top self-cited works
        sc_counts = defaultdict(int)
        for cls in self.classifications:
            if cls.classification == "SELF":
                sc_counts[cls.cited_work_id] += 1
        top_self = sorted(sc_counts.items(), key=lambda x: -x[1])[:5]
        top_self_works = [
            {"title": self.target_works[wid].title,
             "year": self.target_works[wid].publication_year,
             "self_citations": count,
             "total_citations": self.target_works[wid].cited_by_count}
            for wid, count in top_self if wid in self.target_works
        ]

        # Co-author network statistics for the audit trail
        top_coauthors = self.graph.top_coauthors(self.researcher.openalex_id, 10)
        coauthor_stats = {
            "graph_nodes": self.graph.node_count,
            "graph_edges": self.graph.edge_count,
            "direct_coauthors": sum(1 for d in distances.values() if d == 1),
            "transitive_coauthors": sum(1 for d in distances.values() if d == 2),
            "top_coauthors": [
                {"name": name, "openalex_id": aid,
                 "shared_papers": edge.shared_papers,
                 "strength": round(edge.strength, 2),
                 "last_collab": edge.last_collab_year}
                for aid, name, edge in top_coauthors
            ],
        }

        # Reference coverage metric
        works_with_refs = sum(1 for w in self.target_works.values() if w.referenced_work_ids)
        ref_coverage = works_with_refs / len(self.target_works) * 100 if self.target_works else 0

        return ScoreResult(
            researcher=self.researcher, phase="v0.2",
            baron_score=baron, herocon_score=herocon,
            breakdown=breakdown,
            top_self_cited_works=top_self_works,
            coauthor_stats=coauthor_stats,
            herocon_weights_used=self.herocon_weights,
            ingestion_stats={
                "works_fetched": len(self.target_works),
                "citing_works_fetched": len(self.citing_works),
                "citation_links": len(self.citations),
                "reference_coverage": f"{ref_coverage:.1f}%",
                "api_calls": api_calls,
                "time_elapsed": f"{elapsed:.1f}s",
            },
        )


# ============================================================
# Display
# ============================================================

def display_score(console, score, trajectory=None):
    """
    Render the Phase 2 score to the terminal using Rich formatting.

    Shows: researcher info, BARON & HEROCON scores, full breakdown with
    HEROCON weights, optional career trajectory, and the disclaimer.
    """
    b = score.breakdown

    # ── Header panel ──
    console.print(Panel(
        f"[bold]{score.researcher.display_name}[/]\n"
        f"ORCID: {score.researcher.orcid or 'N/A'}  |  "
        f"OpenAlex: {score.researcher.openalex_id}  |  "
        f"Works: {score.researcher.works_count}",
        title="[bold cyan]BARON & HEROCON v0.2 — Co-Author Network[/]",
        border_style="cyan",
    ))

    # ── Score breakdown with HEROCON weights shown ──
    sc = Table(show_header=False, box=None, padding=(0, 2))
    sc.add_column(style="dim", width=32)
    sc.add_column(justify="right")
    sc.add_row("[bold]BARON v0.2[/]", f"[bold yellow]{score.baron_score:.1f}%[/]")
    sc.add_row("[bold]HEROCON v0.2[/]", f"[bold green]{score.herocon_score:.1f}%[/]")
    sc.add_row("  [dim]Gap (HEROCON − BARON)[/]", f"[dim]{score.herocon_score - score.baron_score:.1f}%[/]")
    sc.add_row("", "")
    sc.add_row("  [green]External[/] citations",
               f"[green]{b.external_citations}[/] ({b.pct(b.external_citations):.1f}%)")
    sc.add_row("", "")
    sc.add_row("  [dim]In-group breakdown:[/]", "")
    sc.add_row("    Self-citations",
               f"[red]{b.self_citations}[/] ({b.pct(b.self_citations):.1f}%) → 0.0")
    sc.add_row("    Direct co-author",
               f"[magenta]{b.direct_coauthor_citations}[/] ({b.pct(b.direct_coauthor_citations):.1f}%) → 0.2")
    sc.add_row("    Transitive co-author",
               f"[blue]{b.transitive_coauthor_citations}[/] ({b.pct(b.transitive_coauthor_citations):.1f}%) → 0.5")
    sc.add_row("", "")
    sc.add_row("  Total citations", f"{b.total_citations}")
    console.print(Panel(sc, title="[bold yellow]Score[/]", border_style="yellow"))

    # ── Career trajectory (optional) ──
    if trajectory:
        tt = Table(box=None, padding=(0, 2))
        tt.add_column("Year", style="dim", justify="center")
        tt.add_column("Citations", justify="right")
        tt.add_column("BARON", justify="right")
        tt.add_column("HEROCON", justify="right")
        for row in trajectory:
            baron_str = f"[yellow]{row['baron']}%[/]" if row.get("baron") is not None else "[dim]—[/]"
            herocon_str = f"[green]{row['herocon']}%[/]" if row.get("herocon") is not None else "[dim]—[/]"
            tt.add_row(str(row["year"]), str(row["total_citations"]), baron_str, herocon_str)
        console.print(Panel(tt, title="[bold]Career Trajectory[/] (cumulative)", border_style="blue"))

    # ── Disclaimer ──
    console.print(f"\n[dim italic]{DISCLAIMER}[/]\n")


# ============================================================
# CLI
# ============================================================

app = typer.Typer(name="baron-herocon-p2", help="BARON & HEROCON Phase 2: Co-Author Network Detection")


@app.command()
def score(
    orcid: Optional[str] = typer.Option(None, "--orcid"),
    openalex_id: Optional[str] = typer.Option(None, "--openalex-id"),
    depth: int = typer.Option(2, "--depth", "-d", help="Co-author graph depth (1, 2, or 3)"),
    since: Optional[int] = typer.Option(None, "--since", help="Only include works from this year onward"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    trajectory: bool = typer.Option(False, "--trajectory", "-t", help="Show cumulative career trajectory"),
    export: Optional[str] = typer.Option(None, "--export"),
    no_audit: bool = typer.Option(False, "--no-audit"),
    no_orcid_check: bool = typer.Option(False, "--no-orcid-check"),
    herocon_weights_file: Optional[str] = typer.Option(None, "--herocon-weights", help="Path to custom HEROCON weights JSON file"),
):
    """Compute BARON & HEROCON v0.2 with co-author network detection."""
    console = Console()
    if not orcid and not openalex_id:
        console.print("[bold red]Error:[/] Provide --orcid or --openalex-id")
        raise typer.Exit(1)

    identifier = orcid or openalex_id
    console.print(f"\n[bold]BARON & HEROCON v0.2[/] — Co-Author Network (depth={depth})")
    console.print(f"Target: [cyan]{identifier}[/]")

    # Load custom HEROCON weights if a weights file was provided
    herocon_weights = None
    if herocon_weights_file:
        with open(herocon_weights_file, "r") as f:
            herocon_weights = json.load(f)

    # Run the pipeline
    pipeline = Phase2Pipeline(
        console, verbose=verbose, max_depth=depth,
        skip_orcid=no_orcid_check, show_trajectory=trajectory,
        since_year=since, herocon_weights=herocon_weights,
    )
    result, audit = asyncio.run(pipeline.run(identifier))

    # Display results
    display_score(console, result, trajectory=pipeline.trajectory if trajectory else None)

    # Save audit trail (on by default)
    if not no_audit:
        audit_file = audit.save()
        console.print(f"[dim]Audit trail saved to:[/] [bold green]{audit_file}[/]")
        console.print(f"[dim]  → {len(audit.doc['classifications'])} citations classified[/]\n")

    # Optional JSON export
    if export:
        export_data = {
            "version": "v0.2", "phase": 2,
            "created_at": datetime.now().isoformat(),
            "config": {"coauthor_depth": depth},
            "researcher": asdict(result.researcher),
            "score": {
                "baron_v02": round(result.baron_score, 1),
                "herocon_v02": round(result.herocon_score, 1),
                "herocon_weights": result.herocon_weights_used,
                "breakdown": result.breakdown.to_dict(),
            },
            "coauthor_stats": result.coauthor_stats,
            "top_self_cited_works": result.top_self_cited_works,
            "ingestion_stats": result.ingestion_stats,
        }
        if pipeline.trajectory:
            export_data["trajectory"] = pipeline.trajectory
        with open(export, "w") as f:
            json.dump(export_data, f, indent=2)
        console.print(f"[green]Summary exported to {export}[/]\n")


if __name__ == "__main__":
    app()
