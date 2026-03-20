"""
citation-constellation/orcid_validate.py
==========================================
ORCID Cross-Validation Layer — Smart Two-Mode System

OpenAlex uses algorithmic author disambiguation, which can merge works
from different researchers with similar names. This module cross-references
OpenAlex's work list against the researcher's ORCID record to catch
misattributed works before they enter the scoring pipeline.

Two operating modes (selected automatically):

    High ORCID coverage (≥70%):
        ORCID is used as a hard filter — only works that appear in BOTH
        ORCID and OpenAlex enter the scoring pipeline. This is the safest
        mode but requires the researcher to maintain their ORCID record.

    Low ORCID coverage (<70%):
        All OpenAlex works are kept, but affiliation anomaly detection
        flags works from institutions never associated with the researcher.
        Only flagged works are excluded. This handles researchers who
        haven't fully populated their ORCID record.

The module does NOT do temporal filtering automatically. If the publication
span looks suspicious (>25 years, suggesting name collision), it prints
a warning suggesting the user re-run with --since YEAR. The user is
always in control of what gets excluded.

Usage:
    from orcid_validate import OrcidValidator

    validator = OrcidValidator(console)
    result = await validator.validate(orcid, oa_works_raw, since_year=2010)
    works_for_scoring = result.works_to_use
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from difflib import SequenceMatcher

import httpx
from rich.console import Console

# ============================================================
# Configuration
# ============================================================

ORCID_API_BASE = "https://pub.orcid.org/v3.0"

# Minimum fuzzy title similarity to consider an ORCID–OpenAlex match
TITLE_MATCH_THRESHOLD = 0.85

# Coverage threshold: above this, ORCID is used as a hard filter
HIGH_COVERAGE_THRESHOLD = 0.70

# Publication span (in years) that triggers a name-collision warning
SUSPICIOUS_SPAN_YEARS = 25


# ============================================================
# Data Classes
# ============================================================

@dataclass
class OrcidWork:
    """
    A single work from the ORCID record.

    ORCID works are researcher-claimed: the researcher (or their institution)
    explicitly added this work to their ORCID profile. This makes them a
    trust signal for author identity validation.
    """
    title: str = ""
    doi: Optional[str] = None
    year: Optional[int] = None
    journal: str = ""
    work_type: str = ""
    put_code: Optional[str] = None       # ORCID's internal work identifier
    external_ids: dict = field(default_factory=dict)  # DOI, PMID, etc.


@dataclass
class ValidationResult:
    """
    Complete result of an ORCID cross-validation pass.

    Contains everything needed to understand what was validated, how,
    and what decisions were made — logged verbatim in the audit trail.

    Key fields:
        mode:           "filter" (high ORCID coverage) or "warning" (low coverage)
        verified_works: OpenAlex works confirmed by ORCID matching
        unverified_oa:  OpenAlex works not found in ORCID
        flagged_works:  Works flagged by affiliation anomaly detection
        works_to_use:   The final work list for scoring (after all exclusions)
        span_warning:   Warning message if publication span looks suspicious
    """
    orcid: str
    mode: str = "warning"                # "filter" or "warning"
    since_year: Optional[int] = None     # --since value (if provided)
    orcid_works: list = field(default_factory=list)
    openalex_works_raw: list = field(default_factory=list)
    verified_works: list = field(default_factory=list)
    unverified_oa: list = field(default_factory=list)
    orcid_only: list = field(default_factory=list)    # In ORCID but not OpenAlex
    flagged_works: list = field(default_factory=list)  # Affiliation anomalies
    since_excluded: list = field(default_factory=list)  # Excluded by --since
    works_to_use: list = field(default_factory=list)   # Final list for scoring
    match_log: list = field(default_factory=list)      # Per-work match details
    span_warning: Optional[str] = None

    @property
    def coverage_pct(self) -> float:
        """Percentage of OpenAlex works that matched an ORCID work."""
        if not self.openalex_works_raw:
            return 0.0
        return len(self.verified_works) / len(self.openalex_works_raw) * 100

    @property
    def orcid_completeness(self) -> float:
        """
        Ratio of ORCID works to OpenAlex works.

        Values ≥0.70 trigger "filter" mode (ORCID as hard filter).
        Values <0.70 trigger "warning" mode (anomaly detection only).
        """
        if not self.openalex_works_raw:
            return 0.0
        return len(self.orcid_works) / len(self.openalex_works_raw)

    def to_dict(self) -> dict:
        """Serialise for audit trail and JSON export."""
        return {
            "orcid": self.orcid,
            "mode": self.mode,
            "since_year": self.since_year,
            "orcid_works_count": len(self.orcid_works),
            "openalex_works_count": len(self.openalex_works_raw),
            "verified_count": len(self.verified_works),
            "unverified_count": len(self.unverified_oa),
            "flagged_count": len(self.flagged_works),
            "since_excluded_count": len(self.since_excluded),
            "works_used_for_scoring": len(self.works_to_use),
            "coverage_pct": round(self.coverage_pct, 1),
            "orcid_completeness": round(self.orcid_completeness * 100, 1),
            "span_warning": self.span_warning,
            "flagged_works": [
                {
                    "openalex_id": w["work"].get("id", "").replace("https://openalex.org/", ""),
                    "title": w["work"].get("title", ""),
                    "year": w["work"].get("publication_year"),
                    "reason": w["reason"],
                    "anomaly_type": "affiliation",
                }
                for w in self.flagged_works
            ],
            "since_excluded_works": [
                {
                    "openalex_id": w.get("id", "").replace("https://openalex.org/", ""),
                    "title": w.get("title", ""),
                    "year": w.get("publication_year"),
                }
                for w in self.since_excluded
            ],
            "match_log": self.match_log,
        }


# ============================================================
# ORCID API Client
# ============================================================

class OrcidClient:
    """
    Async client for the ORCID Public API v3.0.

    Fetches the researcher's claimed works list from their ORCID profile.
    Uses the public API (no authentication required) with JSON responses.

    Usage (as async context manager):
        async with OrcidClient() as client:
            works = await client.get_works("0000-0002-1101-3793")
    """

    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            base_url=ORCID_API_BASE,
            headers={"Accept": "application/json"},
            timeout=20.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    async def get_works(self, orcid: str) -> list[OrcidWork]:
        """
        Fetch all works claimed by a researcher on their ORCID profile.

        ORCID groups works by deduplication. Within each group, we take
        the first summary (they're typically identical across sources).
        Extracts: title, DOI, publication year, journal, work type, and
        all external identifiers.

        Args:
            orcid: The researcher's ORCID (e.g. "0000-0002-1101-3793").

        Returns:
            List of OrcidWork dataclass instances.
        """
        resp = await self.client.get(f"/{orcid}/works")
        resp.raise_for_status()
        data = resp.json()

        works = []
        for group in data.get("group", []):
            summaries = group.get("work-summary", [])
            if not summaries:
                continue
            # Take the first summary from each deduplication group
            s = summaries[0]

            # Extract title (nested structure in ORCID API)
            title_obj = s.get("title", {})
            title = title_obj["title"]["value"] if title_obj and title_obj.get("title") else ""

            # Extract publication year
            year = None
            pub_date = s.get("publication-date")
            if pub_date and pub_date.get("year"):
                try:
                    year = int(pub_date["year"]["value"])
                except (ValueError, TypeError):
                    pass

            # Extract external identifiers (DOI, PMID, etc.)
            ext_ids = {}
            doi = None
            for eid in (s.get("external-ids") or {}).get("external-id", []):
                id_type = eid.get("external-id-type", "")
                id_value = eid.get("external-id-value", "")
                ext_ids[id_type] = id_value
                if id_type == "doi":
                    doi = _normalize_doi(id_value)

            # Extract journal title
            journal = ""
            jt = s.get("journal-title")
            if jt:
                journal = jt.get("value", "")

            works.append(OrcidWork(
                title=title, doi=doi, year=year, journal=journal,
                work_type=s.get("type", ""),
                put_code=str(s.get("put-code", "")),
                external_ids=ext_ids,
            ))
        return works


# ============================================================
# Matching & Anomaly Detection
# ============================================================

def _normalize_doi(doi):
    """
    Normalise a DOI string for reliable comparison.

    Strips URL prefixes (https://doi.org/, doi:) and lowercases
    so that different DOI representations match correctly.
    """
    if not doi:
        return ""
    doi = doi.lower().strip()
    doi = re.sub(r'^https?://doi\.org/', '', doi)
    doi = re.sub(r'^doi:', '', doi)
    return doi


def _normalize_title(title):
    """
    Normalise a title string for fuzzy comparison.

    Strips punctuation, collapses whitespace, and lowercases.
    This handles minor formatting differences between ORCID and OpenAlex
    (e.g. different punctuation, extra spaces, case differences).
    """
    if not title:
        return ""
    t = title.lower().strip()
    t = re.sub(r'[^\w\s]', '', t)  # Remove all punctuation
    t = re.sub(r'\s+', ' ', t)     # Collapse whitespace
    return t


def _title_similarity(a, b):
    """
    Compute fuzzy similarity between two title strings (0.0–1.0).

    Uses SequenceMatcher, which handles transpositions and partial
    matches better than simple Levenshtein for title comparison.
    """
    na, nb = _normalize_title(a), _normalize_title(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def match_works(orcid_works, oa_works_raw):
    """
    Match OpenAlex works against ORCID works using DOI and title similarity.

    Matching strategy (applied per OpenAlex work):
      1. DOI exact match: if both have DOIs and they match → VERIFIED
      2. Title fuzzy match: if similarity ≥ TITLE_MATCH_THRESHOLD → VERIFIED
      3. Otherwise → UNVERIFIED

    Args:
        orcid_works: List of OrcidWork objects from the ORCID profile.
        oa_works_raw: List of raw OpenAlex work JSON dicts.

    Returns:
        Tuple of (verified, unverified, orcid_only, match_log):
          - verified: OpenAlex works that matched an ORCID work
          - unverified: OpenAlex works with no ORCID match
          - orcid_only: ORCID works not found in OpenAlex
          - match_log: Per-work matching details for audit
    """
    # Build lookup indices for ORCID works
    orcid_by_doi = {}      # DOI → index in orcid_works
    orcid_by_title = {}    # normalised title → index in orcid_works
    orcid_matched = set()  # Track which ORCID works got matched

    for i, ow in enumerate(orcid_works):
        if ow.doi:
            orcid_by_doi[ow.doi] = i
        if ow.title:
            orcid_by_title[_normalize_title(ow.title)] = i

    verified, unverified, match_log = [], [], []

    for oa_work in oa_works_raw:
        oa_id = oa_work.get("id", "").replace("https://openalex.org/", "")
        oa_title = oa_work.get("title", "")
        oa_doi = _normalize_doi(oa_work.get("doi") or "")
        matched, match_method, matched_idx = False, None, None

        # Strategy 1: DOI exact match (most reliable)
        if oa_doi and oa_doi in orcid_by_doi:
            matched, match_method, matched_idx = True, "doi_exact", orcid_by_doi[oa_doi]

        # Strategy 2: Title fuzzy match (fallback for works without DOI)
        if not matched and oa_title:
            best_sim, best_idx = 0.0, None
            for _, idx in orcid_by_title.items():
                sim = _title_similarity(oa_title, orcid_works[idx].title)
                if sim > best_sim:
                    best_sim, best_idx = sim, idx
            if best_sim >= TITLE_MATCH_THRESHOLD:
                matched, match_method, matched_idx = True, "title_fuzzy", best_idx

        # Record the result
        if matched and matched_idx is not None:
            orcid_matched.add(matched_idx)
            verified.append(oa_work)
            match_log.append({"openalex_id": oa_id, "verdict": "VERIFIED", "method": match_method})
        else:
            unverified.append(oa_work)
            match_log.append({"openalex_id": oa_id, "verdict": "UNVERIFIED", "method": "none"})

    # Identify ORCID works that had no OpenAlex counterpart
    orcid_only = [ow for i, ow in enumerate(orcid_works) if i not in orcid_matched]

    return verified, unverified, orcid_only, match_log


def detect_affiliation_anomalies(oa_works_raw, verified_works):
    """
    Flag unverified works whose affiliations never appear in known works.

    This catches name-collision misattributions: if OpenAlex incorrectly
    assigned a work to our researcher, the author's institution on that
    work probably won't match any institution from the researcher's
    verified works.

    The logic:
      1. Build a set of "known institutions" from verified works
         (or all works if no verified works exist).
      2. For each unverified work, check if ANY of its institutions
         appear in the known set.
      3. If none match → flag as potential misattribution.

    Args:
        oa_works_raw: All OpenAlex works (raw JSON).
        verified_works: Works confirmed by ORCID matching.

    Returns:
        List of flagged work dicts, each with:
          - "work": the raw OpenAlex work JSON
          - "reason": human-readable explanation
          - "unknown_affiliations": list of unrecognised institution names
    """
    # Use verified works as the reference set (or all works if no verifications)
    reference = verified_works if verified_works else oa_works_raw

    # Build set of known institution names (lowercased for comparison)
    known_institutions = set()
    for w in reference:
        for a in w.get("authorships", []):
            for inst in a.get("institutions", []):
                name = inst.get("display_name", "").lower().strip()
                if name:
                    known_institutions.add(name)

    # Flag unverified works with entirely unknown affiliations
    flagged = []
    for w in oa_works_raw:
        if w in verified_works:
            continue  # Skip already-verified works

        work_insts = set()
        for a in w.get("authorships", []):
            for inst in a.get("institutions", []):
                name = inst.get("display_name", "").lower().strip()
                if name:
                    work_insts.add(name)

        # If the work has affiliations but NONE match known institutions → flag it
        if work_insts and not work_insts.intersection(known_institutions):
            flagged.append({
                "work": w,
                "reason": f"Affiliation(s) {', '.join(work_insts)} never appear in known works",
                "unknown_affiliations": list(work_insts),
            })

    return flagged


def check_suspicious_span(oa_works_raw):
    """
    Check if the publication span suggests a name collision.

    If the span between the earliest and latest publication exceeds
    SUSPICIOUS_SPAN_YEARS (default: 25), this likely indicates that
    OpenAlex has merged works from two different researchers with
    similar names.

    Args:
        oa_works_raw: List of raw OpenAlex work JSON dicts.

    Returns:
        Warning message string, or None if the span looks normal.
    """
    years = [w.get("publication_year") for w in oa_works_raw if w.get("publication_year")]
    if len(years) < 2:
        return None
    earliest, latest = min(years), max(years)
    span = latest - earliest
    if span > SUSPICIOUS_SPAN_YEARS:
        return (
            f"Publication span is {span} years ({earliest}–{latest}). "
            f"This may indicate name collision with a different researcher. "
            f"If works before a certain year are not yours, re-run with: --since YEAR"
        )
    return None


# ============================================================
# Validator
# ============================================================

class OrcidValidator:
    """
    Orchestrates the full ORCID cross-validation workflow.

    Steps:
      1. Fetch the researcher's ORCID works list
      2. Apply --since filtering (if provided)
      3. Match OpenAlex works against ORCID (DOI + title)
      4. Determine mode: filter (high coverage) or warning (low coverage)
      5. Run affiliation anomaly detection on unverified works
      6. Check for suspicious publication span
      7. Produce the final works_to_use list

    Usage:
        validator = OrcidValidator(console)
        result = await validator.validate(orcid, oa_works_raw, since_year=2018)
        scored_works = result.works_to_use
    """

    def __init__(self, console: Console):
        self.console = console

    async def validate(self, orcid, oa_works_raw, since_year=None):
        """
        Run the full cross-validation pipeline.

        Args:
            orcid: Researcher's ORCID identifier.
            oa_works_raw: List of raw OpenAlex work JSON dicts.
            since_year: Optional year cutoff (exclude works before this year).

        Returns:
            ValidationResult with the final works_to_use list and full diagnostics.
        """
        # ── Step 1: Fetch ORCID works ──
        self.console.print("\n  [bold]ORCID Validation:[/] Fetching ORCID works list...")
        async with OrcidClient() as client:
            orcid_works = await client.get_works(orcid)

        self.console.print(f"    ORCID record: [bold]{len(orcid_works)}[/] works claimed")
        self.console.print(f"    OpenAlex:     [bold]{len(oa_works_raw)}[/] works assigned")

        # ── Step 2: Apply --since filtering ──
        since_excluded, active_works = [], oa_works_raw
        if since_year:
            since_excluded = [
                w for w in oa_works_raw
                if w.get("publication_year") and w["publication_year"] < since_year
            ]
            active_works = [
                w for w in oa_works_raw
                if not w.get("publication_year") or w["publication_year"] >= since_year
            ]
            if since_excluded:
                self.console.print(
                    f"\n    [bold cyan]--since {since_year}:[/] "
                    f"{len(since_excluded)} work(s) before {since_year} excluded"
                )

        # ── Step 3: Match OpenAlex works against ORCID ──
        verified, unverified, orcid_only, match_log = match_works(orcid_works, active_works)

        # ── Step 4: Determine operating mode ──
        completeness = len(orcid_works) / len(active_works) if active_works else 0
        use_filter = completeness >= HIGH_COVERAGE_THRESHOLD

        # ── Step 5: Affiliation anomaly detection ──
        flagged = detect_affiliation_anomalies(active_works, verified)

        # ── Step 6: Check for suspicious publication span ──
        span_warning = check_suspicious_span(active_works)

        # ── Step 7: Build the final works_to_use list ──
        if use_filter:
            # High coverage: trust ORCID as ground truth, use only verified works
            mode, works_to_use = "filter", verified
        else:
            # Low coverage: keep all works, but exclude affiliation anomalies
            mode = "warning"
            flagged_work_ids = {w["work"].get("id") for w in flagged}
            works_to_use = [w for w in active_works if w.get("id") not in flagged_work_ids]

        result = ValidationResult(
            orcid=orcid, mode=mode, since_year=since_year,
            orcid_works=orcid_works, openalex_works_raw=oa_works_raw,
            verified_works=verified, unverified_oa=unverified,
            orcid_only=orcid_only, flagged_works=flagged,
            since_excluded=since_excluded, works_to_use=works_to_use,
            match_log=match_log, span_warning=span_warning,
        )

        # Display results to the console
        self._display(result)
        return result

    def _display(self, r):
        """Print validation results to the console with Rich formatting."""

        # Show operating mode
        if r.mode == "filter":
            self.console.print(
                f"\n    [bold green]ORCID coverage high "
                f"({r.orcid_completeness*100:.0f}%)[/] — using ORCID as filter"
            )
            if r.unverified_oa:
                self.console.print(
                    f"    [yellow]⚠ {len(r.unverified_oa)} OpenAlex work(s) "
                    f"excluded (not in ORCID)[/]"
                )
        else:
            self.console.print(
                f"\n    [bold yellow]ORCID coverage low "
                f"({r.orcid_completeness*100:.0f}%)[/] — using all OpenAlex "
                f"works with anomaly detection"
            )
            self.console.print(
                f"    [dim]Tip: update your ORCID record for more accurate validation[/]"
            )

        # Show suspicious span warning
        if r.span_warning:
            self.console.print(f"\n    [bold yellow]⚠ {r.span_warning}[/]")

        # Show flagged works (affiliation anomalies)
        if r.flagged_works:
            self.console.print(
                f"\n    [bold red]⚠ {len(r.flagged_works)} work(s) flagged "
                f"as potentially misattributed:[/]"
            )
            for fw in r.flagged_works[:5]:
                w = fw["work"]
                title = w.get("title", "Untitled")
                if len(title) > 55:
                    title = title[:52] + "..."
                self.console.print(
                    f"      [red]✗[/] {title} ({w.get('publication_year', '?')})"
                )
                self.console.print(
                    f"        [dim]Unknown affiliation: "
                    f"{', '.join(fw.get('unknown_affiliations', []))}[/]"
                )
            if len(r.flagged_works) > 5:
                self.console.print(
                    f"      [dim]... and {len(r.flagged_works) - 5} more[/]"
                )
            self.console.print(
                f"    [dim]Flagged works excluded from scoring. Review in audit file.[/]"
            )
        elif r.mode == "warning" and not r.span_warning:
            self.console.print(
                f"\n    [green]✓ No anomalies detected — all works included[/]"
            )

        # Show final count
        self.console.print(
            f"\n    [bold]Using {len(r.works_to_use)}/{len(r.openalex_works_raw)} "
            f"works for scoring[/]\n"
        )
