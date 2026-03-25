"""
citation-constellation/phase3.py
=================================
Phase 3: Affiliation Matching

The most comprehensive detection phase. Builds on Phase 2's co-author
network and adds institutional affiliation matching, detecting citations
from the same department, institution, or parent organisation — even
when there is no co-authorship relationship.

Detection hierarchy (applied in order of priority):
    1. SELF               — target is an author on the citing work
    2. DIRECT_COAUTHOR    — citing author shared ≥1 paper with target
    3. TRANSITIVE_COAUTHOR — citing author is a co-author's co-author
    4. SAME_DEPT          — same department, no co-authorship
    5. SAME_INSTITUTION   — same university, different department
    6. SAME_PARENT_ORG    — different institution, shared parent org
    7. UNKNOWN            — insufficient metadata for classification
    8. EXTERNAL           — no detected relationship

The key innovation in Phase 3 is temporal affiliation matching: a citation
from 2022 is matched against where both researchers were affiliated *in 2022*,
not where they are today. This uses work-level affiliations from OpenAlex,
which record each author's institution at the time of each publication.

Institution hierarchy is resolved using ROR (Research Organization Registry),
which provides parent-child relationships between institutions. Two researchers
at different universities under the same consortium → SAME_PARENT_ORG.

Usage:
    python phase3.py --orcid 0000-0000-0000-0000
    python phase3.py --orcid 0000-0000-0000-0000 --depth 3 --export results.json
    python phase3.py --openalex-id A0000000000 -v
    python phase3.py --orcid 0000-0000-0000-0000 --confirm

Requirements:
    pip install -r requirements.txt
"""

import asyncio
import json
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
    CoAuthorEdge, AffiliationRecord, InstitutionInfo,
    ScoreBreakdown, ScoreResult,
    HEROCON_WEIGHTS, compute_herocon_score, load_herocon_weights, DISCLAIMER,
    parse_author, parse_work, parse_work_authors,
    format_elapsed,
)
from client import OpenAlexClient, RORClient
from orcid_validate import OrcidValidator
from phase2 import CoAuthorGraph, SelfCitationClassifier, compute_trajectory


# ============================================================
# Affiliation Timeline
# ============================================================

class AffiliationTimeline:
    """
    Tracks where each author was affiliated at different points in time.

    Built from work-level affiliations in OpenAlex: each work records the
    author's institution at time of publication. Collecting these across
    all works (both target and citing) gives a temporal trace without
    needing ORCID employment history (which is often incomplete).

    Example timeline for one author:
        2018 → Enchanted Forest University  (from paper W001)
        2019 → Enchanted Forest University  (from paper W002)
        2021 → Dragon Peak Research Centre  (from paper W003)
        2023 → Dragon Peak Research Centre  (from paper W004)

    The key method is get_affiliation_at_year(), which looks up where
    an author was at a specific point in time. When no exact year match
    exists, it uses the closest earlier year (or the closest later year
    as a last resort).
    """

    def __init__(self):
        # author_id → list of AffiliationRecord objects
        self.records: dict[str, list[AffiliationRecord]] = defaultdict(list)

    def add_from_work(self, work_id: str, year: Optional[int], authorships: list[dict]):
        """
        Extract affiliation records from a work's authorship data.

        Each author on the paper may have one or more institutional
        affiliations recorded. Each institution → one AffiliationRecord.

        Args:
            work_id: Bare OpenAlex work ID.
            year: Publication year of the work.
            authorships: Raw 'authorships' array from OpenAlex JSON.
        """
        for a in authorships:
            aid = (a.get("author", {}).get("id") or "").replace("https://openalex.org/", "")
            if not aid:
                continue
            for inst in a.get("institutions", []):
                ror = (inst.get("ror") or "").replace("https://ror.org/", "") or None
                oaid = (inst.get("id") or "").replace("https://openalex.org/", "") or None
                self.records[aid].append(AffiliationRecord(
                    author_openalex_id=aid,
                    institution_name=inst.get("display_name", ""),
                    institution_ror=ror,
                    institution_openalex_id=oaid,
                    year=year,
                    source_work_id=work_id,
                    department=inst.get("department"),
                ))

    def get_affiliation_at_year(self, author_id: str, year: Optional[int]) -> list[AffiliationRecord]:
        """
        Look up an author's affiliation(s) at a specific year.

        Matching strategy (in priority order):
            1. Exact year match → return all affiliations from that year
            2. Closest earlier year → most recent affiliation before the target year
            3. Closest later year → earliest affiliation after the target year
            4. No year data → return the latest available records

        Returns deduplicated records (one per unique institution).

        Args:
            author_id: Bare OpenAlex author ID.
            year: The year to look up (typically the citation year).

        Returns:
            List of AffiliationRecord objects (may be empty).
        """
        recs = self.records.get(author_id, [])
        if not recs:
            return []

        # If no specific year requested, return the latest available
        if year is None:
            return self._latest(recs)

        # Strategy 1: Exact year match
        exact = [r for r in recs if r.year == year]
        if exact:
            return self._dedupe(exact)

        # Strategy 2: Closest earlier year (most common fallback)
        earlier = [r for r in recs if r.year is not None and r.year <= year]
        if earlier:
            max_year = max(r.year for r in earlier)
            return self._dedupe([r for r in earlier if r.year == max_year])

        # Strategy 3: Closest later year (last resort)
        later = [r for r in recs if r.year is not None and r.year > year]
        if later:
            min_year = min(r.year for r in later)
            return self._dedupe([r for r in later if r.year == min_year])

        return []

    def get_all_institutions(self, author_id: str) -> set[str]:
        """Get all unique ROR IDs ever associated with an author."""
        return {r.institution_ror for r in self.records.get(author_id, []) if r.institution_ror}

    def _latest(self, recs):
        """Get the most recent affiliation records."""
        with_year = [r for r in recs if r.year is not None]
        if with_year:
            max_year = max(r.year for r in with_year)
            return self._dedupe([r for r in with_year if r.year == max_year])
        return self._dedupe(recs)

    def _dedupe(self, recs):
        """Deduplicate records by institution (using ROR ID or name as key)."""
        seen = set()
        result = []
        for r in recs:
            key = r.institution_ror or r.institution_name
            if key not in seen:
                seen.add(key)
                result.append(r)
        return result

    @property
    def author_count(self):
        """Number of unique authors tracked in the timeline."""
        return len(self.records)

    @property
    def record_count(self):
        """Total number of affiliation records across all authors."""
        return sum(len(v) for v in self.records.values())


# ============================================================
# Institution Hierarchy
# ============================================================

class InstitutionHierarchy:
    """
    Resolves institutional relationships using ROR hierarchy data.

    Determines how two institutions are related:
        SAME_DEPT        → same institution AND same department
        SAME_INSTITUTION → same ROR ID, different departments (or unknown departments)
        SAME_PARENT_ORG  → different institutions sharing a parent in ROR hierarchy
        DIFFERENT        → no institutional relationship detected

    Data sources:
        - OpenAlex institution profiles (ROR ID, display name, lineage)
        - ROR API v2 (parent/child relationships between organisations)

    For institutions without ROR IDs, falls back to fuzzy string matching
    on institution names (with lower confidence).
    """

    def __init__(self):
        self.institutions: dict[str, InstitutionInfo] = {}  # ror_id → InstitutionInfo
        self.parent_map: dict[str, str] = {}                 # child_ror → parent_ror
        self.oaid_to_ror: dict[str, str] = {}                # OpenAlex inst ID → ROR ID

    def add_from_openalex(self, raw: dict):
        """
        Register an institution from an OpenAlex institution profile.

        Extracts the ROR ID, display name, and other metadata.
        Builds the oaid_to_ror mapping for cross-referencing.

        Args:
            raw: Raw OpenAlex institution JSON dict.
        """
        oaid = (raw.get("id") or "").replace("https://openalex.org/", "")
        ror = (raw.get("ror") or "").replace("https://ror.org/", "") or None
        if not ror:
            return  # Can't do hierarchy matching without a ROR ID

        lineage = raw.get("lineage", [])
        info = InstitutionInfo(
            ror_id=ror, openalex_id=oaid,
            display_name=raw.get("display_name", ""),
            country=raw.get("country_code", ""),
            type=raw.get("type", ""),
        )
        self.institutions[ror] = info
        if oaid:
            self.oaid_to_ror[oaid] = ror

    def add_from_ror(self, ror_id: str, raw: dict):
        """
        Register an institution from a ROR API response.

        Extracts parent/child relationships from the 'relationships' array.
        These relationships are the backbone of SAME_PARENT_ORG detection.

        Args:
            ror_id: The ROR identifier being registered.
            raw: Raw ROR API JSON response.
        """
        if not raw:
            return
        clean_id = ror_id.replace("https://ror.org/", "")

        # Extract parent and child relationships
        parent_ror = None
        children = []
        for rel in raw.get("relationships", []):
            rel_ror = (rel.get("id") or "").replace("https://ror.org/", "")
            if rel.get("type") == "parent":
                parent_ror = rel_ror
            elif rel.get("type") == "child":
                children.append(rel_ror)

        # Extract display name (prefer the ror_display name type)
        names = raw.get("names", [])
        display = next(
            (n["value"] for n in names if "ror_display" in n.get("types", [])),
            raw.get("id", clean_id),
        )

        info = InstitutionInfo(
            ror_id=clean_id, display_name=display,
            country=next(
                (l.get("country", {}).get("country_code", "") for l in raw.get("locations", [])),
                "",
            ),
            type=next(iter(raw.get("types", [])), ""),
            parent_ror_id=parent_ror, parent_name="",
            child_ror_ids=children,
        )
        self.institutions[clean_id] = info
        if parent_ror:
            self.parent_map[clean_id] = parent_ror

    def classify_relationship(self, ror_a, ror_b, dept_a=None, dept_b=None,
                              raw_affil_a="", raw_affil_b=""):
        """
        Determine the institutional relationship between two affiliations.

        Classification hierarchy:
            1. Same ROR ID + same department → SAME_DEPT
            2. Same ROR ID, different departments → SAME_INSTITUTION
            3. Parent-child or shared parent in ROR → SAME_PARENT_ORG
            4. Otherwise → DIFFERENT

        Falls back to fuzzy name matching if no ROR IDs are available.

        Args:
            ror_a, ror_b: ROR IDs (may be None).
            dept_a, dept_b: Department names (may be None).
            raw_affil_a, raw_affil_b: Raw affiliation strings for fuzzy matching.

        Returns:
            One of: "SAME_DEPT", "SAME_INSTITUTION", "SAME_PARENT_ORG", "DIFFERENT".
        """
        # No ROR IDs available → try fuzzy string matching as fallback
        if not ror_a or not ror_b:
            if raw_affil_a and raw_affil_b:
                return self._fuzzy_match(raw_affil_a, raw_affil_b)
            return "DIFFERENT"

        clean_a = ror_a.replace("https://ror.org/", "")
        clean_b = ror_b.replace("https://ror.org/", "")

        # ── Same institution (same ROR ID) ──
        if clean_a == clean_b:
            # Check for department-level match
            if dept_a and dept_b and dept_a.lower() == dept_b.lower():
                return "SAME_DEPT"
            if self._dept_overlap(raw_affil_a, raw_affil_b):
                return "SAME_DEPT"
            # Same institution, but department unclear → conservative classification
            return "SAME_INSTITUTION"

        # ── Parent-child relationship ──
        if self._is_parent_child(clean_a, clean_b):
            return "SAME_PARENT_ORG"

        # ── Shared parent organisation ──
        parent_a = self._get_parent(clean_a)
        parent_b = self._get_parent(clean_b)
        if parent_a and parent_b and parent_a == parent_b:
            return "SAME_PARENT_ORG"
        if parent_a and parent_a == clean_b:
            return "SAME_PARENT_ORG"
        if parent_b and parent_b == clean_a:
            return "SAME_PARENT_ORG"

        return "DIFFERENT"

    def _is_parent_child(self, ror_a, ror_b):
        """Check if one institution is a direct parent/child of the other."""
        return self.parent_map.get(ror_a) == ror_b or self.parent_map.get(ror_b) == ror_a

    def _get_parent(self, ror_id):
        """Look up the parent ROR ID for an institution."""
        if ror_id in self.parent_map:
            return self.parent_map[ror_id]
        info = self.institutions.get(ror_id)
        if info and info.parent_ror_id:
            return info.parent_ror_id
        return None

    def _dept_overlap(self, raw_a, raw_b):
        """
        Heuristic: check if two raw affiliation strings mention the same department.

        Extracts department-like phrases (containing keywords like "department",
        "faculty", "school", etc.) from each string and compares them.

        This is noisy — ROR lacks department-level data for most institutions,
        so we rely on whatever the raw affiliation string contains.
        """
        if not raw_a or not raw_b:
            return False
        dept_keywords = [
            "department", "dept", "division", "school", "faculty",
            "center", "centre", "institute", "lab", "laboratory",
        ]
        parts_a = self._extract_dept(raw_a, dept_keywords)
        parts_b = self._extract_dept(raw_b, dept_keywords)
        if parts_a and parts_b:
            return parts_a == parts_b
        return False

    def _extract_dept(self, raw, keywords):
        """Extract a department-like phrase from a raw affiliation string."""
        raw_lower = raw.lower()
        for kw in keywords:
            if kw in raw_lower:
                for part in raw.split(","):
                    if kw in part.lower():
                        return part.strip().lower()
        return None

    def _fuzzy_match(self, raw_a, raw_b):
        """
        Fallback: fuzzy match institution names when no ROR IDs are available.

        Simple substring/exact match on normalised institution names.
        Results in lower confidence scores in the classification metadata.
        """
        norm_a = raw_a.lower().strip()
        norm_b = raw_b.lower().strip()
        if norm_a == norm_b:
            return "SAME_INSTITUTION"
        if norm_a in norm_b or norm_b in norm_a:
            return "SAME_INSTITUTION"
        return "DIFFERENT"

    def get_name(self, ror_id):
        """Get the display name for a ROR ID (returns the ID itself if unknown)."""
        info = self.institutions.get(ror_id)
        return info.display_name if info else ror_id


# ============================================================
# Phase 3 Classifier
# ============================================================

class AffiliationClassifier:
    """
    The main Phase 3 classifier: combines co-author graph distance with
    temporal affiliation matching.

    Classification priority:
        1. Co-author graph match (SELF / DIRECT / TRANSITIVE) — Phase 2 logic
        2. Affiliation match (SAME_DEPT / SAME_INSTITUTION / SAME_PARENT_ORG)
        3. UNKNOWN (insufficient metadata on either side)
        4. EXTERNAL (data available but no relationship found)

    The affiliation check is only reached if no co-author relationship exists.
    When checking affiliations, the classifier looks up where the target was
    at the time of the cited work, and where each citing author was at the
    time of the citing work.
    """

    def __init__(self, target_id, coauthor_distances, timeline, hierarchy, max_depth=2):
        """
        Args:
            target_id: Target researcher's OpenAlex ID.
            coauthor_distances: Dict from BFS — author_id → distance from target.
            timeline: AffiliationTimeline with temporal affiliation data.
            hierarchy: InstitutionHierarchy for resolving institutional relationships.
            max_depth: Maximum co-author graph depth (typically 2).
        """
        self.target_id = target_id
        self.distances = coauthor_distances
        self.timeline = timeline
        self.hierarchy = hierarchy
        self.max_depth = max_depth

    def classify(self, citing_work, cited_work):
        """
        Classify a single citation using the full Phase 3 detection hierarchy.

        Args:
            citing_work: The paper that contains the citation.
            cited_work: The target researcher's paper being cited.

        Returns:
            CitationClassification with the appropriate label and evidence metadata.
        """
        # ── Phase 2 check first: co-author graph distance ──
        best_distance = None
        best_author_id = None
        best_author_name = None
        for aid, aname in zip(citing_work.author_ids, citing_work.author_names):
            dist = self.distances.get(aid)
            if dist is not None:
                if best_distance is None or dist < best_distance:
                    best_distance = dist
                    best_author_id = aid
                    best_author_name = aname

        # Co-author graph matches take priority over affiliation matching
        if best_distance == 0:
            return self._make(citing_work, cited_work, "SELF", 1.0, 1,
                              {"matching_author_ids": [self.target_id]})
        if best_distance == 1:
            return self._make(citing_work, cited_work, "DIRECT_COAUTHOR", 1.0, 2,
                              {"closest_author_id": best_author_id,
                               "closest_author_name": best_author_name,
                               "graph_distance": 1})
        if best_distance is not None and best_distance <= self.max_depth:
            return self._make(citing_work, cited_work, "TRANSITIVE_COAUTHOR", 1.0, 2,
                              {"closest_author_id": best_author_id,
                               "closest_author_name": best_author_name,
                               "graph_distance": best_distance})

        # ── Phase 3: Temporal affiliation matching ──
        # Look up where the target was at the time of the cited work
        citation_year = citing_work.publication_year
        cited_year = cited_work.publication_year
        target_affils = self.timeline.get_affiliation_at_year(self.target_id, cited_year)

        # Compare against every citing author's affiliation at the citation time
        best_affil_match = "DIFFERENT"
        match_metadata = {}

        for citing_aid in citing_work.author_ids:
            citer_affils = self.timeline.get_affiliation_at_year(citing_aid, citation_year)
            for ta in target_affils:
                for ca in citer_affils:
                    rel = self.hierarchy.classify_relationship(
                        ta.institution_ror, ca.institution_ror,
                        ta.department, ca.department,
                        ta.institution_name, ca.institution_name,
                    )
                    # Keep the strongest (closest) match found
                    if self._match_rank(rel) < self._match_rank(best_affil_match):
                        best_affil_match = rel
                        match_metadata = {
                            "citing_author_id": citing_aid,
                            "citing_institution": ca.institution_name,
                            "citing_institution_ror": ca.institution_ror,
                            "citing_affil_year": ca.year,
                            "target_institution": ta.institution_name,
                            "target_institution_ror": ta.institution_ror,
                            "target_affil_year": ta.year,
                            "temporal_concurrent": (
                                ca.year == ta.year if ca.year and ta.year else None
                            ),
                        }

        # Return affiliation match if found
        if best_affil_match in ("SAME_DEPT", "SAME_INSTITUTION", "SAME_PARENT_ORG"):
            # Confidence is higher when both sides have ROR IDs
            has_ror = bool(
                match_metadata.get("citing_institution_ror")
                and match_metadata.get("target_institution_ror")
            )
            return self._make(citing_work, cited_work, best_affil_match,
                              1.0 if has_ror else 0.7, 3, match_metadata)

        # ── UNKNOWN: insufficient data ──
        if not target_affils:
            return self._make(citing_work, cited_work, "UNKNOWN", 0.5, 3,
                              {"reason": "No affiliation data for target researcher at time of cited work"})

        any_citer_has_affil = False
        for citing_aid in citing_work.author_ids:
            if self.timeline.get_affiliation_at_year(citing_aid, citation_year):
                any_citer_has_affil = True
                break
        if not any_citer_has_affil:
            return self._make(citing_work, cited_work, "UNKNOWN", 0.5, 3,
                              {"reason": "No affiliation data for any citing author at time of citation"})

        # ── EXTERNAL: data available, no relationship found ──
        return self._make(citing_work, cited_work, "EXTERNAL", 1.0, 3,
                          {"affiliation_data_available": True})

    def _match_rank(self, rel):
        """
        Rank affiliation matches for comparison (lower = stronger match).

        Used to keep the strongest match when multiple citing authors
        have different institutional relationships with the target.
        """
        return {"SAME_DEPT": 0, "SAME_INSTITUTION": 1, "SAME_PARENT_ORG": 2, "DIFFERENT": 3}.get(rel, 3)

    def _make(self, citing, cited, cls, conf, phase, meta):
        """Helper: construct a CitationClassification."""
        return CitationClassification(
            citing_work_id=citing.openalex_id, cited_work_id=cited.openalex_id,
            classification=cls, confidence=conf, phase_detected=phase, metadata=meta,
        )


# ============================================================
# Phase 3 Pipeline
# ============================================================

class Phase3Pipeline:
    """
    End-to-end Phase 3 pipeline: the most comprehensive analysis.

    Orchestrates an 11-step workflow:
        1.  Resolve author
        2.  Fetch works
        3.  ORCID cross-validation
        4.  Build co-author graph
        5.  Build affiliation timeline
        6.  Fetch incoming citations (+ update timeline with citing works)
        7.  Build institution hierarchy (OpenAlex + ROR)
        8.  Classify citations (progressive: Phase 1 → 2 → 3)
        9.  Compute career trajectory (optional)
        10. Compute BARON & HEROCON v0.3
        11. Save audit trail

    The pipeline shows progressive scores at each detection step:
    first the Phase 1 (self-citation) baseline, then Phase 2 (co-author),
    then Phase 3 (affiliation), each with the delta from the previous step.
    """

    def __init__(self, console, verbose=False, max_depth=2, skip_orcid=False,
                 show_trajectory=False, since_year=None, herocon_weights=None,
                 exclude_work_ids=None):
        """
        Args:
            console: Rich console for formatted output.
            verbose: Enable verbose logging (reserved for future use).
            max_depth: Co-author graph depth (1, 2, or 3).
            skip_orcid: Skip ORCID cross-validation entirely.
            show_trajectory: Compute cumulative career trajectory.
            since_year: Only include works from this year onward.
            herocon_weights: Custom HEROCON weight configuration.
            exclude_work_ids: Set of OpenAlex work IDs to exclude (from --confirm mode).
        """
        self.console = console
        self.verbose = verbose
        self.max_depth = max_depth
        self.skip_orcid = skip_orcid
        self.show_trajectory = show_trajectory
        self.since_year = since_year
        self.herocon_weights = herocon_weights or HEROCON_WEIGHTS
        self.exclude_work_ids = exclude_work_ids

        # Pipeline state — populated during run()
        self.researcher = None
        self.target_works = {}
        self.citing_works = {}
        self.citations = []
        self.classifications = []
        self.raw_works = []
        self.raw_citing = {}
        self.orcid_result = None
        self.trajectory = []

    async def run(self, identifier):
        """
        Execute the full Phase 3 pipeline.

        Args:
            identifier: ORCID or OpenAlex ID.

        Returns:
            Tuple of (ScoreResult, AuditLog).
        """
        from audit import AuditLog  # Lazy import to avoid circular dependency

        start = time.time()
        self.audit = AuditLog(identifier, phase=3)

        async with OpenAlexClient() as oa_client:

            # ── Step 1: Resolve author ──
            self.console.print("\n[bold cyan]Step 1/11:[/] Resolving author...")
            raw_author = await oa_client.get_author(identifier)
            self.researcher = parse_author(raw_author)
            self.audit.log_researcher(self.researcher)
            self.console.print(
                f"  Found: [bold]{self.researcher.display_name}[/] "
                f"({self.researcher.works_count} works, "
                f"{self.researcher.cited_by_count} citations)"
            )

            # ── Step 2: Fetch all works ──
            self.console.print("\n[bold cyan]Step 2/11:[/] Fetching works...")
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), TextColumn("{task.completed}/{task.total}"),
                          console=self.console) as progress:
                task = progress.add_task("Works", total=self.researcher.works_count)
                def works_cb(done, total):
                    progress.update(task, completed=done, total=total)
                self.raw_works = await oa_client.get_works_by_author(
                    self.researcher.openalex_id, progress_callback=works_cb
                )

            # ── Step 3: ORCID cross-validation + --since filtering ──
            if not self.skip_orcid and self.researcher.orcid:
                self.console.print("\n[bold cyan]Step 3/11:[/] ORCID cross-validation...")
                validator = OrcidValidator(self.console)
                self.orcid_result = await validator.validate(
                    self.researcher.orcid, self.raw_works, since_year=self.since_year
                )

                if self.exclude_work_ids is not None:
                    # ── User explicitly chose which works to exclude (--confirm mode) ──
                    # First remove --since excluded works, then apply user's exclusion choices
                    since_excluded_ids = {
                        w.get("id") for w in self.orcid_result.since_excluded
                    }
                    active = [
                        w for w in self.orcid_result.openalex_works_raw
                        if w.get("id") not in since_excluded_ids
                    ]
                    self.raw_works = [
                        w for w in active
                        if w.get("id", "").replace("https://openalex.org/", "")
                        not in self.exclude_work_ids
                    ]
                    self.console.print(
                        f"    User override: excluding {len(self.exclude_work_ids)} "
                        f"work(s), using {len(self.raw_works)} for scoring"
                    )
                else:
                    self.raw_works = self.orcid_result.works_to_use

            elif self.since_year:
                self.console.print(f"\n[bold cyan]Step 3/11:[/] Filtering works since {self.since_year}...")
                before = len(self.raw_works)
                self.raw_works = [
                    w for w in self.raw_works
                    if not w.get("publication_year") or w["publication_year"] >= self.since_year
                ]
                self.console.print(f"  {before - len(self.raw_works)} work(s) before {self.since_year} excluded")
            elif not self.researcher.orcid:
                self.console.print("\n[bold cyan]Step 3/11:[/] ORCID skipped (no ORCID on profile)")
            else:
                self.console.print("\n[bold cyan]Step 3/11:[/] ORCID skipped (--no-orcid-check)")

            # Parse raw works into typed Work objects
            for rw in self.raw_works:
                wid = rw.get("id", "").replace("https://openalex.org/", "")
                self.target_works[wid] = parse_work(rw, is_target=True)
            self.console.print(f"  {len(self.target_works)} verified works")

            # ── Step 4: Build co-author graph ──
            self.console.print("\n[bold cyan]Step 4/11:[/] Building co-author graph...")
            graph = CoAuthorGraph()
            for wid, work in self.target_works.items():
                graph.add_paper(work.author_ids, work.author_names, work.publication_year, wid)
            distances = graph.bfs(self.researcher.openalex_id, self.max_depth)
            direct = sum(1 for d in distances.values() if d == 1)
            transitive = sum(1 for d in distances.values() if d == 2)
            self.console.print(f"  Network: {direct} direct, {transitive} transitive co-authors")

            # ── Step 5: Build affiliation timeline from target works ──
            self.console.print("\n[bold cyan]Step 5/11:[/] Building affiliation timeline...")
            timeline = AffiliationTimeline()
            for rw in self.raw_works:
                wid = rw.get("id", "").replace("https://openalex.org/", "")
                timeline.add_from_work(wid, rw.get("publication_year"), rw.get("authorships", []))
            self.console.print(
                f"  Timeline: {timeline.author_count} authors, "
                f"{timeline.record_count} affiliation records"
            )

            # ── Step 6: Fetch incoming citations ──
            cited_works = {wid: w for wid, w in self.target_works.items() if w.cited_by_count > 0}
            total_expected = sum(w.cited_by_count for w in cited_works.values())
            self.console.print(
                f"\n[bold cyan]Step 6/11:[/] Fetching incoming citations "
                f"(~{total_expected} across {len(cited_works)} works)..."
            )
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), TextColumn("{task.completed}/{task.total} works"),
                          console=self.console) as progress:
                task = progress.add_task("Citations", total=len(cited_works))
                def cite_cb(done, total):
                    progress.update(task, completed=done, total=total)
                self.raw_citing = await oa_client.get_citing_works_batch(
                    list(cited_works.keys()), progress_callback=cite_cb
                )

            # Build citation links AND update the affiliation timeline with citing works
            for cited_wid, raw_citers in self.raw_citing.items():
                for rc in raw_citers:
                    cw = parse_work(rc, is_target=False)
                    self.citing_works[cw.openalex_id] = cw
                    self.citations.append(Citation(
                        citing_work_id=cw.openalex_id,
                        cited_work_id=cited_wid,
                        citation_year=cw.publication_year,
                    ))
                    # Enrich the timeline with citing authors' affiliations
                    wid_c = rc.get("id", "").replace("https://openalex.org/", "")
                    timeline.add_from_work(
                        wid_c, rc.get("publication_year"), rc.get("authorships", [])
                    )
            self.console.print(
                f"  {len(self.citing_works)} citing works, {len(self.citations)} citation links"
            )
            self.console.print(
                f"  Timeline updated: {timeline.author_count} authors, "
                f"{timeline.record_count} records"
            )

            # ── Step 7: Build institution hierarchy ──
            self.console.print("\n[bold cyan]Step 7/11:[/] Building institution hierarchy...")
            hierarchy = InstitutionHierarchy()

            # Collect all ROR IDs and OpenAlex institution IDs from the data
            target_ror_ids = timeline.get_all_institutions(self.researcher.openalex_id)
            all_ror_ids = set(target_ror_ids)
            inst_oaids = set()

            # From target works
            for rw in self.raw_works:
                for a in rw.get("authorships", []):
                    for inst in a.get("institutions", []):
                        oaid = (inst.get("id") or "").replace("https://openalex.org/", "")
                        if oaid:
                            inst_oaids.add(oaid)

            # From citing works
            for cited_wid, raw_citers in self.raw_citing.items():
                for rc in raw_citers:
                    for a in rc.get("authorships", []):
                        for inst in a.get("institutions", []):
                            oaid = (inst.get("id") or "").replace("https://openalex.org/", "")
                            if oaid:
                                inst_oaids.add(oaid)
                            ror = (inst.get("ror") or "").replace("https://ror.org/", "")
                            if ror:
                                all_ror_ids.add(ror)

            # Fetch institution profiles from OpenAlex
            self.console.print(f"  Fetching {len(inst_oaids)} institution profiles...")
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), TextColumn("{task.completed}/{task.total}"),
                          console=self.console) as progress:
                task = progress.add_task("Institutions", total=len(inst_oaids))
                def inst_cb(done, total):
                    progress.update(task, completed=done, total=total)
                inst_data = await oa_client.get_institutions_batch(
                    list(inst_oaids), progress_callback=inst_cb
                )
            for oaid, raw_inst in inst_data.items():
                hierarchy.add_from_openalex(raw_inst)

            # Fetch ROR hierarchy data for the target's institutions
            self.console.print(
                f"  Fetching ROR hierarchy for {len(target_ror_ids)} target institutions..."
            )
            async with RORClient() as ror_client:
                ror_data = await ror_client.get_organizations_batch(list(target_ror_ids))
                for ror_id, raw_ror in ror_data.items():
                    hierarchy.add_from_ror(ror_id, raw_ror)
            self.console.print(
                f"  Hierarchy: {len(hierarchy.institutions)} institutions, "
                f"{len(hierarchy.parent_map)} parent links"
            )

            # ── Step 8: Progressive Classification ──
            # Run all three phases and show scores at each step
            self.console.print("\n[bold cyan]Step 8/11:[/] Classifying citations (progressive)...\n")

            # Step 8a: Self-citation pass (Phase 1 baseline)
            self_classifier = SelfCitationClassifier(self.researcher.openalex_id)
            self_only_cls = []
            for cit in self.citations:
                citing_w = self.citing_works.get(cit.citing_work_id)
                cited_w = self.target_works.get(cit.cited_work_id)
                if citing_w and cited_w:
                    self_only_cls.append(self_classifier.classify(citing_w, cited_w))

            total = len(self_only_cls)
            self_count = sum(1 for c in self_only_cls if c.classification == "SELF")
            step1_baron = (total - self_count) / total * 100 if total > 0 else 0
            self.console.print(
                f"  [dim]Step 1 — Self-citation detection:[/]\n"
                f"    BARON  [bold yellow]{step1_baron:.1f}%[/]"
                f"                      [dim]({self_count} self-citations removed)[/]\n"
            )

            # Step 8b: Co-author pass (Phase 2)
            from phase2 import CoAuthorClassifier
            coauth_classifier = CoAuthorClassifier(
                self.researcher.openalex_id, graph, self.max_depth
            )
            coauth_cls = []
            for cit in self.citations:
                citing_w = self.citing_works.get(cit.citing_work_id)
                cited_w = self.target_works.get(cit.cited_work_id)
                if citing_w and cited_w:
                    coauth_cls.append(coauth_classifier.classify(citing_w, cited_w))

            ext2 = sum(1 for c in coauth_cls if c.classification == "EXTERNAL")
            coauth_count = sum(
                1 for c in coauth_cls
                if c.classification in ("DIRECT_COAUTHOR", "TRANSITIVE_COAUTHOR")
            )
            step2_baron = ext2 / total * 100 if total > 0 else 0
            step2_herocon = compute_herocon_score(coauth_cls, weights=self.herocon_weights)
            delta2 = step1_baron - step2_baron
            self.console.print(
                f"  [dim]Step 2 — Co-author network:[/]\n"
                f"    BARON  [bold yellow]{step2_baron:.1f}%[/]  [red]↓{delta2:.1f}%[/]"
                f"    HEROCON  [bold green]{step2_herocon:.1f}%[/]"
                f"    [dim]({coauth_count} co-author citations detected)[/]\n"
            )

            # Step 8c: Affiliation pass (Phase 3 — the main classification)
            classifier = AffiliationClassifier(
                self.researcher.openalex_id, distances, timeline, hierarchy, self.max_depth
            )
            for cit in self.citations:
                citing_w = self.citing_works.get(cit.citing_work_id)
                cited_w = self.target_works.get(cit.cited_work_id)
                if citing_w and cited_w:
                    self.classifications.append(classifier.classify(citing_w, cited_w))

            ext3 = sum(1 for c in self.classifications if c.classification == "EXTERNAL")
            affil_count = sum(
                1 for c in self.classifications
                if c.classification in ("SAME_DEPT", "SAME_INSTITUTION", "SAME_PARENT_ORG")
            )
            unknown_count = sum(1 for c in self.classifications if c.classification == "UNKNOWN")
            classifiable = total - unknown_count
            step3_baron = ext3 / classifiable * 100 if classifiable > 0 else 0
            step3_herocon = compute_herocon_score(self.classifications, weights=self.herocon_weights)
            delta3 = step2_baron - step3_baron
            self.console.print(
                f"  [dim]Step 3 — Affiliation matching:[/]\n"
                f"    BARON  [bold yellow]{step3_baron:.1f}%[/]  [red]↓{delta3:.1f}%[/]"
                f"    HEROCON  [bold green]{step3_herocon:.1f}%[/]"
                f"    [dim]({affil_count} institutional, {unknown_count} unknown)[/]"
            )
            self.console.print(
                f"\n  ─── [bold]Final[/] ─────────────────────────────\n"
                f"    BARON  [bold yellow]{step3_baron:.1f}%[/]"
                f"             HEROCON  [bold green]{step3_herocon:.1f}%[/]\n"
                f"    Gap    [dim]{step3_herocon - step3_baron:.1f}%[/]\n"
            )

            # ── Step 9: Career trajectory (optional) ──
            if self.show_trajectory:
                self.console.print("[bold cyan]Step 9/11:[/] Computing career trajectory...")
                self.trajectory = compute_trajectory(
                    self.classifications, self.target_works, self.citing_works,
                    herocon_weights=self.herocon_weights,
                )
            else:
                self.console.print("[bold cyan]Step 9/11:[/] Trajectory skipped (use --trajectory)")

            # ── Step 10: Compute final scores ──
            self.console.print("[bold cyan]Step 10/11:[/] Computing BARON & HEROCON v0.3...")
            score = self._compute_score(
                time.time() - start, oa_client.api_calls,
                graph, distances, timeline, hierarchy,
            )

            # ── Step 11: Save audit trail ──
            self.console.print("[bold cyan]Step 11/11:[/] Saving audit trail...")
            self.audit.log_works(self.target_works, label="target")
            self.audit.log_works(self.citing_works, label="citing")
            self.audit.log_citations(self.citations)
            self.audit.log_classifications(
                self.classifications, self.target_works, self.citing_works
            )
            self.audit.log_coauthor_graph(graph, self.researcher.openalex_id, self.max_depth)
            self.audit.log_score(score)
            self.audit.log_ingestion(score.ingestion_stats)
            self._log_affiliation_audit(timeline, hierarchy, target_ror_ids)
            if self.orcid_result:
                self.audit.doc["orcid_validation"] = self.orcid_result.to_dict()
            if self.trajectory:
                self.audit.doc["trajectory"] = self.trajectory

            self.console.print("Done.\n")
            return score, self.audit

    def _log_affiliation_audit(self, timeline, hierarchy, target_ror_ids):
        """
        Log Phase 3-specific affiliation data to the audit trail.

        Captures the target researcher's affiliation history, detailed
        institution metadata, and timeline/hierarchy statistics.
        """
        # Target researcher's affiliation history (chronological)
        target_records = timeline.records.get(self.researcher.openalex_id, [])
        affil_history = [
            {
                "year": r.year, "institution": r.institution_name,
                "ror_id": r.institution_ror, "source_work": r.source_work_id,
                "department": r.department,
            }
            for r in sorted(target_records, key=lambda x: x.year or 0)
        ]

        # Detailed metadata for each of the target's institutions
        inst_details = {}
        for ror_id in target_ror_ids:
            info = hierarchy.institutions.get(ror_id)
            if info:
                inst_details[ror_id] = {
                    "name": info.display_name, "country": info.country,
                    "type": info.type, "parent_ror": info.parent_ror_id,
                    "parent_name": hierarchy.get_name(info.parent_ror_id) if info.parent_ror_id else None,
                }

        self.audit.doc["affiliation_data"] = {
            "target_affiliation_history": affil_history,
            "target_institutions": inst_details,
            "timeline_stats": {
                "total_authors_tracked": timeline.author_count,
                "total_affiliation_records": timeline.record_count,
            },
            "hierarchy_stats": {
                "institutions_loaded": len(hierarchy.institutions),
                "parent_links": len(hierarchy.parent_map),
            },
        }

    def _compute_score(self, elapsed, api_calls, graph, distances, timeline, hierarchy):
        """
        Compute the full BARON v0.3 and HEROCON v0.3 scores.

        Phase 3 breakdown includes seven classifiable categories plus UNKNOWN:
            SELF, DIRECT_COAUTHOR, TRANSITIVE_COAUTHOR,
            SAME_DEPT, SAME_INSTITUTION, SAME_PARENT_ORG,
            EXTERNAL, UNKNOWN
        """
        # ── Count classifications by category ──
        breakdown = ScoreBreakdown(total_citations=len(self.classifications))
        for cls in self.classifications:
            c = cls.classification
            if c == "SELF":
                breakdown.self_citations += 1
            elif c == "DIRECT_COAUTHOR":
                breakdown.direct_coauthor_citations += 1
            elif c == "TRANSITIVE_COAUTHOR":
                breakdown.transitive_coauthor_citations += 1
            elif c == "SAME_DEPT":
                breakdown.same_dept_citations += 1
            elif c == "SAME_INSTITUTION":
                breakdown.same_institution_citations += 1
            elif c == "SAME_PARENT_ORG":
                breakdown.same_parent_org_citations += 1
            elif c == "UNKNOWN":
                breakdown.unknown_citations += 1
            else:
                breakdown.external_citations += 1

        # BARON: percentage of classifiable citations that are EXTERNAL
        baron = breakdown.pct(breakdown.external_citations)
        # HEROCON: weighted sum of all classifiable citations
        herocon = compute_herocon_score(self.classifications, weights=self.herocon_weights)

        # ── Top self-cited works ──
        self_cite_counts = defaultdict(int)
        for cls in self.classifications:
            if cls.classification == "SELF":
                self_cite_counts[cls.cited_work_id] += 1
        top_self = sorted(self_cite_counts.items(), key=lambda x: -x[1])[:5]
        top_self_works = [
            {
                "title": self.target_works[wid].title,
                "year": self.target_works[wid].publication_year,
                "self_citations": count,
                "total_citations": self.target_works[wid].cited_by_count,
            }
            for wid, count in top_self if wid in self.target_works
        ]

        # ── Co-author network statistics ──
        top_coauthors = graph.top_coauthors(self.researcher.openalex_id, 10)
        coauthor_stats = {
            "graph_nodes": graph.node_count,
            "graph_edges": graph.edge_count,
            "direct_coauthors": sum(1 for d in distances.values() if d == 1),
            "transitive_coauthors": sum(1 for d in distances.values() if d == 2),
            "top_coauthors": [
                {
                    "name": name, "openalex_id": aid,
                    "shared_papers": edge.shared_papers,
                    "strength": round(edge.strength, 2),
                    "last_collab": edge.last_collab_year,
                }
                for aid, name, edge in top_coauthors
            ],
        }

        # ── Affiliation statistics ──
        target_ror_ids = timeline.get_all_institutions(self.researcher.openalex_id)
        affiliation_stats = {
            "target_institutions": [
                {"ror_id": rid, "name": hierarchy.get_name(rid)}
                for rid in target_ror_ids
            ],
            "timeline_authors_tracked": timeline.author_count,
            "affiliation_records": timeline.record_count,
            "institutions_in_hierarchy": len(hierarchy.institutions),
        }

        # Reference coverage metric
        works_with_refs = sum(1 for w in self.target_works.values() if w.referenced_work_ids)
        ref_coverage = works_with_refs / len(self.target_works) * 100 if self.target_works else 0

        return ScoreResult(
            researcher=self.researcher, phase="v0.3",
            baron_score=baron, herocon_score=herocon, breakdown=breakdown,
            top_self_cited_works=top_self_works, coauthor_stats=coauthor_stats,
            herocon_weights_used=self.herocon_weights,
            ingestion_stats={
                "works_fetched": len(self.target_works),
                "citing_works_fetched": len(self.citing_works),
                "citation_links": len(self.citations),
                "institutions_fetched": len(hierarchy.institutions),
                "reference_coverage": f"{ref_coverage:.1f}%",
                "api_calls": api_calls,
                "time_elapsed": format_elapsed(elapsed),
                "affiliation_stats": affiliation_stats,
            },
        )


# ============================================================
# Display
# ============================================================

def display_score(console, score, trajectory=None):
    """
    Render the Phase 3 score to the terminal using Rich formatting.

    Shows: researcher info, BARON & HEROCON scores, full breakdown
    (co-author + affiliation categories with HEROCON weights), data
    quality metrics, optional career trajectory, and the disclaimer.
    """
    b = score.breakdown

    # ── Header panel ──
    console.print(Panel(
        f"[bold]{score.researcher.display_name}[/]\n"
        f"ORCID: {score.researcher.orcid or 'N/A'}  |  "
        f"OpenAlex: {score.researcher.openalex_id}  |  "
        f"Works: {score.researcher.works_count}",
        title="[bold cyan]BARON & HEROCON v0.3 — Affiliation Matching[/]",
        border_style="cyan",
    ))

    # ── Score breakdown with all Phase 3 categories ──
    sc = Table(show_header=False, box=None, padding=(0, 2))
    sc.add_column(style="dim", width=34)
    sc.add_column(justify="right")
    sc.add_row("[bold]BARON v0.3[/]", f"[bold yellow]{score.baron_score:.1f}%[/]")
    sc.add_row("[bold]HEROCON v0.3[/]", f"[bold green]{score.herocon_score:.1f}%[/]")
    sc.add_row("  [dim]Gap (HEROCON − BARON)[/]", f"[dim]{score.herocon_score - score.baron_score:.1f}%[/]")
    sc.add_row("", "")
    sc.add_row("  [green]External[/] citations",
               f"[green]{b.external_citations}[/] ({b.pct(b.external_citations):.1f}%)")
    sc.add_row("", "")
    # Co-author in-group categories (Phase 2)
    sc.add_row("  [dim]Co-author in-group:[/]", "")
    sc.add_row("    Self-citations",
               f"[red]{b.self_citations}[/] ({b.pct(b.self_citations):.1f}%) → 0.0")
    sc.add_row("    Direct co-author",
               f"[magenta]{b.direct_coauthor_citations}[/] ({b.pct(b.direct_coauthor_citations):.1f}%) → 0.2")
    sc.add_row("    Transitive co-author",
               f"[blue]{b.transitive_coauthor_citations}[/] ({b.pct(b.transitive_coauthor_citations):.1f}%) → 0.5")
    sc.add_row("", "")
    # Affiliation in-group categories (Phase 3)
    sc.add_row("  [dim]Affiliation in-group:[/]", "")
    sc.add_row("    Same department",
               f"[red]{b.same_dept_citations}[/] ({b.pct(b.same_dept_citations):.1f}%) → 0.1")
    sc.add_row("    Same institution",
               f"[yellow]{b.same_institution_citations}[/] ({b.pct(b.same_institution_citations):.1f}%) → 0.4")
    sc.add_row("    Same parent org",
               f"[cyan]{b.same_parent_org_citations}[/] ({b.pct(b.same_parent_org_citations):.1f}%) → 0.7")
    sc.add_row("", "")
    # Data quality metrics
    if b.unknown_citations > 0:
        sc.add_row("  [dim]Insufficient data:[/]", "")
        sc.add_row("    UNKNOWN",
                   f"[dim]{b.unknown_citations}[/] ({b.pct_of_total(b.unknown_citations):.1f}% of total)")
        sc.add_row("", "")
    sc.add_row("  Total citations", f"{b.total_citations}")
    sc.add_row("  Classifiable", f"{b.classifiable_citations} ({b.data_quality_pct:.0f}%)")
    sc.add_row("  Reliability", f"[bold]{b.reliability}[/]")
    console.print(Panel(sc, title="[bold yellow]Score[/]", border_style="yellow"))

    # ── Career trajectory (optional) ──
    if trajectory:
        tr = Table(box=None, padding=(0, 2))
        tr.add_column("Year", style="dim", justify="center")
        tr.add_column("Citations", justify="right")
        tr.add_column("BARON", justify="right")
        tr.add_column("HEROCON", justify="right")
        for row in trajectory:
            m = f"[yellow]{row['baron']}%[/]" if row.get("baron") is not None else "[dim]—[/]"
            h = f"[green]{row['herocon']}%[/]" if row.get("herocon") is not None else "[dim]—[/]"
            tr.add_row(str(row["year"]), str(row["total_citations"]), m, h)
        console.print(Panel(tr, title="[bold]Career Trajectory[/] (cumulative)", border_style="blue"))

    # ── Disclaimer ──
    console.print(f"\n[dim italic]{DISCLAIMER}[/]\n")


# ============================================================
# CLI Helpers
# ============================================================

def parse_exclusion_input(raw: str, max_index: int) -> set[int]:
    """
    Parse user input for the --confirm interactive work exclusion prompt.

    Supports several input formats:
        "all"       → exclude everything:  {1, 2, ..., max_index}
        "none"      → exclude nothing:     {}
        "1,3,5"     → specific indices:    {1, 3, 5}
        "1-3,5"     → ranges + singles:    {1, 2, 3, 5}
        "1-3, 7-9"  → multiple ranges:     {1, 2, 3, 7, 8, 9}

    Args:
        raw: The raw input string from the user.
        max_index: Maximum valid index (1-based, inclusive).

    Returns:
        Set of 1-based indices to exclude.

    Raises:
        ValueError: If the input contains invalid numbers or out-of-range indices.
    """
    raw = raw.strip().lower()

    if raw in ("all", "a"):
        return set(range(1, max_index + 1))
    if raw in ("none", "n", ""):
        return set()

    result = set()
    for part in raw.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            # Range: "1-3" → {1, 2, 3}
            try:
                lo, hi = part.split("-", 1)
                lo, hi = int(lo), int(hi)
                result.update(range(lo, hi + 1))
            except ValueError:
                raise ValueError(f"Invalid range: '{part}'. Use e.g. 1-3")
        else:
            # Single index
            try:
                result.add(int(part))
            except ValueError:
                raise ValueError(f"Invalid number: '{part}'")

    # Validate all indices are within the valid range
    out_of_range = {i for i in result if i < 1 or i > max_index}
    if out_of_range:
        raise ValueError(f"Index out of range (1–{max_index}): {out_of_range}")
    return result


# ============================================================
# CLI
# ============================================================

app = typer.Typer(
    name="baron-herocon-p3",
    help="BARON & HEROCON Phase 3: Affiliation Matching",
)


@app.command()
def score(
    orcid: Optional[str] = typer.Option(None, "--orcid"),
    openalex_id: Optional[str] = typer.Option(None, "--openalex-id"),
    depth: int = typer.Option(2, "--depth", "-d"),
    since: Optional[int] = typer.Option(None, "--since"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    trajectory: bool = typer.Option(False, "--trajectory", "-t"),
    export: Optional[str] = typer.Option(None, "--export"),
    no_audit: bool = typer.Option(False, "--no-audit"),
    no_orcid_check: bool = typer.Option(False, "--no-orcid-check"),
    herocon_weights_file: Optional[str] = typer.Option(None, "--herocon-weights"),
    confirm: bool = typer.Option(
        False, "--confirm", "-c",
        help="Review ORCID-flagged works interactively before scoring. "
             "Expects: 'all', 'none', or index ranges like '1,3,5' or '1-3'.",
    ),
):
    """Compute BARON & HEROCON v0.3 with affiliation matching."""
    console = Console()
    if not orcid and not openalex_id:
        console.print("[bold red]Error:[/] Provide --orcid or --openalex-id")
        raise typer.Exit(1)

    identifier = orcid or openalex_id
    console.print(f"\n[bold]BARON & HEROCON v0.3[/] — Affiliation Matching (depth={depth})")
    console.print(f"Target: [cyan]{identifier}[/]\n")

    # Load custom HEROCON weights if a weights file was provided
    herocon_weights = None
    if herocon_weights_file:
        with open(herocon_weights_file, "r") as f:
            herocon_weights = json.load(f)

    # ── Confirm mode: validate first, prompt user, then run ──
    # This two-stage workflow lets the user review ORCID-flagged works
    # before committing to a full analysis run.
    exclude_work_ids = None

    if confirm and not no_orcid_check and orcid:
        console.print("[bold cyan]Confirm mode:[/] fetching works and validating against ORCID...\n")

        async def _validate():
            """Quick validation pass: fetch works + run ORCID check only."""
            async with OpenAlexClient() as client:
                raw_author = await client.get_author(identifier)
                researcher = parse_author(raw_author)
                raw_works = await client.get_works_by_author(researcher.openalex_id)

                validator = OrcidValidator(console)
                result = await validator.validate(researcher.orcid, raw_works, since_year=since)
                return result

        val_result = asyncio.run(_validate())
        flagged = val_result.flagged_works
        since_excluded = val_result.since_excluded

        # Show --since excluded works (informational)
        if since_excluded:
            console.print(f"\n  [bold cyan]{len(since_excluded)} work(s) excluded by --since {since}[/]")
            for i, w in enumerate(since_excluded[:10], 1):
                title = w.get("title", "Untitled")
                year = w.get("publication_year", "?")
                console.print(f"    {i}. [dim]{title}[/] ({year})")
            if len(since_excluded) > 10:
                console.print(f"    [dim]... and {len(since_excluded) - 10} more[/]")

        # Show flagged works and prompt for exclusion
        if not flagged:
            console.print("\n  [green]✓ No flagged works — proceeding with full analysis.[/]\n")
        else:
            console.print(f"\n  [bold yellow]⚠ {len(flagged)} work(s) flagged:[/]\n")
            flagged_index = []
            for i, fw in enumerate(flagged, 1):
                w = fw["work"]
                title = w.get("title", "Untitled")
                if len(title) > 70:
                    title = title[:67] + "..."
                year = w.get("publication_year", "?")
                reason = fw.get("reason", "")
                oa_id = w.get("id", "").replace("https://openalex.org/", "")
                flagged_index.append(oa_id)
                console.print(f"    [bold]{i}.[/] {title} ({year})")
                console.print(f"       [dim]{reason}[/]")

            # Interactive prompt: which flagged works to exclude?
            console.print(
                f"\n  [bold]Exclude which?[/] "
                f"[dim](all / none / 1,3,5 / 1-3,5)[/]"
            )
            try:
                raw_input = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Cancelled.[/]")
                raise typer.Exit(0)

            try:
                selected = parse_exclusion_input(raw_input, len(flagged))
            except ValueError as e:
                console.print(f"[bold red]Error:[/] {e}")
                raise typer.Exit(1)

            # Convert 1-based indices to OpenAlex work IDs
            exclude_work_ids = {flagged_index[i - 1] for i in selected}

            if exclude_work_ids:
                console.print(f"\n  Excluding {len(exclude_work_ids)} work(s). Running full analysis...\n")
            else:
                console.print(f"\n  Keeping all flagged works. Running full analysis...\n")

    elif confirm and (no_orcid_check or not orcid):
        console.print("[yellow]--confirm has no effect without ORCID validation. Proceeding normally.[/]\n")

    # ── Run the full Phase 3 pipeline ──
    pipeline = Phase3Pipeline(
        console, verbose=verbose, max_depth=depth,
        skip_orcid=no_orcid_check, show_trajectory=trajectory,
        since_year=since, herocon_weights=herocon_weights,
        exclude_work_ids=exclude_work_ids,
    )
    result, audit = asyncio.run(pipeline.run(identifier))

    # Display results
    display_score(console, result, trajectory=pipeline.trajectory if trajectory else None)

    # Save audit trail (on by default)
    if not no_audit:
        audit_file = audit.save()
        console.print(f"[dim]Audit trail saved to:[/] [bold green]{audit_file}[/]")
        console.print(f"[dim]  → {len(audit.doc['classifications'])} citations classified[/]")
        console.print(f"[dim]  → Affiliation timeline and institution hierarchy logged[/]")
        console.print(f"[dim]  → Every decision documented for full transparency[/]\n")

    # Optional JSON export
    if export:
        export_data = {
            "version": "v0.3", "phase": 3,
            "created_at": datetime.now().isoformat(),
            "disclaimer": DISCLAIMER,
            "config": {"coauthor_depth": depth},
            "researcher": asdict(result.researcher),
            "score": {
                "baron_v03": round(result.baron_score, 1),
                "herocon_v03": round(result.herocon_score, 1),
                "data_quality_pct": round(result.breakdown.data_quality_pct, 1),
                "reliability": result.breakdown.reliability,
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
