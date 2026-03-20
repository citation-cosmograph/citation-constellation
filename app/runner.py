"""
citation-constellation/app/runner.py
======================================
Runs the Phase 3 pipeline in a separate thread with its own event loop.

Gradio runs its own asyncio event loop. Calling asyncio.run() inside a
Gradio callback crashes silently or requires multiple clicks. This module
solves that by running the pipeline in a dedicated thread.
"""

import asyncio
import concurrent.futures
import json
import os
import tempfile
import threading
from typing import Optional

from app.validation import sanitize_filename


# Thread pool for running async pipelines outside Gradio's event loop
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


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
                "has_orcid": bool(researcher.orcid),
                "orcid_validation": validation_dict,
                "flagged_works": flagged_works,
                "since_excluded_works": since_excluded_works,
                "auto_excluded_ids": auto_excluded_ids,
            }

    future = _executor.submit(_run_in_new_loop, _validate())
    return future.result(timeout=120)  # 2 min timeout for validation


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
) -> dict:
    """
    Run Phase 3 pipeline synchronously (safe to call from Gradio callbacks).

    Args:
        exclude_work_ids: If provided, these OA IDs (no prefix) are excluded
            instead of the ORCID validator's auto-exclusion. Used in confirm
            mode after the user reviews flagged works.

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
    future = _executor.submit(_run_in_new_loop, pipeline.run(identifier))
    score_result, audit = future.result(timeout=300)  # 5 min timeout

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
        #id_part = f"Orcid-ID_{orcid.replace('-', '')}"
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
