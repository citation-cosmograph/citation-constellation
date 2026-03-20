"""
citation-constellation/phase1.py
=================================
Phase 1: Self-Citation Baseline

The simplest and fastest phase. Ingests a researcher's publications
via OpenAlex, fetches all incoming citations, and classifies each
citation as either SELF (the researcher is an author on the citing
paper) or NON_SELF (they aren't). Computes BARON v0.1.

This is the foundation that Phase 2 and Phase 3 build upon. The
BARON v0.1 score represents the upper bound — it only gets lower
as more types of in-group citations are detected in later phases.

Pipeline steps:
    1. Resolve author from ORCID or OpenAlex ID
    2. Fetch all works attributed to the author
    3. Cross-validate against ORCID (if available)
    4. Fetch all incoming citations for cited works
    5. Classify each citation as SELF or NON_SELF
    6. Compute BARON v0.1 score
    7. Generate audit trail

Usage:
    python phase1.py --orcid 0000-0000-0000-0000
    python phase1.py --openalex-id A0000000000
    python phase1.py --orcid 0000-0000-0000-0000 --export results.json

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
    ScoreBreakdown, ScoreResult, DISCLAIMER,
    parse_author, parse_work, parse_work_authors,
)
from client import OpenAlexClient
from audit import AuditLog
from orcid_validate import OrcidValidator
from phase2 import compute_trajectory


# ============================================================
# Phase 1 Classifier
# ============================================================

class SelfCitationClassifier:
    """
    Classifies citations as SELF or NON_SELF based on author ID matching.

    The simplest possible classifier: checks whether the target researcher's
    OpenAlex ID appears in the citing work's author list. If yes → SELF.
    If no → NON_SELF (which Phase 1 treats as "external").

    This is Phase 1 only. Phase 2 refines NON_SELF into DIRECT_COAUTHOR,
    TRANSITIVE_COAUTHOR, and EXTERNAL. Phase 3 adds institutional categories.
    """

    def __init__(self, target_researcher_id: str):
        """
        Args:
            target_researcher_id: Bare OpenAlex ID of the researcher being analysed.
        """
        self.target_id = target_researcher_id

    def classify(self, citing_work: Work, cited_work: Work) -> CitationClassification:
        """
        Classify a single citation as SELF or NON_SELF.

        Args:
            citing_work: The paper that contains the citation.
            cited_work: The target researcher's paper being cited.

        Returns:
            CitationClassification with classification="SELF" or "NON_SELF".
        """
        is_self = self.target_id in citing_work.author_ids
        return CitationClassification(
            citing_work_id=citing_work.openalex_id,
            cited_work_id=cited_work.openalex_id,
            classification="SELF" if is_self else "NON_SELF",
            confidence=1.0,
            phase_detected=1,
            metadata={"matching_author_ids": [self.target_id] if is_self else []},
        )


# ============================================================
# Phase 1 Pipeline
# ============================================================

class Phase1Pipeline:
    """
    End-to-end Phase 1 pipeline: ingest → classify → score → audit.

    Orchestrates the full workflow from resolving the researcher to
    producing the final BARON v0.1 score and audit trail. All data
    is fetched from OpenAlex (and optionally ORCID for validation).
    """

    def __init__(self, console: Console, verbose: bool = False,
                 skip_orcid: bool = False, show_trajectory: bool = False,
                 since_year: Optional[int] = None):
        """
        Args:
            console: Rich console for formatted output.
            verbose: Enable verbose logging (currently unused, reserved).
            skip_orcid: If True, skip ORCID cross-validation entirely.
            show_trajectory: If True, compute cumulative career trajectory.
            since_year: Only include works from this year onward.
        """
        self.console = console
        self.verbose = verbose
        self.skip_orcid = skip_orcid
        self.show_trajectory = show_trajectory
        self.since_year = since_year

        # Pipeline state — populated during run()
        self.researcher: Optional[Researcher] = None
        self.target_works: dict[str, Work] = {}
        self.citing_works: dict[str, Work] = {}
        self.work_authors = []
        self.citations: list[Citation] = []
        self.classifications: list[CitationClassification] = []
        self.orcid_result = None
        self.trajectory = []

    async def run(self, identifier: str) -> tuple[ScoreResult, AuditLog]:
        """
        Execute the full Phase 1 pipeline.

        Args:
            identifier: ORCID (e.g. "0000-0002-1101-3793") or OpenAlex ID.

        Returns:
            Tuple of (ScoreResult, AuditLog) — the score and its audit trail.
        """
        start = time.time()
        self.audit = AuditLog(identifier, phase=1)

        async with OpenAlexClient() as client:

            # ── Step 1: Resolve author ──
            self.console.print("\n[bold cyan]Step 1/7:[/] Resolving author...")
            raw_author = await client.get_author(identifier)
            self.researcher = parse_author(raw_author)
            self.audit.log_researcher(self.researcher)
            self.console.print(
                f"  Found: [bold]{self.researcher.display_name}[/] "
                f"({self.researcher.works_count} works, "
                f"{self.researcher.cited_by_count} citations)"
            )

            # ── Step 2: Fetch all works ──
            self.console.print("\n[bold cyan]Step 2/7:[/] Fetching works...")
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
                self.console.print("\n[bold cyan]Step 3/7:[/] ORCID cross-validation...")
                validator = OrcidValidator(self.console)
                self.orcid_result = await validator.validate(
                    self.researcher.orcid, raw_works, since_year=self.since_year
                )
                raw_works = self.orcid_result.works_to_use
            elif self.since_year:
                # No ORCID check, but --since was provided: apply year filter directly
                self.console.print(f"\n[bold cyan]Step 3/7:[/] Filtering works since {self.since_year}...")
                before = len(raw_works)
                raw_works = [
                    w for w in raw_works
                    if not w.get("publication_year") or w["publication_year"] >= self.since_year
                ]
                self.console.print(f"  {before - len(raw_works)} work(s) before {self.since_year} excluded")
            elif not self.researcher.orcid:
                self.console.print("\n[bold cyan]Step 3/7:[/] ORCID validation skipped (no ORCID on profile)")
            else:
                self.console.print("\n[bold cyan]Step 3/7:[/] ORCID validation skipped (--no-orcid-check)")

            # Parse raw works into typed Work objects
            for rw in raw_works:
                wid = rw.get("id", "").replace("https://openalex.org/", "")
                work = parse_work(rw, is_target=True)
                self.target_works[wid] = work
                self.work_authors.extend(parse_work_authors(rw, wid))

            self.console.print(
                f"\n[bold cyan]Step 4/7:[/] {len(self.target_works)} verified works, "
                f"{len(self.work_authors)} author records"
            )

            # ── Step 5: Fetch incoming citations ──
            # Only fetch citations for works that actually have citations
            cited_works = {
                wid: w for wid, w in self.target_works.items()
                if w.cited_by_count > 0
            }
            total_expected = sum(w.cited_by_count for w in cited_works.values())
            self.console.print(
                f"\n[bold cyan]Step 5/7:[/] Fetching incoming citations for "
                f"{len(cited_works)} works (~{total_expected} citations)..."
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

            # Build citation links from the raw citing data
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
                f"  Fetched {len(self.citing_works)} unique citing works, "
                f"{len(self.citations)} citation links"
            )

            # ── Step 6: Classify each citation ──
            self.console.print("\n[bold cyan]Step 6/7:[/] Classifying citations...")
            classifier = SelfCitationClassifier(self.researcher.openalex_id)
            for cit in self.citations:
                citing_w = self.citing_works.get(cit.citing_work_id)
                cited_w = self.target_works.get(cit.cited_work_id)
                if citing_w and cited_w:
                    cls = classifier.classify(citing_w, cited_w)
                    self.classifications.append(cls)

            # ── Step 7: Compute score ──
            self.console.print("[bold cyan]Step 7/7:[/] Computing BARON v0.1...")
            score = self._compute_score(time.time() - start, client.api_calls)

            # Optional: compute career trajectory
            if self.show_trajectory:
                self.trajectory = compute_trajectory(
                    self.classifications, self.target_works, self.citing_works
                )

            # ── Log everything to the audit trail ──
            self.audit.log_works(self.target_works, label="target")
            self.audit.log_works(self.citing_works, label="citing")
            self.audit.log_citations(self.citations)
            self.audit.log_classifications(
                self.classifications, self.target_works, self.citing_works
            )
            self.audit.log_score(score)
            self.audit.log_ingestion(score.ingestion_stats)
            if self.orcid_result:
                self.audit.doc["orcid_validation"] = self.orcid_result.to_dict()
            if self.trajectory:
                self.audit.doc["trajectory"] = self.trajectory

            self.console.print("Done.\n")
            return score, self.audit

    def _compute_score(self, elapsed: float, api_calls: int) -> ScoreResult:
        """
        Compute the BARON v0.1 score from classified citations.

        In Phase 1, the score is simple:
            BARON = (non-self citations / total citations) × 100

        Everything that isn't SELF is treated as "external" because
        Phase 1 doesn't analyse co-author relationships or affiliations.
        """
        total = len(self.classifications)
        self_cites = sum(1 for c in self.classifications if c.classification == "SELF")
        non_self = total - self_cites

        breakdown = ScoreBreakdown(
            total_citations=total,
            self_citations=self_cites,
            external_citations=non_self,  # Phase 1: everything non-self is "external"
        )

        # Identify the most self-cited papers (useful for self-reflection)
        self_cite_counts = defaultdict(int)
        for cls in self.classifications:
            if cls.classification == "SELF":
                self_cite_counts[cls.cited_work_id] += 1
        top_self = sorted(self_cite_counts.items(), key=lambda x: -x[1])[:10]
        top_self_works = []
        for wid, count in top_self:
            w = self.target_works.get(wid)
            if w:
                top_self_works.append({
                    "title": w.title, "year": w.publication_year,
                    "self_citations": count, "total_citations": w.cited_by_count,
                })

        # Reference coverage: fraction of target works that include reference lists
        works_with_refs = sum(
            1 for w in self.target_works.values() if w.referenced_work_ids
        )
        ref_coverage = (
            works_with_refs / len(self.target_works) * 100
            if self.target_works else 0
        )

        return ScoreResult(
            researcher=self.researcher,
            phase="v0.1",
            baron_score=breakdown.pct(breakdown.external_citations),
            breakdown=breakdown,
            top_self_cited_works=top_self_works,
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

def display_score(console: Console, score: ScoreResult, trajectory=None):
    """
    Render the Phase 1 score to the terminal using Rich formatting.

    Shows: researcher info, ingestion stats, BARON score with breakdown,
    top self-cited papers, optional career trajectory, and the disclaimer.
    """
    b = score.breakdown

    # ── Header panel ──
    console.print(Panel(
        f"[bold]{score.researcher.display_name}[/]\n"
        f"ORCID: {score.researcher.orcid or 'N/A'}  |  "
        f"OpenAlex: {score.researcher.openalex_id}  |  "
        f"Works: {score.researcher.works_count}",
        title="[bold cyan]BARON v0.1 — Self-Citation Baseline[/]",
        border_style="cyan",
    ))

    # ── Ingestion statistics ──
    stats = score.ingestion_stats
    st = Table(show_header=False, box=None, padding=(0, 2))
    st.add_column(style="dim")
    st.add_column(style="bold")
    for k, v in stats.items():
        st.add_row(k.replace("_", " ").title(), str(v))
    console.print(Panel(st, title="Ingestion", border_style="blue"))

    # ── Score breakdown ──
    sc = Table(show_header=False, box=None, padding=(0, 2))
    sc.add_column(style="dim", width=28)
    sc.add_column(justify="right")
    sc.add_row("[bold]BARON v0.1[/]", f"[bold yellow]{score.baron_score:.1f}%[/]")
    sc.add_row("", "")
    sc.add_row(
        "  External citations",
        f"[green]{b.external_citations}[/] ({b.pct(b.external_citations):.1f}%)",
    )
    sc.add_row(
        "  Self-citations",
        f"[red]{b.self_citations}[/] ({b.pct(b.self_citations):.1f}%)",
    )
    sc.add_row("  Total citations", f"{b.total_citations}")
    console.print(Panel(sc, title="[bold yellow]Score[/]", border_style="yellow"))

    # ── Top self-cited papers ──
    if score.top_self_cited_works:
        tt = Table(box=None, padding=(0, 1))
        tt.add_column("Paper", style="white", max_width=55)
        tt.add_column("Year", style="dim", justify="center")
        tt.add_column("Self-cites", style="bold red", justify="right")
        tt.add_column("Total cites", style="dim", justify="right")
        for w in score.top_self_cited_works:
            title = w["title"]
            if len(title) > 55:
                title = title[:52] + "..."
            tt.add_row(
                title, str(w["year"] or "?"),
                str(w["self_citations"]), str(w["total_citations"]),
            )
        console.print(Panel(tt, title="Top Self-Cited Papers", border_style="red"))

    # ── Career trajectory (optional) ──
    if trajectory:
        tr = Table(box=None, padding=(0, 2))
        tr.add_column("Year", style="dim", justify="center")
        tr.add_column("Citations", justify="right")
        tr.add_column("BARON", justify="right")
        for row in trajectory:
            m = f"[yellow]{row['baron']}%[/]" if row.get("baron") is not None else "[dim]—[/]"
            tr.add_row(str(row["year"]), str(row["total_citations"]), m)
        console.print(Panel(tr, title="[bold]Career Trajectory[/] (cumulative)", border_style="blue"))

    # ── Disclaimer and next-phase hint ──
    console.print(
        f"\n[dim italic]{DISCLAIMER}[/]\n"
        "[dim]Run phase2.py for co-author network detection, "
        "phase3.py for affiliation matching.[/]\n"
    )


# ============================================================
# CLI
# ============================================================

app = typer.Typer(
    name="baron-herocon-p1",
    help="BARON & HEROCON Phase 1: Self-Citation Baseline",
)


@app.command()
def score(
    orcid: Optional[str] = typer.Option(None, "--orcid", help="Researcher ORCID"),
    openalex_id: Optional[str] = typer.Option(None, "--openalex-id", help="OpenAlex author ID"),
    since: Optional[int] = typer.Option(None, "--since", help="Only include works from this year onward"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    trajectory: bool = typer.Option(False, "--trajectory", "-t", help="Show cumulative career trajectory"),
    export: Optional[str] = typer.Option(None, "--export", help="Export summary to JSON"),
    no_audit: bool = typer.Option(False, "--no-audit", help="Skip audit file generation"),
    no_orcid_check: bool = typer.Option(False, "--no-orcid-check", help="Skip ORCID cross-validation"),
):
    """Compute BARON v0.1 (self-citation baseline) for a researcher."""
    console = Console()

    if not orcid and not openalex_id:
        console.print("[bold red]Error:[/] Provide --orcid or --openalex-id")
        raise typer.Exit(1)

    identifier = orcid or openalex_id

    console.print(f"\n[bold]BARON v0.1[/] — Self-Citation Baseline")
    console.print(f"Target: [cyan]{identifier}[/]\n")

    # Run the pipeline
    pipeline = Phase1Pipeline(
        console, verbose=verbose,
        skip_orcid=no_orcid_check, show_trajectory=trajectory,
        since_year=since,
    )
    result, audit = asyncio.run(pipeline.run(identifier))

    # Display results
    display_score(console, result, trajectory=pipeline.trajectory if trajectory else None)

    # Save audit trail (on by default)
    if not no_audit:
        audit_file = audit.save()
        console.print(f"[dim]Audit trail saved to:[/] [bold green]{audit_file}[/]")
        console.print(
            f"[dim]  → {len(audit.doc['classifications'])} citation classifications logged[/]"
        )
        console.print(
            f"[dim]  → Every decision is documented for full transparency[/]\n"
        )

    # Optional JSON export
    if export:
        export_data = {
            "version": "v0.1",
            "phase": 1,
            "created_at": datetime.now().isoformat(),
            "researcher": asdict(result.researcher),
            "score": {
                "baron_v01": round(result.baron_score, 1),
                "breakdown": result.breakdown.to_dict(),
            },
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
