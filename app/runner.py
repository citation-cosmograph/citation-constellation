"""
citation-constellation/app/runner.py
======================================
Runs the Phase 3 pipeline in a separate thread with its own event loop.

Gradio runs its own asyncio event loop. Calling asyncio.run() inside a
Gradio callback crashes silently or requires multiple clicks. This module
solves that by running the pipeline in a dedicated thread.

Timeouts scale dynamically with the researcher's citation count:
  - Base: 5 minutes (handles small profiles comfortably)
  - +3 minutes per 1000 citations (proportional to API work)
  - Capped by CC_PIPELINE_TIMEOUT_MAX env var (default: 1 hour)
"""

import asyncio
import concurrent.futures
import json
import os
import tempfile
import threading
from typing import Optional

from app.validation import sanitize_filename


# Thread pool for running async pipelines outside Gradio's event loop.
# 4 workers: allows headroom if a previous run's thread is still winding down.
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# ============================================================
# Timeout Configuration
# ============================================================

# Absolute caps — env-var overridable for deployment tuning
VALIDATE_TIMEOUT_MAX = int(os.environ.get("CC_VALIDATE_TIMEOUT_MAX", "600"))   # 10 min
PIPELINE_TIMEOUT_MAX = int(os.environ.get("CC_PIPELINE_TIMEOUT_MAX", "3600"))  # 1 hour


def _compute_pipeline_timeout(estimated_citations: int = 0) -> int:
    """
    Compute a proportional timeout based on expected citation count.

    Formula: base + (citations / 1000) * per_1000_increment
      - Base:      300s (5 min)  — enough for small profiles
      - Per 1000:  180s (3 min)  — scales with API fetching work
      - Min:       300s
      - Max:       PIPELINE_TIMEOUT_MAX (default 3600s = 1 hour)

    Examples:
        500 citations  → ~390s  (~6.5 min)
        2000 citations → ~660s  (~11 min)
        4000 citations → ~1020s (~17 min)
        8000 citations → ~1740s (~29 min)
    """
    base = 300
    per_1000 = 180
    dynamic = base + (estimated_citations / 1000) * per_1000
    return min(max(int(dynamic), base), PIPELINE_TIMEOUT_MAX)


def _compute_validate_timeout(total_works: int = 0) -> int:
    """
    Compute a proportional timeout for the validation-only step.

    Validation fetches all works + runs ORCID matching. Lighter than
    the full pipeline but still scales with profile size.

    Formula: base + (works / 100) * per_100_increment
      - Base:     120s (2 min)
      - Per 100:  30s
      - Min:      120s
      - Max:      VALIDATE_TIMEOUT_MAX (default 600s = 10 min)
    """
    base = 120
    per_100 = 30
    dynamic = base + (total_works / 100) * per_100
    return min(max(int(dynamic), base), VALIDATE_TIMEOUT_MAX)


def estimate_time_human(cited_by_count: int) -> str:
    """
    Return a human-friendly time estimate based on citation count.

    Used in Gradio status messages so the user knows what to expect.
    """
    if cited_by_count < 300:
        return "1–2 minutes"
    elif cited_by_count < 1000:
        return "2–5 minutes"
    elif cited_by_count < 3000:
        return "5–15 minutes"
    elif cited_by_count < 6000:
        return "15–25 minutes"
    else:
        return "25–45 minutes"


def format_elapsed(seconds: float) -> str:
    """
    Format elapsed seconds into a human-readable string.
    Re-exported from models.py for convenience in app/ imports.
    """
    from models import format_elapsed as _fmt
    return _fmt(seconds)


def _run_in_new_loop(coro):
    """Run an async coroutine in a brand-new event loop on this thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================
# Step 1 of 2 (confirm mode): Fetch works + ORCID validation
# ============================================================

def validate_works_sync(
    identifier: str,
    since_year: Optional[int] = None,
) -> dict:
    """
    Fetch works and run ORCID validation only (no classification/scoring).
    Returns validation info for user review before running the full pipeline.

    Returns dict with:
        researcher_name: str
        researcher_orcid: str or None
        total_works: int
        cited_by_count: int  — total incoming citations (for time estimates)
        has_orcid: bool
        orcid_validation: dict or None (from ValidationResult.to_dict())
        flagged_works: list[dict]  — works flagged for potential misattribution
        since_excluded_works: list[dict]  — works excluded by --since filter
        auto_excluded_ids: set[str]  — OA IDs that would be auto-excluded
    """
    from rich.console import Console
    from io import StringIO
    from models import parse_author

    console = Console(file=StringIO(), force_terminal=False)

    async def _validate():
        from client import OpenAlexClient
        from orcid_validate import OrcidValidator

        async with OpenAlexClient() as client:
            raw_author = await client.get_author(identifier)
            researcher = parse_author(raw_author)

            raw_works = await client.get_works_by_author(
                researcher.openalex_id
            )

            validation_dict = None
            flagged_works = []
            since_excluded_works = []
            auto_excluded_ids = set()

            if researcher.orcid:
                validator = OrcidValidator(console)
                result = await validator.validate(
                    researcher.orcid, raw_works, since_year=since_year
                )
                validation_dict = result.to_dict()
                flagged_works = validation_dict.get("flagged_works", [])
                since_excluded_works = validation_dict.get(
                    "since_excluded_works", []
                )
                # Compute which IDs would be auto-excluded
                all_ids = {
                    w.get("id", "").replace("https://openalex.org/", "")
                    for w in raw_works
                }
                used_ids = {
                    w.get("id", "").replace("https://openalex.org/", "")
                    for w in result.works_to_use
                }
                auto_excluded_ids = all_ids - used_ids

            return {
                "researcher_name": researcher.display_name,
                "researcher_orcid": researcher.orcid,
                "total_works": len(raw_works),
                "cited_by_count": researcher.cited_by_count,
                "has_orcid": bool(researcher.orcid),
                "orcid_validation": validation_dict,
                "flagged_works": flagged_works,
                "since_excluded_works": since_excluded_works,
                "auto_excluded_ids": auto_excluded_ids,
            }

    future = _executor.submit(_run_in_new_loop, _validate())
    timeout = _compute_validate_timeout(0)  # conservative: we don't know works count yet
    return future.result(timeout=timeout)


# ============================================================
# Full pipeline run (step 2 of 2 in confirm mode, or single step)
# ============================================================

def run_pipeline_sync(
    identifier: str,
    since_year: Optional[int] = None,
    depth: int = 2,
    herocon_weights: Optional[dict] = None,
    skip_orcid: bool = False,
    exclude_work_ids: Optional[set] = None,
    estimated_citations: int = 0,
) -> dict:
    """
    Run Phase 3 pipeline synchronously (safe to call from Gradio callbacks).

    Args:
        exclude_work_ids: If provided, these OA IDs (no prefix) are excluded
            instead of the ORCID validator's auto-exclusion. Used in confirm
            mode after the user reviews flagged works.
        estimated_citations: Approximate citation count for dynamic timeout
            calculation. Pass researcher.cited_by_count when available.

    Returns dict with:
        audit_data: the full audit document dict
        filepath: path to saved JSON file
        filename: the generated filename
        baron_score: float
        herocon_score: float or None
    """
    from rich.console import Console
    from io import StringIO

    # Quiet console (captures output without printing)
    console = Console(file=StringIO(), force_terminal=False)

    from phase3 import Phase3Pipeline

    pipeline = Phase3Pipeline(
        console=console,
        verbose=False,
        max_depth=depth,
        skip_orcid=skip_orcid,
        show_trajectory=True,
        since_year=since_year,
        herocon_weights=herocon_weights,
        exclude_work_ids=exclude_work_ids,
    )

    # Run async pipeline in a new event loop on a worker thread
    # Timeout scales with citation count
    timeout = _compute_pipeline_timeout(estimated_citations)
    future = _executor.submit(_run_in_new_loop, pipeline.run(identifier))
    score_result, audit = future.result(timeout=timeout)

    # ── Build filename (same format as audit.py) ──
    import re
    from datetime import datetime

    researcher_name = sanitize_filename(score_result.researcher.display_name)
    baron = f"{score_result.baron_score:.1f}"
    herocon = (
        f"{score_result.herocon_score:.1f}"
        if score_result.herocon_score is not None
        else "NA"
    )
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Identifier part
    orcid = score_result.researcher.orcid
    oa_id = score_result.researcher.openalex_id
    if orcid:
        id_part = f"ORCID-ID_{orcid}"
    elif oa_id:
        id_part = f"OpenAlex-ID_{oa_id}"
    else:
        id_part = f"ID_{identifier.replace('-', '').replace('/', '')}"

    filename = (
        f"{researcher_name}_Citation-Constellation-Audit-Report"
        f"_BARON-Score_{baron}"
        f"_HEROCON-Score_{herocon}"
        f"_{id_part}"
        f"_Generated-Time_{ts}"
        f".json"
    )

    # Save to temp directory
    tmpdir = os.environ.get("GRADIO_TEMP_DIR", tempfile.gettempdir())
    os.makedirs(tmpdir, exist_ok=True)
    filepath = os.path.join(tmpdir, filename)
    audit.save_to(filepath)

    return {
        "audit_data": audit.doc,
        "filepath": filepath,
        "filename": filename,
        "baron_score": score_result.baron_score,
        "herocon_score": score_result.herocon_score,
    }
