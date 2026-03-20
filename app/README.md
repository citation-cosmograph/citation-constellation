# BARON & HEROCON — Web Interface

**Citation Network Structure Analysis — No-Code UI**

A Gradio-based web interface for computing and visualizing BARON and HEROCON scores. Designed for researchers who want interactive results without touching the command line. Deployed on [SciLifeLab Serve](https://serve.scilifelab.se).

```
pulsar 🌟 → astrolabe 🔭 → citation-constellation ✨
(the signal)   (the instrument)   (the map — you are here)
```

---

## ⚠️ Ethical Notice

These scores measure **citation network structure** — where in the social graph citations originate — **not research quality, impact, or integrity**.

In-group citation is normal and often appropriate. A low BARON score may indicate a productive collaborative lab, a small-field researcher, or a disciplinary norm — not a flaw in research practice.

**These scores should NOT be used for hiring, promotion, or funding decisions.**

Every classification decision is documented in the downloadable audit trail. Verify any result before drawing conclusions.

---

## How to Use

The interface has three tabs: **Run New Analysis**, **Visualize Existing Reports**, and **About**.

### Tab 1: Run New Analysis

Enter a researcher identifier and get interactive BARON & HEROCON results.

#### Input Fields

| Field | What to enter | Required? |
|-------|--------------|-----------|
| **Researcher Identifier** | An ORCID (e.g., `0000-0000-0000-0000`) or OpenAlex ID (e.g., `A5100390903`). You can paste the full URL — the tool extracts the ID automatically. | Yes |
| **Since Year** | Exclude publications before this year. Useful when OpenAlex has merged works from a different researcher with a similar name. Leave blank to include all works. | No |
| **Co-author Graph Depth** | How many hops of co-authorship count as "in-group". **Depth 1:** only direct co-authors. **Depth 2** (recommended): co-authors of co-authors. **Depth 3:** three hops, largest in-group. | Default: 2 |
| **Wait for my validation** | When checked, the tool pauses after ORCID validation to show you a list of flagged papers (potential misattributions). You review and confirm before scoring proceeds. When unchecked, flagged papers are automatically excluded. | Default: off |
| **Custom HEROCON Weights** | Upload a JSON file to override the default graduated weights. Any classification not specified uses the default. | No |

#### What Happens When You Click "Run Analysis"

1. The tool resolves the researcher profile via OpenAlex
2. Fetches all their publications (with ORCID cross-validation)
3. For each publication, fetches all incoming citations
4. Classifies every citation through three detection layers:
   - **Phase 1:** Self-citations (author ID match)
   - **Phase 2:** Co-author network (graph distance)
   - **Phase 3:** Institutional affiliation (temporal ROR matching)
5. Computes BARON (strict) and HEROCON (graduated) scores
6. Generates interactive visualizations and a downloadable audit report

**Rate limit:** 10 analyses per hour per session. The counter resets hourly.

#### Results You'll See

**Score Summary** — BARON, HEROCON, gap, total citations, reliability rating in a clean table.

**Classification Donut** — Visual breakdown of where citations come from: self, co-author, institutional, external, unknown. BARON and HEROCON scores displayed in the center.

**Classification Summary Table** — Each category with count, percentage, and HEROCON weight.

**Co-Author Network Graph** — Interactive force-directed network:
- 🟡 **Gold node (large):** Target researcher
- 🔴 **Crimson nodes:** Direct co-authors (depth 1). Size scales with shared papers.
- 🔵 **Blue nodes:** Transitive co-authors (depth 2)
- **Edges:** Thickness reflects co-authorship strength (papers × recency decay)
- **Hover** any node to see: name, shared papers, strength, last collaboration year
- **Zoom, pan, reset** with plotly controls

**Career Trajectory Chart** — Dual-line chart showing BARON (yellow) and HEROCON (green) over time:
- Shaded area between the lines = the "gap" (inner circle effect)
- Gray bars = cumulative citation count (right axis)
- Hover any year for exact values

**Full Classification Table** — Every individual citation with: citing paper, cited paper, classification, confidence, phase, and human-readable rationale. Sortable and searchable. Expandable accordion (collapsed by default to keep the page clean).

**Download Button** — Downloads the complete JSON audit report. Filename format:
```
Mahbub_Ul_Alam_Citation_Constellation_Scores_BARON_84.9_HEROCON_85.9_Orcid_0000000211013793_timestamp_20260315_215252_audit_report.json
```
For researchers identified by OpenAlex ID (no ORCID):
```
Mahbub_Ul_Alam_Citation_Constellation_Scores_BARON_84.9_HEROCON_85.9_OpenAlex_A5100390903_timestamp_20260315_215252_audit_report.json
```
No academic titles (Dr., Prof.) in the filename — just the name.

---

### Tab 2: Visualize Existing Reports

Upload previously generated BARON/HEROCON audit JSON files for visualization and comparison. No computation — pure visualization.

#### Single File Upload

Upload one `.json` audit report → get the full visualization suite (same as Tab 1 results): score summary, donut chart, classification table, co-author graph, trajectory.

#### Multiple File Upload

Upload 2–5 `.json` files → get a **comparison view**:

**Comparison Table** — Side-by-side: Researcher, ORCID, Works, Citations, BARON, HEROCON, Gap, Reliability, Data Quality, Self-cite %, External %.

**Overlaid Trajectory** — All researchers' BARON scores on one chart with different colors. Quickly see who has growing vs. declining external reach.

**Individual Reports** — Expandable accordion for each researcher with their full individual visualizations (donut, graph, trajectory).

#### Accepted Files

- Format: JSON audit reports generated by citation-constellation (CLI or UI)
- Max size: 100 MB per file (SciLifeLab Serve limit)
- The tool validates that uploaded files contain the expected `score` and `researcher` fields

---

### Tab 3: About

Background information: what the scores mean, what they don't mean, detection phases, data sources, naming etymology, source code links, and paper reference.

---

## Input Validation

The UI validates all inputs before running:

| Input | Validation |
|-------|-----------|
| ORCID | Format regex + ISO 7064 Mod 11,2 checksum |
| OpenAlex ID | Must match `A` followed by 3–15 digits |
| Since Year | Integer, 1900–current year |
| Depth | Must be 1, 2, or 3 |
| Custom Weights | Must be valid JSON with numeric values |

Validation errors are shown as clear, actionable messages — never raw stack traces. For example:
- *"Invalid ORCID format. Expected: 0000-0000-0000-0000 (four groups of four digits separated by hyphens, last character may be X)."*
- *"ORCID checksum failed for '0000-0000-0000-0001'. Please double-check the ID — one or more digits may be wrong."*

---

## Rate Limiting

To protect the OpenAlex API and ensure fair usage:

- **10 analyses per hour** per session (configurable via `RATE_LIMIT_MAX` environment variable)
- Applies to Tab 1 only — Tab 2 (visualization) has no limit
- The remaining run count is displayed below the Run button
- When the limit is reached: *"Rate limit reached (10 analyses per hour). Please try again in ~X minute(s)."*

---

## Error Handling

All errors are caught and displayed as user-friendly messages:

| Error Type | What You See |
|-----------|-------------|
| Invalid input | ⚠️ Validation Error: [specific guidance] |
| Network failure | ❌ Analysis failed: [brief explanation]. Please check the identifier and try again. |
| Invalid JSON upload | ❌ File X: Does not appear to be a BARON/HEROCON audit report |
| Rate limit | ⚠️ Rate limit reached. Please try again in ~X minute(s). |
| Unexpected error | ❌ Unexpected error: [truncated message]. Please try again or report this issue. |

No raw Python tracebacks are ever shown to the user.

---

## Deployment on SciLifeLab Serve

### Build the Docker image

```bash
cd citation-constellation
docker build --platform linux/amd64 -t citation-constellation:v0.3 .
```

### Test locally

```bash
docker run --rm -it -p 7860:7860 citation-constellation:v0.3
# Open http://localhost:7860
```

### Push to registry

```bash
# DockerHub
docker tag citation-constellation:v0.3 yourusername/citation-constellation:v0.3
docker push yourusername/citation-constellation:v0.3

# Or GitHub Container Registry (via GitHub Actions — see .github/workflows/)
```

### Deploy on Serve

1. Log in to [serve.scilifelab.se](https://serve.scilifelab.se)
2. Create or open a project
3. Create a **Gradio app** with:
   - **Name:** BARON & HEROCON
   - **Port:** 7860
   - **Image:** `yourusername/citation-constellation:v0.3`
   - **Permissions:** Public (or Link for pre-publication review)

### SciLifeLab Serve constraints

| Constraint | How we comply |
|-----------|--------------|
| Non-root user, uid 1000 | `useradd -m -u 1000 appuser` in Dockerfile |
| Port 3000–9999 | Using 7860 (Gradio default) |
| Default 2 vCPU / 4 GB RAM | Sufficient for Phase 1–3 analysis |
| No user databases | No persistent state — resets on restart |
| No sensitive data | Only public bibliometric data |
| Upload limit 100 MB | Documented in UI |
| Public code required | MIT licensed on GitHub |
| Unique image tags | Use version tags (v0.3, v0.3.1, etc.) |

---

## File Structure

```
app/
├── main.py                  # Gradio app entry point
├── README.md                # This file
├── runner.py                # Async pipeline runner (thread-safe)
├── tabs/
│   ├── __init__.py
│   ├── run_analysis.py      # Tab 1: Run new analysis
│   └── visualize.py         # Tab 2: Upload & compare JSON files
├── components/
│   ├── __init__.py
│   ├── coauthor_graph.py    # Interactive force-directed network (plotly)
│   ├── trajectory_chart.py  # BARON/HEROCON career trajectory (plotly)
│   ├── score_panel.py       # Score donut chart + summary
│   ├── classification_table.py  # Sortable citation table
│   └── comparison.py        # Multi-researcher comparison
├── validation.py            # ORCID/OpenAlex format validation
├── rate_limiter.py          # In-memory rate limiting
├── confirmation.py          # Paper discard confirmation workflow
├── branding.py              # Logo, footer, disclaimers, repo links
└── assets/
    ├── logo_placeholder.png
    ├── favicon_placeholder.ico
    └── cover_placeholder.png
```

### Component Design

Each visualization component is a standalone module that accepts a parsed JSON audit dict and returns a plotly Figure or pandas DataFrame. This makes them reusable:

```python
from app.components.coauthor_graph import build_coauthor_graph
from app.components.trajectory_chart import build_trajectory_chart
from app.components.score_panel import build_score_donut

# Works with any audit JSON — from a fresh run or an uploaded file
fig = build_coauthor_graph(audit_data)
```

### Why runner.py exists

Gradio runs its own asyncio event loop internally. The Phase 1–3 pipeline uses `async/await` with httpx for OpenAlex API calls. Calling `asyncio.run()` inside a Gradio callback fails silently (the event loop is already running) or requires multiple button clicks to trigger.

`runner.py` solves this by executing the async pipeline in a **separate thread with its own event loop** via `concurrent.futures.ThreadPoolExecutor`. This makes the "Run Analysis" button work reliably on first click.

### Performance Notes

**Where time is spent:** ~95% of the processing time is OpenAlex API calls (fetching citing works for each publication). For a researcher with ~80 papers and ~1500 citations, expect 30–90 seconds. The visualizations (plotly + networkx) render in under 1 second.

**Large co-author networks:** Networks with 500+ nodes are automatically pruned to the top 150 by co-authorship strength. Target researcher and all direct co-authors are always kept; transitive co-authors are ranked and trimmed. A subtitle note shows "showing top 150/523 nodes" when pruning occurs.

**Graph layout algorithm:** Networks under 80 nodes use spring layout (prettier, slower). Larger networks use Kamada-Kawai layout (faster, still good). This keeps graph rendering under 500ms regardless of size.

**Progress feedback:** Gradio's built-in progress bar shows status during the analysis: "Resolving researcher profile...", "Fetching publications from OpenAlex (this may take 30–90 seconds)...", "Building visualizations...", "Done!"

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_MAX` | `10` | Max analysis runs per hour per session |
| `GRADIO_TEMP_DIR` | `/home/appuser/app/temp/` | Directory for temporary upload files |
| `GRADIO_SERVER_NAME` | `0.0.0.0` | Server bind address |

---

## What the Scores Mean — Quick Reference

| Score | What it measures | Higher means |
|-------|-----------------|-------------|
| **BARON** | % of citations from completely outside your network | More external reach |
| **HEROCON** | Weighted % giving partial credit to in-group | More total weighted reach |
| **Gap** | HEROCON − BARON | More inner-circle dependence |

| Classification | Detected by | BARON | HEROCON |
|---------------|-------------|-------|---------|
| Self | Phase 1 | 0 | 0.0 |
| Direct co-author | Phase 2 | 0 | 0.2 |
| Transitive co-author | Phase 2 | 0 | 0.5 |
| Same department | Phase 3 | 0 | 0.1 |
| Same institution | Phase 3 | 0 | 0.4 |
| Same parent org | Phase 3 | 0 | 0.7 |
| External | — | 1 | 1.0 |
| Unknown | — | excluded | excluded |

---

## Naming

**BARON** — from the *Marcher Baron*, the feudal lord charged with securing the outer boundaries of a realm. The BARON score anchors citation integrity by measuring only boundary-spanning outreach.

**HEROCON** — from the constellation *Hercules*, placed among the stars as a monument to labors transcending mortal limits. Its brightest star *Rasalgethi* (Arabic: *ra's al-jāthī*, "the kneeler's head") reminds us that scholarly leadership requires humility.

> Ridpath, I. (2018). *Star Tales* (revised and expanded edition). Lutterworth Press.

---

## Part of the Citation Constellation Ecosystem

```
pulsar 🌟 → astrolabe 🔭 → citation-constellation ✨
(the signal)   (the instrument)   (the map)
```

| Repo | What | Link |
|------|------|------|
| **pulsar-helm** | LLM inference on k8s | [github.com/citation-cosmograph/pulsar-helm](https://github.com/citation-cosmograph/pulsar-helm) |
| **astrolabe** | Venue governance database | [github.com/citation-cosmograph/astrolabe](https://github.com/citation-cosmograph/astrolabe) |
| **citation-constellation** | BARON & HEROCON scoring | [github.com/citation-cosmograph/citation-constellation](https://github.com/citation-cosmograph/citation-constellation) |

**Paper:** Alam, M. U. (2026). BARON and HEROCON: Revealing Citation Network Structure Through Multi-Layer Decomposition. *[arXiv: placeholder]*

---

## License

MIT