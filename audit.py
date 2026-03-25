"""
citation-constellation/audit.py
================================
Transparent audit logging for BARON & HEROCON.

Every run produces a comprehensive JSON audit file that documents:
  - Every citation and its classification rationale
  - Every co-author relationship and its strength
  - Every decision the system made and why

This is non-optional by design. Transparency is a core principle:
any researcher should be able to open the audit file and verify
exactly how their score was computed, down to individual citations.

Output directory: ./audits/ (created automatically)

Filename format (example):
    Mahbub_Ul_Alam_Citation_Constellation_Scores_BARON_84.9_HEROCON_85.9
    _Orcid_0000000211013793_timestamp_20260315_215252_audit_report.json
"""

import json
import os
from datetime import datetime

from models import (
    Researcher, Work, Citation, CitationClassification,
    ScoreResult, DISCLAIMER,
)


# ============================================================
# Audit File Naming
# ============================================================

AUDIT_DIR = "audits"


def audit_filename(identifier: str, phase: int, researcher_name: str = "",
                   baron_score: float = None, herocon_score: float = None) -> str:
    """
    Generate a descriptive audit filename embedding key metadata.

    The filename encodes the researcher's name, both scores, the identifier
    type (ORCID or OpenAlex), and a timestamp. This makes audit files
    self-describing — you can tell what's inside without opening the file.

    Examples:
        ORCID identifier:
            Mahbub_Ul_Alam_Citation_Constellation_Scores_BARON_84.9_HEROCON_85.9
            _Orcid_0000000211013793_timestamp_20260315_215252_audit_report.json

        OpenAlex identifier (no ORCID):
            Mahbub_Ul_Alam_Citation_Constellation_Scores_BARON_84.9_HEROCON_85.9
            _OpenAlex_A5100390903_timestamp_20260315_215252_audit_report.json

    Args:
        identifier: ORCID or OpenAlex ID used for the run.
        phase: Pipeline phase number (1, 2, or 3).
        researcher_name: Display name (academic titles are stripped).
        baron_score: Final BARON score (None if not yet computed).
        herocon_score: Final HEROCON score (None if Phase 1).

    Returns:
        Filename string (without directory path).
    """
    import re
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Name part: strip academic titles and sanitise for filesystem ──
    if researcher_name:
        for prefix in ["Professor ", "Prof. ", "Prof ", "Doctor ", "Dr. ", "Dr ",
                        "Associate Professor ", "Assoc. Prof. ",
                        "Assistant Professor ", "Asst. Prof. "]:
            if researcher_name.startswith(prefix):
                researcher_name = researcher_name[len(prefix):]
                break
        name_part = re.sub(r"[^\w\s-]", "", researcher_name.strip())
        name_part = re.sub(r"[\s]+", "-", name_part).strip("-")
    else:
        name_part = "Unknown_Researcher"

    # ── Score parts: format as "84.9" or "pending"/"NA" if not available ──
    baron_str = f"{baron_score:.1f}" if baron_score is not None else "pending"
    herocon_str = f"{herocon_score:.1f}" if herocon_score is not None else "NA"

    # ── Identifier part: detect ORCID vs OpenAlex format ──
    clean_id = identifier.replace("https://openalex.org/", "").replace("https://orcid.org/", "")
    if "-" in clean_id and len(clean_id.replace("-", "")) == 16:
        # ORCID format: 16 digits with hyphens (e.g. 0000-0002-1101-3793)
        id_part = f"ORCID-ID_{clean_id}"
    elif clean_id.startswith("A"):
        # OpenAlex author ID format (e.g. A5100390903)
        id_part = f"OpenAlex-ID_{clean_id}"
    else:
        # Unknown format: strip non-alphanumeric characters
        id_part = f"ID_{re.sub(r'[^a-zA-Z0-9]', '', clean_id)}"

    return (
        f"{name_part}_Citation-Constellation-Audit-Report"
        f"_BARON-Score_{baron_str}"
        f"_HEROCON-Score_{herocon_str}"
        f"_{id_part}"
        f"_Generated-Time_{ts}"
        f".json"
    )


def audit_path(identifier: str, phase: int, researcher_name: str = "",
               baron_score: float = None, herocon_score: float = None) -> str:
    """
    Generate the full filesystem path for an audit file.

    Creates the audits/ directory if it doesn't exist.

    Returns:
        Full path string (e.g. "audits/Mahbub_Ul_Alam_..._audit_report.json").
    """
    os.makedirs(AUDIT_DIR, exist_ok=True)
    return os.path.join(AUDIT_DIR, audit_filename(
        identifier, phase, researcher_name, baron_score, herocon_score
    ))


# ============================================================
# Audit Document Builder
# ============================================================

class AuditLog:
    """
    Builds a complete audit document for a single BARON/HEROCON run.

    The audit document is a structured JSON object that captures everything
    the system saw, did, and decided — in one file. It serves as the single
    source of truth for reproducibility and transparency.

    Usage:
        audit = AuditLog("0000-0002-1101-3793", phase=3)
        audit.log_researcher(researcher)
        audit.log_works(target_works, label="target")
        audit.log_citations(citations)
        audit.log_classifications(classifications, target_works, citing_works)
        audit.log_score(score)
        path = audit.save()

    The document structure:
        _meta:            Run metadata (tool version, timestamps, disclaimer)
        researcher:       Target researcher profile
        score:            Final BARON/HEROCON scores with full breakdown
        ingestion:        Data fetching statistics
        works:            Every work analysed (target and citing)
        citations:        Every citation link
        classifications:  Every classification with rationale and evidence
        coauthor_graph:   Full co-author network (Phase 2+)
        affiliation_data: Temporal affiliation timeline (Phase 3)
        orcid_validation: ORCID cross-validation results (when available)
        trajectory:       Career trajectory data (when --trajectory is used)
    """

    def __init__(self, identifier: str, phase: int):
        self.identifier = identifier
        self.phase = phase
        self.started_at = datetime.now().isoformat()

        # Initialise the audit document skeleton
        self.doc = {
            "_meta": {
                "tool": "citation-constellation",
                "version": f"v0.{phase}",
                "phase": phase,
                "identifier": identifier,
                "created_at": self.started_at,
                "started_at": self.started_at,
                "completed_at": None,  # Set on save()
                "description": (
                    "Complete audit trail for citation network structure analysis. "
                    "Every citation, classification, and decision is logged here. "
                    "This file exists for full transparency — any researcher can "
                    "verify exactly how their score was computed."
                ),
                "disclaimer": DISCLAIMER,
            },
            "researcher": None,
            "score": None,
            "ingestion": None,
            "works": [],
            "citations": [],
            "classifications": [],
        }

    # ── Researcher ──

    def log_researcher(self, researcher: Researcher):
        """Log the target researcher's profile information."""
        self.doc["researcher"] = {
            "openalex_id": researcher.openalex_id,
            "orcid": researcher.orcid,
            "display_name": researcher.display_name,
            "works_count": researcher.works_count,
            "cited_by_count": researcher.cited_by_count,
            "openalex_url": f"https://openalex.org/{researcher.openalex_id}",
        }

    # ── Works ──

    def log_works(self, works: dict[str, Work], label: str = "target"):
        """
        Log all works with full metadata.

        Args:
            works: Dict mapping work ID to Work objects.
            label: Role label — "target" for the researcher's own works,
                   "citing" for works that cite the target.
        """
        for wid, w in works.items():
            self.doc["works"].append({
                "openalex_id": w.openalex_id,
                "doi": w.doi,
                "title": w.title,
                "year": w.publication_year,
                "venue": w.venue_name,
                "type": w.work_type,
                "cited_by_count": w.cited_by_count,
                "author_count": len(w.author_ids),
                "authors": [
                    {"id": aid, "name": aname}
                    for aid, aname in zip(w.author_ids, w.author_names)
                ],
                "reference_count": len(w.referenced_work_ids),
                "role": label,
                "openalex_url": f"https://openalex.org/{w.openalex_id}",
            })

    # ── Citations ──

    def log_citations(self, citations: list[Citation]):
        """Log every citation link (citing_work → cited_work)."""
        for cit in citations:
            self.doc["citations"].append({
                "citing_work_id": cit.citing_work_id,
                "cited_work_id": cit.cited_work_id,
                "citation_year": cit.citation_year,
            })

    # ── Classifications ──

    def log_classifications(
        self,
        classifications: list[CitationClassification],
        target_works: dict[str, Work],
        citing_works: dict[str, Work],
    ):
        """
        Log every classification with full context for auditability.

        Each classification entry includes:
          - The citing work (title, year, authors)
          - The cited work (title, year)
          - The classification label and confidence
          - A human-readable rationale explaining the decision
          - Raw metadata used to make the classification

        This is the heart of the audit trail — it lets any reviewer
        trace exactly why a specific citation was classified the way
        it was.
        """
        for cls in classifications:
            citing_w = citing_works.get(cls.citing_work_id)
            cited_w = target_works.get(cls.cited_work_id)

            entry = {
                "citing_work": {
                    "id": cls.citing_work_id,
                    "title": citing_w.title if citing_w else "Unknown",
                    "year": citing_w.publication_year if citing_w else None,
                    "authors": (
                        [
                            {"id": aid, "name": aname}
                            for aid, aname in zip(
                                citing_w.author_ids, citing_w.author_names
                            )
                        ]
                        if citing_w else []
                    ),
                },
                "cited_work": {
                    "id": cls.cited_work_id,
                    "title": cited_w.title if cited_w else "Unknown",
                    "year": cited_w.publication_year if cited_w else None,
                },
                "classification": cls.classification,
                "confidence": cls.confidence,
                "phase_detected": cls.phase_detected,
                "rationale": _rationale(cls),
                "metadata": cls.metadata,
            }
            self.doc["classifications"].append(entry)

    # ── Co-Author Graph (Phase 2+) ──

    def log_coauthor_graph(self, graph, target_id: str, max_depth: int):
        """
        Log the full co-author graph with distances and edge details.

        Captures:
          - Every node (author) with their distance from the target
          - Every edge with collaboration strength and history
          - Summary statistics (total nodes, edges, direct/transitive counts)

        For direct co-authors (distance 1), the full co-authorship record
        is included: shared papers, strength score, collaboration timeline,
        and the specific work IDs that connect them.
        """
        # BFS from target to compute distances for all reachable nodes
        distances = graph.bfs(target_id, max_depth)

        # ── Build node list with distance and role labels ──
        nodes = []
        for author_id, distance in sorted(distances.items(), key=lambda x: x[1]):
            node = {
                "author_id": author_id,
                "name": graph.names.get(author_id, "Unknown"),
                "distance_from_target": distance,
                "role": _distance_label(distance),
            }
            # Include full co-authorship details for direct co-authors
            if distance == 1:
                edge = graph.get_edge(target_id, author_id)
                if edge:
                    node["coauthorship"] = {
                        "shared_papers": edge.shared_papers,
                        "strength": round(edge.strength, 3),
                        "first_collab_year": edge.first_collab_year,
                        "last_collab_year": edge.last_collab_year,
                        "shared_work_ids": edge.shared_work_ids,
                    }
            nodes.append(node)

        # ── Build deduplicated edge list ──
        edges = []
        seen = set()
        for src, neighbors in graph.adj.items():
            for dst, edge in neighbors.items():
                # Avoid duplicates: edges are undirected, stored in both directions
                pair = tuple(sorted([src, dst]))
                if pair not in seen:
                    seen.add(pair)
                    edges.append({
                        "author_a": {
                            "id": edge.author_a_id,
                            "name": graph.names.get(edge.author_a_id, "Unknown"),
                        },
                        "author_b": {
                            "id": edge.author_b_id,
                            "name": graph.names.get(edge.author_b_id, "Unknown"),
                        },
                        "shared_papers": edge.shared_papers,
                        "strength": round(edge.strength, 3),
                        "first_collab_year": edge.first_collab_year,
                        "last_collab_year": edge.last_collab_year,
                    })

        self.doc["coauthor_graph"] = {
            "config": {
                "target_author_id": target_id,
                "max_depth": max_depth,
            },
            "summary": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "direct_coauthors": sum(1 for n in nodes if n["distance_from_target"] == 1),
                "transitive_coauthors": sum(1 for n in nodes if n["distance_from_target"] == 2),
            },
            "nodes": nodes,
            "edges": edges,
        }

    # ── Score ──

    def log_score(self, score: ScoreResult):
        """
        Log the final computed score with full breakdown.

        Includes HEROCON explanation when applicable: describes the
        difference between BARON (binary) and HEROCON (graduated)
        scoring, and what the gap between them signifies.
        """
        self.doc["score"] = {
            "phase": score.phase,
            "baron_score": round(score.baron_score, 2),
            "herocon_score": round(score.herocon_score, 2) if score.herocon_score is not None else None,
            "herocon_weights": score.herocon_weights_used,
            "breakdown": score.breakdown.to_dict(),
            "top_self_cited_works": score.top_self_cited_works,
        }

        # Add HEROCON explanation when both scores are present (Phase 2+)
        if score.herocon_score is not None:
            self.doc["score"]["herocon_explanation"] = (
                "HEROCON gives partial credit to in-group citations using graduated weights. "
                "BARON uses binary 0/1 (in-group=0, external=1). "
                "HEROCON is always >= BARON. The gap shows how much impact depends on the inner circle."
            )

        # Include co-author network statistics if available
        if score.coauthor_stats:
            self.doc["score"]["coauthor_stats"] = score.coauthor_stats

    # ── Ingestion Stats ──

    def log_ingestion(self, stats: dict):
        """Log data fetching statistics (API calls, timing, coverage)."""
        self.doc["ingestion"] = stats

    # ── Classification Summary ──

    def _add_summary(self):
        """
        Add a human-readable summary to the audit _meta section.

        Computes aggregate counts and percentages across all classifications,
        giving a quick overview without having to scan every individual entry.
        This summary is always added just before saving.
        """
        cls_counts = {}
        for c in self.doc["classifications"]:
            label = c["classification"]
            cls_counts[label] = cls_counts.get(label, 0) + 1

        total = len(self.doc["classifications"])
        self.doc["_meta"]["summary"] = {
            "total_works_analyzed": len(
                [w for w in self.doc["works"] if w["role"] == "target"]
            ),
            "total_citing_works": len(
                [w for w in self.doc["works"] if w["role"] == "citing"]
            ),
            "total_citations_classified": total,
            "classification_counts": cls_counts,
            "classification_percentages": {
                k: round(v / total * 100, 1) if total > 0 else 0
                for k, v in cls_counts.items()
            },
        }

    # ── Save ──

    def save(self) -> str:
        """
        Save the audit document to a JSON file in the audits/ directory.

        The filename is auto-generated from the researcher name, scores,
        identifier, and current timestamp. Timestamps prevent overwrites
        between runs.

        Returns:
            The full filesystem path to the saved audit file.
        """
        self.doc["_meta"]["completed_at"] = datetime.now().isoformat()
        self._add_summary()

        # Extract naming info from logged data
        researcher_name = ""
        baron_score = None
        herocon_score = None
        if self.doc.get("researcher"):
            researcher_name = self.doc["researcher"].get("display_name", "")
        if self.doc.get("score"):
            baron_score = self.doc["score"].get("baron_score")
            herocon_score = self.doc["score"].get("herocon_score")

        path = audit_path(
            self.identifier, self.phase,
            researcher_name=researcher_name,
            baron_score=baron_score,
            herocon_score=herocon_score,
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.doc, f, indent=2, ensure_ascii=False)
        return path

    def save_to(self, path: str) -> str:
        """
        Save the audit document to a specific filesystem path.

        Creates parent directories if they don't exist. Useful for
        testing or when the caller wants control over the output location.

        Args:
            path: Full filesystem path for the output file.

        Returns:
            The path that was written to.
        """
        self.doc["_meta"]["completed_at"] = datetime.now().isoformat()
        self._add_summary()

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.doc, f, indent=2, ensure_ascii=False)
        return path


# ============================================================
# Helpers
# ============================================================

def _rationale(cls: CitationClassification) -> str:
    """
    Generate a human-readable rationale for a citation classification.

    Each classification type has a specific rationale template that
    explains, in plain English, why the citation was classified that way.
    These rationales appear in the audit file next to each classification,
    making the audit trail readable without needing to interpret raw metadata.

    Args:
        cls: The CitationClassification to explain.

    Returns:
        A one-sentence explanation of the classification decision.
    """
    meta = cls.metadata or {}

    if cls.classification == "SELF":
        ids = meta.get("matching_author_ids", [])
        return (
            f"Target researcher is an author on the citing work "
            f"(matched ID: {ids[0] if ids else 'unknown'})"
        )

    elif cls.classification == "DIRECT_COAUTHOR":
        name = meta.get("closest_author_name") or "unknown"
        aid = meta.get("closest_author_id", "")
        return (
            f"Citing author '{name}' ({aid}) is a direct co-author of target "
            f"(graph distance 1)"
        )

    elif cls.classification == "TRANSITIVE_COAUTHOR":
        name = meta.get("closest_author_name") or "unknown"
        aid = meta.get("closest_author_id", "")
        dist = meta.get("graph_distance", 2)
        return (
            f"Citing author '{name}' ({aid}) is a transitive co-author "
            f"(graph distance {dist})"
        )

    elif cls.classification == "SAME_DEPT":
        inst = meta.get("citing_institution", "unknown institution")
        return (
            f"Citing author at same department within '{inst}' "
            f"(no co-authorship, affiliation match at time of citation)"
        )

    elif cls.classification == "SAME_INSTITUTION":
        c_inst = meta.get("citing_institution", "unknown")
        t_inst = meta.get("target_institution", "unknown")
        ror = meta.get("citing_institution_ror", "")
        if ror:
            return (
                f"Citing author at same institution '{c_inst}' (ROR: {ror}), "
                f"different department from target"
            )
        return (
            f"Citing author at same institution '{c_inst}' "
            f"(raw string match, no co-authorship)"
        )

    elif cls.classification == "SAME_PARENT_ORG":
        c_inst = meta.get("citing_institution", "unknown")
        t_inst = meta.get("target_institution", "unknown")
        return (
            f"Citing author at '{c_inst}' shares parent organization "
            f"with target at '{t_inst}'"
        )

    elif cls.classification == "UNKNOWN":
        reason = meta.get("reason", "Insufficient metadata for classification")
        return f"UNKNOWN — {reason}. Not counted in BARON/HEROCON percentages."

    elif cls.classification == "EXTERNAL":
        has_data = meta.get("affiliation_data_available", True)
        if not has_data:
            return (
                "No affiliation data available for target researcher at this time "
                "— defaulted to EXTERNAL"
            )
        return "No co-authorship or institutional connection found within configured parameters"

    elif cls.classification == "NON_SELF":
        return "Not a self-citation (Phase 1 — co-author network not yet analyzed)"

    # Fallback for any future classification types
    return f"Classification: {cls.classification}"


def _distance_label(distance: int) -> str:
    """
    Convert a graph distance integer to a human-readable role label.

    Used in the co-author graph audit section to label each node
    with its relationship to the target researcher.
    """
    if distance == 0:
        return "target_researcher"
    elif distance == 1:
        return "direct_coauthor"
    elif distance == 2:
        return "transitive_coauthor"
    else:
        return f"depth_{distance}"
