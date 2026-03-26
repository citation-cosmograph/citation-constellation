# Citation-Constellation — Web Interface

<div style="flex: 0 0 auto; padding: 0 30px; display: flex; align-items: center; justify-content: center;">
      <img src="app/assets/logo.png" alt="Citation Constellation Logo" style="max-width: 100%; height: auto; border-radius: 12px; filter: drop-shadow(0 20px 40px rgba(0,0,0,0.5)); display: block;">
    </div>


**No-Code UI for BARON & HEROCON Citation Network Analysis**

A Gradio-based web interface for computing and visualizing BARON and HEROCON scores. Deployed on [SciLifeLab Serve](https://serve.scilifelab.se) — no installation, registration, or payment required.

**Live:** [citation-constellation.serve.scilifelab.se](https://citation-constellation.serve.scilifelab.se)

```
pulsar 🌟 → astrolabe 🔭 → constellation ✨
the signal    the instrument    the map — you are here
```

---

## Ethical Notice

These scores measure **citation network structure** — where in the social graph citations originate — **not research quality, impact, or integrity**.

In-group citation is normal and often appropriate. A low BARON score may indicate a productive collaborative lab, a small-field researcher, or a disciplinary norm — not a flaw in research practice.

**These scores should NOT be used for hiring, promotion, or funding decisions.**

Every classification decision is documented in the downloadable audit trail.

---

## How to Use

The interface has six tabs: **Run Analysis**, **View Existing Audits**, **How to Run Here & Install Locally**, **How BARON & HEROCON Work**, **Future Features**, and **Full Research Paper**.

### Tab 1: Run Analysis

Enter a researcher identifier and get interactive BARON & HEROCON results.

#### Input Fields

| Field | What to enter | Required? |
|-------|--------------|-----------|
| **Researcher Identifier** | ORCID (e.g., `0000-0002-1101-3793`) or OpenAlex ID (e.g., `A5100390903`). Full URLs accepted — the tool extracts the ID automatically. | Yes |
| **Since Year** | Exclude publications before this year. Useful for name collision in OpenAlex. Leave blank to include all works. | No |
| **Co-author Graph Depth** | Hops of co-authorship counted as in-group. **1:** direct only. **2** (default): co-authors of co-authors. **3:** three hops. | Default: 2 |
| **Wait for my validation** | Pause after ORCID validation to review flagged papers before scoring. When unchecked, flagged papers are automatically excluded. | Default: off |
| **Custom HEROCON Weights** | Upload a JSON file to override default graduated weights. Unspecified classifications use defaults. | No |

#### What Happens on "Run Analysis"

1. Resolves the researcher profile via OpenAlex
2. Fetches all publications (with ORCID cross-validation)
3. For each publication, fetches all incoming citations
4. Classifies every citation through three detection layers:
   - **Phase 1:** Self-citations (author ID match)
   - **Phase 2:** Co-author network (BFS graph distance)
   - **Phase 3:** Institutional affiliation (temporal ROR matching)
5. Computes BARON (strict binary) and HEROCON (graduated weighted) scores
6. Generates interactive visualizations and a downloadable audit report

**Rate limit:** 10 analyses per hour per session.

#### Results

- **Score Summary** — BARON, HEROCON, gap, total citations, classifiable citations, reliability rating
- **Classification Donut Chart** — Proportional breakdown with scores in center
- **Classification Summary Table** — Each category with count, percentage, and HEROCON weight
- **Co-Author Network Graph** — Interactive force-directed network:
  - 🟡 Gold node (large): target researcher
  - 🔴 Crimson nodes: direct co-authors (sized by shared papers)
  - 🔵 Blue nodes: transitive co-authors
  - Edges: thickness reflects co-authorship strength (papers × recency decay)
  - Hover any node for details. Networks above 150 nodes are auto-pruned.
- **Career Trajectory Chart** — Dual-line BARON (yellow) and HEROCON (green) over time, shaded gap area, cumulative citation bars
- **Full Classification Table** — Every citation with classification, confidence, phase, and human-readable rationale. Collapsible accordion.
- **Download Audit Report** — Complete JSON audit file

**Audit filename format:**
```
Mahbub_Ul_Alam_Citation_Constellation_Scores_BARON_84.9_HEROCON_85.9_Orcid_0000000211013793_timestamp_20260315_215252_audit_report.json
```

---

### Tab 2: View Existing Audits

Upload previously generated audit JSON files for visualization and comparison. No computation — pure visualization.

**Single file** → Full visualization suite (same as Tab 1 results).

**Multiple files** → Comparison view:
- Comparison table (side-by-side scores, gap, reliability, self-cite %, external %)
- Overlaid BARON trajectory chart
- Overlaid HEROCON trajectory chart
- Expandable individual reports for each researcher

Up to 115 simultaneous comparisons supported. Files are validated against the expected schema; invalid files are rejected with clear messages.

**Note:** The trajectory chart requires the `--trajectory` flag during CLI generation. All other visualizations work regardless.

---

---

## Demo

### Ethical Notice

Every analysis output begins with a prominent ethical disclaimer, reinforcing that BARON and HEROCON measure citation network structure, not research quality, impact, or integrity.

![Ethical notice displayed at the top of every analysis output.](assets/ethical-note.png)

### Score Panel

The score panel presents BARON and HEROCON scores alongside key summary statistics: total citations, classifiable citations, the BARON–HEROCON gap, and a data quality reliability rating.

![Score panel — Web Interface](assets/score-panel-tool.png)

![Score panel — Command Line Interface](assets/score-panel-tool-cli.png)

### Classification Breakdown

The donut chart provides a proportional breakdown of citation origins across all classification categories, with BARON and HEROCON scores displayed in the center.

![Classification breakdown donut chart](assets/classification-breakdown.png)

### Classification Summary

Each citation category with its count, percentage of classifiable citations, and the HEROCON weight applied.

![Classification summary — Web Interface](assets/classification-summary.png)

![Classification summary — Command Line Interface](assets/classification-summary-cli.png)

### Co-Author Network Graph

Interactive force-directed network. The target researcher appears as a gold node, direct co-authors in crimson (sized by shared publications), and transitive co-authors in blue. Hover any node for details. Networks exceeding 150 nodes are automatically pruned.

![Co-author network graph (overview)](assets/co-author-network.png)

![Co-author network graph (detail)](assets/co-author-network2.png)

### Career Trajectory

Cumulative BARON and HEROCON scores over time as dual lines, with a shaded region representing the gap. Stacked bars beneath show annual citation volume.

![Career trajectory — Web Interface](assets/career-trajectory.png)

![Career trajectory — Command Line Interface](assets/career-trajectory-cli.png)

### Citation Table

Every individual citation with its classification, confidence level, detection phase, and a human-readable rationale. This is the audit trail made visible — any classification can be inspected and contested.

![Full citation table from the audit trail](assets/citation-table.png)

### Comparison View

Side-by-side structural analysis of multiple researchers from uploaded audit files. Researcher names below are anonymized.

![Comparison table](assets/comparison-table.png)

![BARON trajectory comparison](assets/baron-trajectory-comparison.png)

![HEROCON trajectory comparison](assets/herocon-trajectory-comparison.png)

![Individual reports within the comparison view](assets/individual-reports.png)

---

## Input Validation

| Input | Validation |
|-------|-----------|
| ORCID | Format regex + ISO 7064 Mod 11,2 checksum |
| OpenAlex ID | Must match `A` followed by 3–15 digits |
| Since Year | Integer, 1900–current year |
| Depth | Must be 1, 2, or 3 |
| Custom Weights | Valid JSON with numeric values |

Errors are shown as clear, actionable messages — never raw stack traces.

---

## Rate Limiting

- **10 analyses per hour** per session (configurable via `RATE_LIMIT_MAX`)
- Applies to Run Analysis only — View Existing Audits has no limit
- Remaining run count displayed below the Run button

---

## Error Handling

| Error Type | User sees |
|-----------|-----------|
| Invalid input | Validation error with specific guidance |
| Network failure | Brief explanation with retry suggestion |
| Invalid JSON upload | File rejected with reason |
| Rate limit | Wait time shown |
| Unexpected error | Truncated message, no raw traceback |

---

## Running Locally

### Python (simplest)

```bash
cd citation-constellation/
pip install -r app/requirements.txt
python app/main.py
# Open http://localhost:7860
```

### Docker from Source

```bash
cd citation-constellation
docker build --platform linux/amd64 -t citation-constellation:v0.3 .
docker run --rm -it -p 7860:7860 citation-constellation:v0.3
```

### Prebuilt Image

```bash
docker pull mahbub1969/citation-constellation:v1
docker run --rm -it -p 7860:7860 mahbub1969/citation-constellation:v1
```

---

## File Structure

```
app/
├── main.py                      # Gradio app entry point
├── README.md                    # This file
├── runner.py                    # Async pipeline runner (thread-safe)
├── tabs/
│   ├── __init__.py
│   ├── run_analysis.py          # Tab 1: Run new analysis
│   ├── visualize.py             # Tab 2: Upload & compare JSON files
│   ├── BARON_and_HEROCON.py     # Tab 4: How BARON & HEROCON Work
│   ├── FUTURE_FEATURES.py       # Tab 5: Roadmap
│   └── HOW_TO_RUN.py            # Tab 3: Installation & usage guide
├── components/
│   ├── __init__.py
│   ├── coauthor_graph.py        # Interactive force-directed network (plotly)
│   ├── trajectory_chart.py      # BARON/HEROCON career trajectory (plotly)
│   ├── score_panel.py           # Score donut chart + summary
│   ├── classification_table.py  # Sortable citation table
│   └── comparison.py            # Multi-researcher comparison
├── validation.py                # ORCID/OpenAlex format validation
├── rate_limiter.py              # In-memory rate limiting
├── confirmation.py              # Paper discard confirmation workflow
├── branding.py                  # Logo, footer, disclaimers, repo links
└── assets/
    ├── cover-full.png
    ├── ethical-note.png
    ├── score-panel-tool.png
    ├── classification-breakdown.png
    ├── co-author-network.png
    ├── career-trajectory.png
    ├── citation-table.png
    ├── comparison-table.png
    ├── baron-trajectory-comparison.png
    ├── herocon-trajectory-comparison.png
    ├── individual-reports.png
    └── phased-architecture.png
```

### Component Design

Each visualization component is a standalone module that accepts a parsed JSON audit dict and returns a plotly Figure or pandas DataFrame:

```python
from app.components.coauthor_graph import build_coauthor_graph
from app.components.trajectory_chart import build_trajectory_chart
from app.components.score_panel import build_score_donut

# Works with any audit JSON — from a fresh run or an uploaded file
fig = build_coauthor_graph(audit_data)
```

### Why runner.py Exists

Gradio runs its own asyncio event loop internally. The Phase 1–3 pipeline uses `async/await` with httpx for OpenAlex API calls. Calling `asyncio.run()` inside a Gradio callback fails (the event loop is already running).

`runner.py` solves this by executing the async pipeline in a **separate thread with its own event loop** via `concurrent.futures.ThreadPoolExecutor`. This makes the Run Analysis button work reliably on first click.

---

## Performance

**Where time is spent:** ~95% is OpenAlex API calls (fetching citing works for each publication). For ~80 papers and ~1,500 citations, expect 30–90 seconds. Visualizations render in under 1 second.

**Large co-author networks:** Networks with 500+ nodes are auto-pruned to the top 150 by co-authorship strength. Target researcher and all direct co-authors are always kept. A subtitle shows "showing top 150/523 nodes" when pruning occurs.

**Graph layout:** Networks under 80 nodes use spring layout (prettier). Larger networks use Kamada-Kawai (faster). Graph rendering stays under 500ms regardless of size.

**Progress feedback:** Status updates throughout: "Resolving researcher profile...", "Fetching publications from OpenAlex...", "Building visualizations...", "Done!"

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_MAX` | `10` | Max analysis runs per hour per session |
| `GRADIO_TEMP_DIR` | `/home/appuser/app/temp/` | Temporary upload directory |
| `GRADIO_SERVER_NAME` | `0.0.0.0` | Server bind address |

---

## Quick Score Reference

| Score | Measures | Higher means |
|-------|----------|-------------|
| **BARON** | % of citations from completely outside your network | More external reach |
| **HEROCON** | Weighted %, partial credit for in-group | More total weighted reach |
| **Gap** | HEROCON − BARON | More inner-circle dependence |

| Classification | Phase | BARON | HEROCON Weight |
|---------------|-------|-------|----------------|
| SELF | 1 | 0 | 0.0 |
| DIRECT_COAUTHOR | 2 | 0 | 0.2 |
| TRANSITIVE_COAUTHOR | 2 | 0 | 0.5 |
| SAME_DEPT | 3 | 0 | 0.1 |
| SAME_INSTITUTION | 3 | 0 | 0.4 |
| SAME_PARENT_ORG | 3 | 0 | 0.7 |
| EXTERNAL | — | 1 | 1.0 |
| UNKNOWN | — | excluded | excluded |

---

## Part of the Citation-Cosmograph Ecosystem

| Component | Purpose | Link |
|-----------|---------|------|
| **Citation-Constellation** | BARON & HEROCON scoring | [Live Tool](https://citation-constellation.serve.scilifelab.se) · [Source](https://github.com/citation-cosmograph/citation-constellation) |
| **Citation-Pulsar-Helm** | LLM inference on Kubernetes | [Source](https://github.com/citation-cosmograph/citation-pulsar-helm) |
| **Citation-Astrolabe** | Venue governance database | [Source](https://github.com/citation-cosmograph/citation-astrolabe) |

[github.com/citation-cosmograph](https://github.com/citation-cosmograph)

---

## Phased Implementation Architecture Diagram
![Phased Implementation Architecture Diagram](app/assets/phased-architecture.png)

---

## Future Roadmap Diagram
![Future Roadmap Diagram](app/assets/project-plan.png)

---

## Paper

For the full methodology, conceptual foundations, tool landscape comparison, discussion of responsible research assessment alignment, and detailed limitations analysis, see the accompanying research paper:

Mahbub Ul Alam. Where do your citations come from? Citation-Constellation: A free, open-source, no-code, and auditable tool for citation network decomposition with complementary BARON and HEROCON scores, 2026. URL: https://arxiv.org/abs/2603.24216, arXiv:2603.24216, doi:10.48550/arXiv.2603.24216.

The paper is also available embedded within the web tool under the **Full Research Paper** tab.

### BibTeX

```bibtex
@misc{alam2026citationconstellation,
  title={Where Do Your Citations Come From? {C}itation-{C}onstellation: A Free, Open-Source, No-Code, and Auditable Tool for Citation Network Decomposition with Complementary {BARON} and {HEROCON} Scores},
  author={Mahbub Ul Alam},
  year={2026},
  eprint={2603.24216},
  archivePrefix={arXiv},
  primaryClass={cs.DL},
  url={https://arxiv.org/abs/2603.24216},
  doi={10.48550/arXiv.2603.24216}
}
```
## Acknowledgements

Built on [SciLifeLab Serve](https://serve.scilifelab.se). Powered by [OpenAlex](https://openalex.org), [ORCID](https://orcid.org), and [ROR](https://ror.org).

---

## License

MIT
