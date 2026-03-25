"""
citation-constellation/models.py
=================================
Shared data models used across all phases.

This module defines every data structure that flows through the pipeline:
  - Core entities (Researcher, Work, Citation, CitationClassification)
  - Score computation (ScoreBreakdown, ScoreResult)
  - HEROCON weighted scoring system
  - Co-author graph edges (Phase 2+)
  - Affiliation records and institution metadata (Phase 3+)
  - Parsing helpers to convert raw OpenAlex JSON into typed objects

Design principle: all models are plain dataclasses with no external
dependencies. This keeps them serialisable, testable, and easy to
reason about. Business logic lives in the phase modules; models are
just containers.
"""

from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# Core Entities
# ============================================================

@dataclass
class Researcher:
    """
    A single researcher resolved from OpenAlex.

    The openalex_id is the canonical identifier used throughout the
    pipeline. ORCID is optional — many researchers don't have one,
    and some OpenAlex profiles lack the ORCID link even when one exists.
    """
    openalex_id: str
    orcid: Optional[str] = None
    display_name: str = ""
    works_count: int = 0        # Total works attributed by OpenAlex
    cited_by_count: int = 0     # Total incoming citations across all works


@dataclass
class Work:
    """
    A single scholarly work (paper, preprint, book chapter, etc.).

    Works appear in two roles throughout the pipeline:
      - "target" works: publications authored by the researcher under analysis
      - "citing" works: publications that cite one of the target works

    The author_ids and author_names lists are parallel — author_ids[i]
    corresponds to author_names[i]. Both are extracted from OpenAlex's
    authorships array.
    """
    openalex_id: str
    doi: Optional[str] = None
    title: str = ""
    publication_year: Optional[int] = None
    venue_name: str = ""                          # Journal or conference name
    venue_openalex_id: Optional[str] = None       # OpenAlex source ID
    work_type: str = ""                           # e.g. "article", "book-chapter"
    cited_by_count: int = 0
    is_target_work: bool = False                  # True if authored by the target researcher
    author_ids: list = field(default_factory=list)        # Parallel list: OpenAlex author IDs
    author_names: list = field(default_factory=list)      # Parallel list: display names
    referenced_work_ids: list = field(default_factory=list)  # Outgoing references (OpenAlex IDs)


@dataclass
class WorkAuthor:
    """
    A single author–work relationship with institutional affiliation.

    Used primarily in Phase 1 for detailed author-level metadata.
    Captures the author's institution at the time of publication,
    which is important for temporal affiliation matching in Phase 3.
    """
    work_openalex_id: str
    author_openalex_id: str
    author_name: str = ""
    author_position: str = ""           # "first", "middle", or "last"
    institution_name: str = ""          # Institution at time of publication
    institution_ror: Optional[str] = None  # ROR ID for the institution (if available)


@dataclass
class Citation:
    """
    A single directed citation link: one work citing another.

    This is the fundamental unit that gets classified. The citing_work_id
    is the paper doing the citing; the cited_work_id is the target
    researcher's paper being cited. citation_year is when the citing
    paper was published (used for temporal affiliation matching).
    """
    citing_work_id: str
    cited_work_id: str
    citation_year: Optional[int] = None


@dataclass
class CitationClassification:
    """
    The result of classifying a single citation.

    Every citation in the pipeline receives exactly one classification.
    The classification label determines how the citation contributes to
    BARON (binary: in-group=0, external=1) and HEROCON (graduated weights).

    Possible classification values:
      Phase 1: SELF, NON_SELF
      Phase 2: SELF, DIRECT_COAUTHOR, TRANSITIVE_COAUTHOR, EXTERNAL
      Phase 3: + SAME_DEPT, SAME_INSTITUTION, SAME_PARENT_ORG, UNKNOWN
      Phase 4: + VENUE_SELF_GOVERNANCE, VENUE_EDITOR_COAUTHOR,
               VENUE_EDITOR_AFFIL, VENUE_COMMITTEE (planned)

    The metadata dict contains classification-specific evidence:
      - For SELF: matching_author_ids
      - For co-author classes: closest_author_id, graph_distance, etc.
      - For affiliation classes: institution names, ROR IDs, years
      - For UNKNOWN: reason string explaining why classification failed

    This metadata is logged verbatim in the audit trail for full
    transparency — any researcher can see exactly why each citation
    was classified the way it was.
    """
    citing_work_id: str
    cited_work_id: str
    classification: str             # The label (e.g. "SELF", "EXTERNAL")
    confidence: float = 1.0         # 0.0–1.0, lower when data is incomplete
    phase_detected: int = 1         # Which phase first classified this citation
    metadata: Optional[dict] = None  # Evidence supporting the classification


# ============================================================
# Score Results
# ============================================================

@dataclass
class ScoreBreakdown:
    """
    Breakdown of citation classifications at any phase.

    Tracks counts for every classification category. The key design
    decision: UNKNOWN citations (insufficient metadata) are excluded
    from both BARON and HEROCON denominators. This prevents missing
    data from inflating or deflating scores, and the data_quality_pct
    makes the exclusion transparent.

    Properties compute derived metrics:
      - classifiable_citations: total minus unknowns
      - data_quality_pct: what fraction of citations had enough data
      - reliability: human-readable quality label (HIGH/MODERATE/LOW/VERY LOW)
      - pct(): percentage relative to classifiable (used for BARON/HEROCON)
      - pct_of_total(): percentage relative to total (used for UNKNOWN display)
    """
    total_citations: int = 0
    self_citations: int = 0
    direct_coauthor_citations: int = 0
    transitive_coauthor_citations: int = 0
    same_dept_citations: int = 0           # Phase 3+
    same_institution_citations: int = 0     # Phase 3+
    same_parent_org_citations: int = 0      # Phase 3+
    external_citations: int = 0
    unknown_citations: int = 0              # Insufficient data for classification

    @property
    def in_group_citations(self) -> int:
        """Total citations from within the researcher's network (all in-group categories)."""
        return (
            self.self_citations
            + self.direct_coauthor_citations
            + self.transitive_coauthor_citations
            + self.same_dept_citations
            + self.same_institution_citations
            + self.same_parent_org_citations
        )

    @property
    def classifiable_citations(self) -> int:
        """Citations with sufficient metadata for classification (excludes UNKNOWN)."""
        return self.total_citations - self.unknown_citations

    @property
    def data_quality_pct(self) -> float:
        """Percentage of citations with sufficient data. Higher is better."""
        if self.total_citations == 0:
            return 0.0
        return self.classifiable_citations / self.total_citations * 100

    @property
    def reliability(self) -> str:
        """
        Human-readable score reliability based on data quality.

        Thresholds:
          ≥85% → HIGH       (scores are trustworthy)
          ≥70% → MODERATE   (scores are reasonable but treat with care)
          ≥50% → LOW        (significant data gaps — interpret cautiously)
          <50% → VERY LOW   (too much missing data for reliable scoring)
        """
        q = self.data_quality_pct
        if q >= 85:
            return "HIGH"
        elif q >= 70:
            return "MODERATE"
        elif q >= 50:
            return "LOW"
        return "VERY LOW"

    def pct(self, count: int) -> float:
        """
        Percentage relative to classifiable citations (not total).

        This is the denominator used for BARON and HEROCON scores.
        UNKNOWN citations are excluded so that missing data doesn't
        artificially inflate or deflate the final score.
        """
        return count / self.classifiable_citations * 100 if self.classifiable_citations > 0 else 0.0

    def pct_of_total(self, count: int) -> float:
        """Percentage relative to total citations (including UNKNOWN). Used for display only."""
        return count / self.total_citations * 100 if self.total_citations > 0 else 0.0

    def to_dict(self) -> dict:
        """Serialise breakdown to a flat dictionary for JSON export and audit logging."""
        return {
            "total_citations": self.total_citations,
            "classifiable_citations": self.classifiable_citations,
            "unknown_citations": self.unknown_citations,
            "data_quality_pct": round(self.data_quality_pct, 1),
            "reliability": self.reliability,
            "self_citations": self.self_citations,
            "self_citation_pct": round(self.pct(self.self_citations), 1),
            "direct_coauthor_citations": self.direct_coauthor_citations,
            "direct_coauthor_pct": round(self.pct(self.direct_coauthor_citations), 1),
            "transitive_coauthor_citations": self.transitive_coauthor_citations,
            "transitive_coauthor_pct": round(self.pct(self.transitive_coauthor_citations), 1),
            "same_dept_citations": self.same_dept_citations,
            "same_dept_pct": round(self.pct(self.same_dept_citations), 1),
            "same_institution_citations": self.same_institution_citations,
            "same_institution_pct": round(self.pct(self.same_institution_citations), 1),
            "same_parent_org_citations": self.same_parent_org_citations,
            "same_parent_org_pct": round(self.pct(self.same_parent_org_citations), 1),
            "external_citations": self.external_citations,
            "external_pct": round(self.pct(self.external_citations), 1),
        }


# ============================================================
# HEROCON Scoring
# ============================================================

# Default HEROCON weights — graduated penalties for in-group citations.
#
# BARON uses binary 0/1 (in-group = 0, external = 1).
# HEROCON uses these softer weights so in-group citations still count,
# just less than fully external ones.
#
# Weight semantics:
#   0.0 = no credit at all (same as BARON for this category)
#   0.5 = half credit
#   1.0 = full credit (treated as external)
#
# These are DEFAULTS, not empirically calibrated values.
# Users can override via --herocon-weights path/to/weights.json.
# The weights used for any given run are always logged in the audit trail.
HEROCON_WEIGHTS = {
    # ── Phase 1: Self-citation ──
    "SELF": 0.0,                    # Self-citations get zero credit in both scores

    # ── Phase 2: Co-author network ──
    "DIRECT_COAUTHOR": 0.2,         # Shared ≥1 publication → low partial credit
    "TRANSITIVE_COAUTHOR": 0.5,     # Co-author's co-author → moderate partial credit

    # ── Phase 3: Institutional affiliation ──
    "SAME_DEPT": 0.1,               # Same department, no co-authorship → very low credit
    "SAME_INSTITUTION": 0.4,        # Same university, different department → moderate credit
    "SAME_PARENT_ORG": 0.7,         # Same consortium/parent, different institution → high credit

    # ── Phase 4: Venue governance (planned) ──
    "VENUE_SELF_GOVERNANCE": 0.05,   # Researcher on editorial board of citing venue
    "VENUE_EDITOR_COAUTHOR": 0.15,   # Venue editor is co-author
    "VENUE_EDITOR_AFFIL": 0.3,       # Venue editor at same institution
    "VENUE_COMMITTEE": 0.4,          # Committee member in network

    # ── Baseline categories ──
    "NON_SELF": 1.0,                # Phase 1 fallback (everything that isn't self)
    "EXTERNAL": 1.0,                # No detected relationship → full credit
}


def load_herocon_weights(path: str) -> dict:
    """
    Load custom HEROCON weights from a JSON file.

    The file should contain a JSON object mapping classification names
    to float weights (0.0–1.0). Any classification not specified in the
    file will fall back to the default weight from HEROCON_WEIGHTS.

    Example file contents:
        {
            "SELF": 0.0,
            "DIRECT_COAUTHOR": 0.3,
            "TRANSITIVE_COAUTHOR": 0.6,
            "SAME_DEPT": 0.2,
            "SAME_INSTITUTION": 0.5,
            "SAME_PARENT_ORG": 0.8,
            "EXTERNAL": 1.0
        }

    Args:
        path: Filesystem path to the JSON weights file.

    Returns:
        Merged weight dictionary (custom values override defaults).
    """
    import json
    with open(path, "r") as f:
        custom = json.load(f)
    # Merge: custom overrides take precedence, defaults fill gaps
    merged = dict(HEROCON_WEIGHTS)
    merged.update(custom)
    return merged


def compute_herocon_score(
    classifications: list,
    weights: dict = None,
) -> float:
    """
    Compute HEROCON score as a weighted percentage.

    Formula:
        HEROCON = (Σ weight(classification_i) / classifiable_count) × 100

    UNKNOWN citations are excluded from both numerator and denominator,
    ensuring missing data doesn't artificially affect the score.

    The key difference from BARON:
      - BARON: weight is 0 (in-group) or 1 (external) — binary
      - HEROCON: weight is graduated (0.0 to 1.0) — partial credit

    This means HEROCON is always ≥ BARON. The gap between them reveals
    how much of a researcher's measured impact depends on their inner circle.

    Args:
        classifications: List of CitationClassification objects to score.
        weights: Optional custom weight dict. Defaults to HEROCON_WEIGHTS.

    Returns:
        HEROCON score as a percentage (0.0–100.0).
    """
    w = weights or HEROCON_WEIGHTS

    # Filter out UNKNOWN — they lack sufficient data for any classification
    classifiable = [c for c in classifications if c.classification != "UNKNOWN"]
    if not classifiable:
        return 0.0

    total = len(classifiable)
    weighted_sum = sum(
        w.get(cls.classification, 1.0)  # Default to 1.0 (full credit) for unknown categories
        for cls in classifiable
    )
    return (weighted_sum / total) * 100


# ============================================================
# Disclaimer (inline with every output)
# ============================================================

# This disclaimer is embedded in every CLI display, JSON export, and audit file.
# It's non-optional because BARON and HEROCON are structural measurements that
# should never be confused with research quality assessments.
DISCLAIMER = (
    "BARON and HEROCON measure citation network structure, not research quality, "
    "impact, or integrity. They describe where in the social graph citations "
    "originate. They should not be used for hiring, promotion, or funding "
    "decisions. See the audit trail for full classification details."
)

# ============================================================
# Time Formatting Helper
# ============================================================

def format_elapsed(seconds: float) -> str:
    """
    Format elapsed seconds into a human-readable string.

    Used in audit trails, CLI output, and Gradio status messages
    so users never see raw seconds like "270.3s".

    Examples:
        42.3   → "42s"
        127.5  → "2m 8s"
        270.0  → "4m 30s"
        3672.1 → "1h 1m 12s"
    """
    total = int(seconds)
    if total < 60:
        return f"{total}s"
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    return f"{minutes}m {secs}s"


@dataclass
class ScoreResult:
    """
    Complete result of a BARON/HEROCON scoring run.

    Encapsulates everything needed to display, export, and audit:
      - The researcher being analysed
      - The phase version (v0.1, v0.2, v0.3)
      - BARON and HEROCON scores
      - Full breakdown of classification counts
      - Top self-cited works (for self-citation analysis)
      - Co-author network statistics (Phase 2+)
      - Ingestion stats (API calls, timing, coverage)
      - Which HEROCON weights produced the score
    """
    researcher: Researcher
    phase: str = "v0.1"
    baron_score: float = 0.0
    herocon_score: Optional[float] = None     # None in Phase 1, present from Phase 2+
    breakdown: ScoreBreakdown = field(default_factory=ScoreBreakdown)
    top_self_cited_works: list = field(default_factory=list)
    ingestion_stats: dict = field(default_factory=dict)
    # Phase 2+ extras
    coauthor_stats: Optional[dict] = None
    herocon_weights_used: Optional[dict] = None  # Log which weights produced this HEROCON score


# ============================================================
# Co-Author Graph (Phase 2)
# ============================================================

@dataclass
class CoAuthorEdge:
    """
    Weighted co-authorship edge between two authors.

    Each edge tracks the full collaboration history: how many papers
    were shared, when the collaboration started and ended, and which
    specific works connect the two authors.

    The strength property implements recency-weighted collaboration
    intensity using exponential decay:
        strength = shared_papers × exp(-0.1 × years_since_last_collab)

    This gives a half-life of ~7 years. A prolific recent collaborator
    has much higher strength than a one-off co-author from a decade ago.
    The strength score is logged in audit metadata but does not directly
    affect BARON/HEROCON classification (which is binary distance-based).
    """
    author_a_id: str
    author_b_id: str
    shared_papers: int = 0
    first_collab_year: Optional[int] = None
    last_collab_year: Optional[int] = None
    shared_work_ids: list = field(default_factory=list)

    @property
    def strength(self) -> float:
        """
        Co-authorship strength with exponential recency decay.

        Formula: shared_papers × exp(-0.1 × years_since_last_collab)
        Half-life: ~7 years (ln(2)/0.1 ≈ 6.93)

        Returns raw shared_papers count if last_collab_year is unknown.
        """
        import math
        if not self.last_collab_year:
            return float(self.shared_papers)
        years_ago = 2026 - self.last_collab_year
        decay = math.exp(-0.1 * years_ago)
        return self.shared_papers * decay


# ============================================================
# Affiliation Timeline (Phase 3)
# ============================================================

@dataclass
class AffiliationRecord:
    """
    A single affiliation entry for an author at a point in time.

    Built from work-level affiliations in OpenAlex: each work records
    the author's institution at time of publication. Collecting these
    across all works gives a temporal trace of where the author has been.

    This is more reliable than ORCID employment history (which is often
    incomplete) because it's derived from actual publication metadata.
    """
    author_openalex_id: str
    institution_name: str
    institution_ror: Optional[str] = None          # ROR ID (if available)
    institution_openalex_id: Optional[str] = None   # OpenAlex institution ID
    year: Optional[int] = None                      # Year this affiliation was observed
    source_work_id: Optional[str] = None            # Which work provided this affiliation
    department: Optional[str] = None                # Sub-affiliation (rarely available in ROR)


@dataclass
class InstitutionInfo:
    """
    Institution metadata from ROR and/or OpenAlex.

    Used by the InstitutionHierarchy to resolve parent-child relationships
    between institutions. For example, if two institutions share a parent
    ROR ID, a citation between them is classified as SAME_PARENT_ORG.
    """
    ror_id: Optional[str] = None
    openalex_id: Optional[str] = None
    display_name: str = ""
    country: str = ""                               # ISO country code (e.g. "SE", "US")
    type: str = ""                                  # ROR type: education, facility, company, etc.
    parent_ror_id: Optional[str] = None             # Parent institution's ROR ID
    parent_name: Optional[str] = None               # Parent institution's display name
    child_ror_ids: list = field(default_factory=list)  # Child institution ROR IDs


# ============================================================
# Parsing Helpers
# ============================================================

def parse_author(raw: dict) -> Researcher:
    """
    Convert a raw OpenAlex author JSON response into a Researcher dataclass.

    Strips the 'https://openalex.org/' and 'https://orcid.org/' prefixes
    from IDs to keep them clean throughout the pipeline. All internal logic
    uses bare IDs (e.g. 'A5100390903', '0000-0002-1101-3793').
    """
    return Researcher(
        openalex_id=raw.get("id", "").replace("https://openalex.org/", ""),
        orcid=(raw.get("orcid") or "").replace("https://orcid.org/", "") or None,
        display_name=raw.get("display_name", "Unknown"),
        works_count=raw.get("works_count", 0),
        cited_by_count=raw.get("cited_by_count", 0),
    )


def parse_work(raw: dict, is_target: bool = False) -> Work:
    """
    Convert a raw OpenAlex work JSON response into a Work dataclass.

    Extracts author IDs/names from the nested authorships array and
    venue information from primary_location.source. Referenced works
    are extracted as bare IDs for potential future reference analysis.

    Args:
        raw: Raw JSON dict from OpenAlex /works endpoint.
        is_target: True if this is one of the target researcher's own works.
    """
    # Extract parallel author ID and name lists from nested authorships
    author_ids, author_names = [], []
    for a in raw.get("authorships", []):
        aid = (a.get("author", {}).get("id") or "").replace("https://openalex.org/", "")
        aname = a.get("author", {}).get("display_name", "")
        if aid:
            author_ids.append(aid)
            author_names.append(aname)

    # Extract venue (journal/conference) from primary location
    loc = raw.get("primary_location") or {}
    source = loc.get("source") or {}

    return Work(
        openalex_id=raw.get("id", "").replace("https://openalex.org/", ""),
        doi=raw.get("doi"),
        title=raw.get("title", "Untitled"),
        publication_year=raw.get("publication_year"),
        venue_name=source.get("display_name", ""),
        venue_openalex_id=(source.get("id") or "").replace("https://openalex.org/", "") or None,
        work_type=raw.get("type", ""),
        cited_by_count=raw.get("cited_by_count", 0),
        is_target_work=is_target,
        author_ids=author_ids,
        author_names=author_names,
        referenced_work_ids=[
            r.replace("https://openalex.org/", "")
            for r in raw.get("referenced_works", [])
        ],
    )


def parse_work_authors(raw: dict, work_id: str) -> list[WorkAuthor]:
    """
    Extract detailed author-level metadata from a raw OpenAlex work.

    Returns one WorkAuthor per author on the paper, each capturing
    the author's position (first/middle/last) and institutional
    affiliation at the time of publication.

    Uses the first institution in the list if multiple are present
    (OpenAlex sometimes records multiple affiliations per author).

    Args:
        raw: Raw JSON dict from OpenAlex /works endpoint.
        work_id: The bare OpenAlex work ID (without URL prefix).
    """
    authors = []
    for a in raw.get("authorships", []):
        aid = (a.get("author", {}).get("id") or "").replace("https://openalex.org/", "")
        if not aid:
            continue
        # Take the first institution if multiple are listed
        insts = a.get("institutions", [])
        inst = insts[0] if insts else {}
        authors.append(WorkAuthor(
            work_openalex_id=work_id,
            author_openalex_id=aid,
            author_name=a.get("author", {}).get("display_name", ""),
            author_position=a.get("author_position", ""),
            institution_name=inst.get("display_name", ""),
            institution_ror=(inst.get("ror") or "").replace("https://ror.org/", "") or None,
        ))
    return authors
