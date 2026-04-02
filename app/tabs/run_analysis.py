"""
citation-constellation/app/tabs/run_analysis.py
=================================================
Tab 1: Run a new BARON & HEROCON analysis from ORCID or OpenAlex ID.

When "Wait for my validation" is checked:
  Step 1: Fetch works + ORCID validation → show flagged works as checkboxes
  Step 2: User confirms → run full pipeline with user's selections

When unchecked:
  Single step: run full pipeline (auto-exclude flagged works)
"""

import json
import time
import gradio as gr

from app.validation import validate_identifier, validate_since_year, validate_depth
from app.rate_limiter import limiter
from app.runner import run_pipeline_sync, validate_works_sync, estimate_time_human, format_elapsed, get_queue_status, GRADIO_CONCURRENCY
from app.branding import (
    IDENTIFIER_HELP, SINCE_HELP, DEPTH_HELP, CONFIRM_HELP, WEIGHTS_HELP,
    DISCLAIMER_SHORT,
)
from app.components.coauthor_graph import build_coauthor_graph
from app.components.trajectory_chart import build_trajectory_chart
from app.components.score_panel import build_score_donut, format_score_summary
from app.components.classification_table import (
    build_classification_dataframe, build_classification_summary,
    export_classifications_json,
)


# ============================================================
# Helpers
# ============================================================

def _safe_error_msg(e: Exception) -> str:
    """
    Extract a useful error message from an exception.

    concurrent.futures.TimeoutError and some other exceptions have an
    empty str() representation. This helper falls back to the class name
    so users never see a blank "Analysis failed: ." message.
    """
    msg = str(e).strip()
    if msg:
        return msg[:300]
    return type(e).__name__


def _queue_notice() -> str:
    """Return a queue status notice string, or empty if no queue."""
    queue = get_queue_status()
    if queue["message"]:
        return f"\n\n{queue['message']}"
    return ""


def _render_results(audit_data: dict, filepath: str, pipeline_elapsed: float) -> dict:
    """Render all visualizations from audit data. Returns output dict."""
    render_start = time.time()
    try:
        summary_md = format_score_summary(audit_data)
        summary_df = build_classification_summary(audit_data)
        donut = build_score_donut(audit_data)
        graph = build_coauthor_graph(audit_data)
        trajectory = build_trajectory_chart(audit_data)
        cls_df = build_classification_dataframe(audit_data)
    except Exception as e:
        summary_md = "Score computation completed. See JSON for details."
        summary_df = None
        donut = graph = trajectory = cls_df = None

    render_elapsed = time.time() - render_start

    return {
        "status": (
            f"✅ Done — data fetched in **{format_elapsed(pipeline_elapsed)}**, "
            f"visualizations rendered in **{format_elapsed(render_elapsed)}**."
        ),
        "summary_md": summary_md,
        "summary_df": summary_df,
        "filepath": filepath,
        "donut": donut,
        "graph": graph,
        "trajectory": trajectory,
        "cls_df": cls_df,
    }


def build_tab():
    """Build and return the 'Run New Analysis' tab components."""

    with gr.Column():
        gr.Markdown(IDENTIFIER_HELP)

        with gr.Row():
            identifier_input = gr.Textbox(
                label="Researcher Identifier (ORCID or OpenAlex ID)",
                placeholder="e.g., 0000-0000-0000-0000 or A0000000000",
                max_lines=1,
            )

        with gr.Row():
            since_input = gr.Number(
                label="Filter by Career Start (Optional)",
                info=SINCE_HELP,
                placeholder="e.g., 1990",
                value=2000,
                precision=0,
                minimum=1900,
                maximum=2026,
            )
            depth_input = gr.Radio(
                choices=[1, 2, 3],
                value=2,
                label="Co-author Graph Depth (Deafult: 2)",
                info=DEPTH_HELP,
            )

        with gr.Row():
            confirm_checkbox = gr.Checkbox(
                label="Wait for my validation before discarding flagged papers (Optional)",
                value=False,
                info=CONFIRM_HELP,
            )

        with gr.Accordion("Advanced: Provide Custom HEROCON Weights (Optional)", open=False):
            gr.Markdown(WEIGHTS_HELP)
            weights_file = gr.File(
                label="Upload weights JSON",
                file_types=[".json"],
                type="filepath",
            )

        run_btn = gr.Button("🔍 Run Analysis", variant="primary", size="lg")
        rate_display = gr.Markdown(
            value=f"*{limiter.remaining('default')} analysis runs remaining this hour.*"
        )
        gr.Markdown(
            "💡 **Tip for large profiles:** If the researcher has a high citation count "
            "(4,000+) or many publications (200+), the web app may time out — the analysis "
            "time scales with both citation volume *and* co-author network size (more publications "
            "= larger network to traverse). In these cases, running via the **CLI** is more "
            "reliable: it has no timeout limits and gives real-time progress feedback. "
            "Remember to include the `--trajectory` or `-t` flag so the career trajectory "
            "chart is available when you visualize the results.\n\n"
            "You can then upload the generated audit JSON in the **📊 View Existing Audits** "
            "tab for full interactive visualization. See the **💻 How to Run Here & Install "
            "Locally** tab for CLI setup and usage instructions."
        )

        # ── Status ──
        status_output = gr.Markdown(visible=False)

        # ══════════════════════════════════════════════════════════
        # Confirmation section (visible only in confirm mode)
        # ══════════════════════════════════════════════════════════
        confirm_section = gr.Column(visible=False)
        with confirm_section:
            gr.Markdown("### Review flagged works before scoring")
            confirm_info = gr.Markdown()
            flagged_checkbox = gr.CheckboxGroup(
                label="Flagged works (checked = will be EXCLUDED from scoring)",
                choices=[],
                value=[],
                interactive=True,
            )
            since_excluded_info = gr.Markdown(visible=False)
            confirm_btn = gr.Button(
                "✅ Confirm & Run Full Analysis",
                variant="primary",
                size="lg",
            )

        # ── State for confirm mode + audit data for exports ──
        validation_state = gr.State(value=None)
        audit_state = gr.State(value=None)

        # ── Results ──
        results_section = gr.Column(visible=False)
        with results_section:
            gr.Markdown(f"---\n### *{DISCLAIMER_SHORT}*\n---")
            download_btn = gr.File(label="📥 Download Audit Report (JSON). Click the file link with the ↓ icon on the right to save it.")
            score_summary = gr.Markdown()
            gr.Markdown(
                "*ℹ️ The EXTERNAL % in the summary is computed against all citations "
                "(including UNKNOWN). The BARON score excludes UNKNOWN from its denominator, "
                "so BARON will be ≥ the raw EXTERNAL % when UNKNOWN citations are present.*",
                visible=True,
            )
            summary_table = gr.Dataframe(
                label="Classification Summary",
                interactive=False,
                wrap=True,
            )
            with gr.Row():
                donut_chart = gr.Plot(label="Classification Breakdown")
            graph_plot = gr.Plot(label="Co-Author Network")
            trajectory_plot = gr.Plot(label="Career Trajectory")
            with gr.Accordion("All Citation Classifications", open=False):
                full_table = gr.Dataframe(
                    label="Citations",
                    interactive=False,
                    wrap=True,
                )
                export_json_btn = gr.Button(
                    "📥 Export Citations as JSON (see instructions below)", size="sm",
                )
                export_file = gr.File(
                    label="After clicking the button above, your download will appear here. Click the file link with the ↓ icon on the right to save it.",
                    visible=True,
                )

        # ── All outputs for on_run and on_confirm ──
        all_outputs = [
            status_output, results_section, download_btn, score_summary,
            summary_table, donut_chart, graph_plot, trajectory_plot,
            full_table, rate_display,
            # Confirm-mode outputs
            confirm_section, confirm_info, flagged_checkbox,
            since_excluded_info, validation_state,
            # Audit state for exports
            audit_state,
        ]

        def _make_output(
            status_msg="", status_visible=False,
            results_visible=False,
            filepath=None, summary_md="", summary_df=None,
            donut=None, graph=None, trajectory=None, cls_df=None,
            # Confirm section
            confirm_visible=False, confirm_info_md="",
            flagged_choices=None, flagged_values=None,
            since_info_md="", since_info_visible=False,
            state_data=None,
            # Audit data for export
            audit_data=None,
        ):
            """Build a complete output dict."""
            return {
                status_output: gr.update(value=status_msg, visible=status_visible),
                results_section: gr.update(visible=results_visible),
                download_btn: filepath,
                score_summary: summary_md,
                summary_table: summary_df,
                donut_chart: donut,
                graph_plot: graph,
                trajectory_plot: trajectory,
                full_table: cls_df,
                rate_display: f"*{limiter.remaining('default')} analysis runs remaining this hour.*",
                # Confirm section
                confirm_section: gr.update(visible=confirm_visible),
                confirm_info: gr.update(value=confirm_info_md),
                flagged_checkbox: gr.update(
                    choices=flagged_choices or [],
                    value=flagged_values or [],
                ),
                since_excluded_info: gr.update(
                    value=since_info_md, visible=since_info_visible,
                ),
                validation_state: state_data,
                # Audit data
                audit_state: audit_data,
            }

        def _validate_inputs(ident, since, depth, weights):
            """Shared input validation. Returns (ok, error_output_or_params)."""
            # Strip URL prefix if pasted as URL
            ident = ident.replace("https://openalex.org/", "").replace("http://openalex.org/", "")
            # Strip 'authors/' path if present (handles both /authors/A123 and /A123)
            if ident.startswith("authors/"):
                ident = ident[8:]
            # Convert lowercase 'a' to uppercase 'A' for OpenAlex IDs
            if ident.startswith('a'):
                ident = 'A' + ident[1:]
            # Format bare ORCID (16 chars) to hyphenated format
            if len(ident) == 16 and (ident[-1].isdigit() or ident[-1].upper() == 'X'):
                ident = f"{ident[0:4]}-{ident[4:8]}-{ident[8:12]}-{ident[12:16]}"
            ok, result, id_type = validate_identifier(ident or "")
            if not ok:
                return False, _make_output(
                    status_msg=f"⚠️ **Validation Error:** {result}",
                    status_visible=True,
                )

            since_val = None
            if since and str(since).strip():
                try:
                    sv = float(since)
                    if sv > 0:
                        ok2, msg = validate_since_year(since)
                        if not ok2:
                            return False, _make_output(
                                status_msg=f"⚠️ **Validation Error:** {msg}",
                                status_visible=True,
                            )
                        since_val = int(sv)
                except (ValueError, TypeError):
                    pass

            ok3, msg3 = validate_depth(depth)
            if not ok3:
                return False, _make_output(
                    status_msg=f"⚠️ **Validation Error:** {msg3}",
                    status_visible=True,
                )

            allowed, rate_msg = limiter.check("default")
            if not allowed:
                return False, _make_output(
                    status_msg=f"⚠️ {rate_msg}",
                    status_visible=True,
                )

            herocon_weights = None
            if weights is not None:
                try:
                    with open(weights, "r") as f:
                        herocon_weights = json.load(f)
                except Exception as e:
                    return False, _make_output(
                        status_msg=f"⚠️ **Weights Error:** {e}",
                        status_visible=True,
                    )

            return True, {
                "identifier": result,
                "since_val": since_val,
                "depth": int(depth),
                "herocon_weights": herocon_weights,
            }

        def _make_final_output(params_or_state, pipeline_result, pipeline_elapsed,
                               extra_status=""):
            """Shared helper to render final results from a pipeline run."""
            audit_data = pipeline_result["audit_data"]
            rendered = _render_results(
                audit_data, pipeline_result["filepath"], pipeline_elapsed,
            )
            status_msg = rendered["status"]
            if extra_status:
                status_msg += extra_status

            return _make_output(
                status_msg=status_msg,
                status_visible=True,
                results_visible=True,
                filepath=rendered["filepath"],
                summary_md=rendered["summary_md"],
                summary_df=rendered["summary_df"],
                donut=rendered["donut"],
                graph=rendered["graph"],
                trajectory=rendered["trajectory"],
                cls_df=rendered["cls_df"],
                audit_data=audit_data,
            )

        # ══════════════════════════════════════════════════════════
        # on_run: handles both confirm and non-confirm modes
        # ══════════════════════════════════════════════════════════
        def on_run(ident, since, depth, confirm, weights):
            """
            Generator:
              Non-confirm mode: Yield 1 (processing), Yield 2 (results)
              Confirm mode:     Yield 1 (validating), Yield 2 (show flagged OR results)
            """
            ok, result = _validate_inputs(ident, since, depth, weights)
            if not ok:
                yield result
                return

            params = result

            if confirm:
                # ─── CONFIRM MODE: Step 1 — Fetch + Validate only ───
                yield _make_output(
                    status_msg=(
                        "🔄 **Fetching publications and validating against ORCID...**\n\n"
                        "This typically takes **10–30 seconds**. "
                        "You will be able to review flagged works before scoring begins."
                        + _queue_notice()
                    ),
                    status_visible=True,
                )

                try:
                    val_result = validate_works_sync(
                        identifier=params["identifier"],
                        since_year=params["since_val"],
                    )
                except Exception as e:
                    yield _make_output(
                        status_msg=(
                            f"❌ **Validation failed:** {_safe_error_msg(e)}. "
                            "Please check the identifier and try again."
                        ),
                        status_visible=True,
                    )
                    return

                flagged = val_result.get("flagged_works", [])
                since_excluded = val_result.get("since_excluded_works", [])
                cited_by_count = val_result.get("cited_by_count", 0)
                time_estimate = estimate_time_human(cited_by_count)

                if not flagged and not since_excluded:
                    # ── Nothing to review — run full pipeline directly ──
                    yield _make_output(
                        status_msg=(
                            "✅ **No flagged works** — all works passed ORCID validation.\n\n"
                            "🔄 **Now running full analysis...**\n\n"
                            f"Fetching citations and classifying "
                            f"(~{cited_by_count:,} citations). "
                            f"Estimated time: **{time_estimate}**. "
                            "Please wait — do not close this tab."
                            + _queue_notice()
                        ),
                        status_visible=True,
                    )

                    start = time.time()
                    try:
                        pipeline_result = run_pipeline_sync(
                            identifier=params["identifier"],
                            since_year=params["since_val"],
                            depth=params["depth"],
                            herocon_weights=params["herocon_weights"],
                            estimated_citations=cited_by_count,
                        )
                    except Exception as e:
                        yield _make_output(
                            status_msg=(
                                f"❌ **Analysis failed:** {_safe_error_msg(e)}. "
                                "For researchers with 4,000+ citations or 200+ publications, "
                                "consider using the **CLI** instead (see the "
                                "**💻 How to Run Here & Install Locally** tab). "
                                "The CLI has no timeout limits."
                            ),
                            status_visible=True,
                        )
                        return

                    pipeline_elapsed = time.time() - start
                    limiter.record("default")
                    yield _make_final_output(
                        params, pipeline_result, pipeline_elapsed,
                        extra_status="\n\n✅ No flagged works — all works passed validation.",
                    )
                    return

                # ── Build confirmation UI ──
                checkbox_choices = []
                checkbox_values = []
                for fw in flagged:
                    oa_id = fw.get("openalex_id", "")
                    title = fw.get("title", "Untitled")
                    year = fw.get("year", "?")
                    reason = fw.get("reason", "")
                    label = f"{title} ({year}) — {reason}"
                    checkbox_choices.append((label, oa_id))
                    checkbox_values.append(oa_id)

                since_info = ""
                if since_excluded:
                    parts = [f"**{len(since_excluded)} work(s) excluded by --since filter** (always excluded):\n"]
                    for i, ew in enumerate(since_excluded[:10], 1):
                        parts.append(f"{i}. *{ew.get('title', 'Untitled')}* ({ew.get('year', '?')})")
                    if len(since_excluded) > 10:
                        parts.append(f"*... and {len(since_excluded) - 10} more*")
                    since_info = "\n".join(parts)

                confirm_md = (
                    f"Found **{val_result['total_works']}** works for "
                    f"**{val_result['researcher_name']}** "
                    f"(~{cited_by_count:,} total citations).\n\n"
                    f"**{len(flagged)} work(s) flagged** as potential misattributions. "
                    f"Uncheck any works you want to **keep** in the analysis. "
                    f"Checked works will be excluded from scoring.\n\n"
                    f"When ready, click **Confirm & Run Full Analysis** below. "
                    f"The full analysis will take approximately **{time_estimate}**."
                )

                state = {
                    "identifier": params["identifier"],
                    "since_val": params["since_val"],
                    "depth": params["depth"],
                    "herocon_weights": params["herocon_weights"],
                    "cited_by_count": cited_by_count,
                    "since_excluded_ids": {
                        ew.get("openalex_id", "") for ew in since_excluded
                    },
                }

                yield _make_output(
                    status_msg=(
                        f"🔍 **Validation complete** for **{val_result['researcher_name']}** "
                        f"({val_result['total_works']} works, ~{cited_by_count:,} citations).\n\n"
                        "Review the flagged works below, then confirm to run the full analysis."
                    ),
                    status_visible=True,
                    confirm_visible=True,
                    confirm_info_md=confirm_md,
                    flagged_choices=checkbox_choices,
                    flagged_values=checkbox_values,
                    since_info_md=since_info,
                    since_info_visible=bool(since_excluded),
                    state_data=state,
                )
                return

            else:
                # ─── NON-CONFIRM MODE: Single pipeline run ───
                yield _make_output(
                    status_msg=(
                        "🔄 **Analysis in progress...**\n\n"
                        "Fetching publications and citations from OpenAlex. "
                        "Duration depends on the number of publications and citations — "
                        "small profiles finish in **1–3 minutes**, while large profiles "
                        "(2000+ citations) may take **10–30 minutes**. "
                        "Please wait — do not close this tab."
                        + _queue_notice()
                    ),
                    status_visible=True,
                )

                start = time.time()
                try:
                    pipeline_result = run_pipeline_sync(
                        identifier=params["identifier"],
                        since_year=params["since_val"],
                        depth=params["depth"],
                        herocon_weights=params["herocon_weights"],
                    )
                except Exception as e:
                    yield _make_output(
                        status_msg=(
                            f"❌ **Analysis failed:** {_safe_error_msg(e)}. "
                            "This may be due to a network issue with OpenAlex, "
                            "an invalid identifier, or a timeout for very large profiles. "
                            "For researchers with 4,000+ citations or 200+ publications, "
                            "consider using the **CLI** instead (see the "
                            "**💻 How to Run Here & Install Locally** tab). "
                            "The CLI has no timeout limits."
                        ),
                        status_visible=True,
                    )
                    return

                pipeline_elapsed = time.time() - start
                limiter.record("default")
                yield _make_final_output(params, pipeline_result, pipeline_elapsed)

        # ══════════════════════════════════════════════════════════
        # on_confirm: Step 2 of confirm mode
        # ══════════════════════════════════════════════════════════
        def on_confirm(excluded_ids, state):
            """
            Generator: runs the full pipeline with user's explicit exclusion list.
            """
            if not state:
                yield _make_output(
                    status_msg="⚠️ **Error:** No validation data found. Please run the analysis again.",
                    status_visible=True,
                )
                return

            exclude_set = set(excluded_ids or [])
            cited_by_count = state.get("cited_by_count", 0)
            time_estimate = estimate_time_human(cited_by_count)

            yield _make_output(
                status_msg=(
                    f"🔄 **Running full analysis** with your selections "
                    f"(excluding {len(exclude_set)} flagged work(s))...\n\n"
                    f"Fetching citations and classifying "
                    f"(~{cited_by_count:,} citations). "
                    f"Estimated time: **{time_estimate}**. "
                    "Please wait — do not close this tab."
                    + _queue_notice()
                ),
                status_visible=True,
                confirm_visible=False,
            )

            start = time.time()
            try:
                pipeline_result = run_pipeline_sync(
                    identifier=state["identifier"],
                    since_year=state["since_val"],
                    depth=state["depth"],
                    herocon_weights=state["herocon_weights"],
                    exclude_work_ids=exclude_set if exclude_set else None,
                    estimated_citations=cited_by_count,
                )
            except Exception as e:
                yield _make_output(
                    status_msg=(
                        f"❌ **Analysis failed:** {_safe_error_msg(e)}. "
                        "For researchers with 4,000+ citations or 200+ publications, "
                        "consider using the **CLI** instead (see the "
                        "**💻 How to Run Here & Install Locally** tab). "
                        "The CLI has no timeout limits."
                    ),
                    status_visible=True,
                )
                return

            pipeline_elapsed = time.time() - start
            limiter.record("default")

            extra = ""
            if exclude_set:
                extra = f"\n\n📋 **{len(exclude_set)} flagged work(s) excluded** per your review."

            yield _make_final_output(
                state, pipeline_result, pipeline_elapsed,
                extra_status=extra,
            )

        # ══════════════════════════════════════════════════════════
        # Export handlers
        # ══════════════════════════════════════════════════════════
        def on_export_json(audit_data):
            if not audit_data:
                return gr.update(value=None)
            try:
                path = export_classifications_json(audit_data)
                if path:
                    return gr.update(value=path)
            except Exception:
                pass
            return gr.update(value=None)

        # ── Wire up buttons ──
        # concurrency_limit = MAX_WORKERS × 5, imported as GRADIO_CONCURRENCY.
        # Must be higher than the thread pool so ALL users immediately enter
        # on_run, see the queue status message, then wait on the thread pool.
        # The handlers themselves are lightweight generators (~10 KB each).
        #
        #   8 workers → 40 | 4 workers → 20 | 2 workers → 10 | 1 worker → 5
        run_btn.click(
            fn=on_run,
            inputs=[
                identifier_input, since_input, depth_input,
                confirm_checkbox, weights_file,
            ],
            outputs=all_outputs,
            concurrency_limit=GRADIO_CONCURRENCY,
        )

        confirm_btn.click(
            fn=on_confirm,
            inputs=[flagged_checkbox, validation_state],
            outputs=all_outputs,
            concurrency_limit=GRADIO_CONCURRENCY,
        )

        export_json_btn.click(
            fn=on_export_json,
            inputs=[audit_state],
            outputs=[export_file],
        )
