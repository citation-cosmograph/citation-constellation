# BARON & HEROCON

**Quantitative Impact Measurement of Research Outreach**

Two complementary bibliometric scores that measure how far a researcher's publications reach beyond their own collaborative network.

- **BARON** — Boundary-Anchored Research Outreach Network score. Strict: in-group citations count as zero. Pure external reach. Higher is better.
- **HEROCON** — Holistic Equilibrated Research Outreach CONstellation score. Graduated: in-group citations get partial credit through configurable weights. Always ≥ BARON. Higher is better.
- **The gap** — HEROCON minus BARON reveals how much of a researcher's impact depends on their inner circle.

### Why "BARON" and "HEROCON"?

**BARON** takes its name from the historical concept of a *Marcher Baron* — a feudal lord charged with securing the outer boundaries of a realm. Just as Marcher Barons anchored the borders so the interior could function with legitimacy, the BARON score anchors the integrity of a researcher's citation metrics by measuring strictly boundary-spanning, external outreach. It serves as the foundational threshold governing the broader HEROCON score: without demonstrated reach beyond the immediate circle, the constellation cannot take shape.

**HEROCON** draws from the constellation *Hercules* (IAU abbreviated *Her*). In Greek mythology, Heracles was placed among the stars after his death — an eternal monument to labors that transcended mortal limits. The HEROCON score maps a researcher's total influence as a constellation: localized collaborations form bright, dense clusters, but a constellation must stretch across the sky. The BARON score provides the anchoring boundary stars that give it shape. The constellation's brightest star, *Rasalgethi* (α Herculis, from the Arabic *ra's al-jāthī*, "the kneeler's head"), carries a further resonance: true scholarly leadership, like the kneeling Hercules, requires humility — a high HEROCON demonstrates that a researcher honors their community's contributions while illuminating the broader scholarly universe beyond it.

> Ridpath, I. (2018). *Star Tales* (revised and expanded edition). Lutterworth Press. — For the mythology and etymology of the constellation Hercules and Rasalgethi.

### Why "Citation Constellation"?

A constellation is not a physical grouping — the stars that form Hercules are scattered across vastly different distances. What makes them a constellation is *our* act of drawing lines between them, imposing narrative structure on apparent chaos. A researcher's citation profile is the same: individual citations scattered across journals, years, and fields, which only become a legible pattern when you trace the network connections between them.

This tool draws those lines. It reveals whether the bright points in a citation profile form a tight local cluster (in-group citations from co-authors and institutional colleagues) or a true constellation stretching across the scholarly sky (external citations from independent researchers). The BARON score measures the boundary stars — the distant anchors. The HEROCON score maps the full figure.

The name also positions this repo within its ecosystem: you need a **[pulsar](https://github.com/citation-cosmograph/pulsar-helm)** (steady LLM signal) to power the **[astrolabe](https://github.com/citation-cosmograph/astrolabe)** (instrument mapping venue governance), which feeds the **citation-constellation** (the map of a researcher's scholarly sky).

```
pulsar 🌟 → astrolabe 🔭 → citation-constellation ✨
(the signal)   (the instrument)   (the map)
```

---

## Current Status: Phase 3 — Affiliation Matching

The tool implements three detection phases, each building on the last:

| Phase | What it detects | Score |
|-------|----------------|-------|
| **Phase 1** | Self-citations (author ID match) | BARON v0.1 |
| **Phase 2** | Co-author network (graph distance 1–2) | BARON & HEROCON v0.2 |
| **Phase 3** | Institutional affiliation (temporal ROR matching) | BARON & HEROCON v0.3 |

Phase 4 (venue governance detection via local LLM) is planned. Citations with insufficient metadata are classified as UNKNOWN and excluded from scores for honest data quality reporting.

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/citation-cosmograph/citation-constellation.git
cd citation-constellation
pip install -r requirements.txt

# Phase 1: Self-citation baseline
python phase1.py --orcid 0000-0000-0000-0000

# Phase 2: Co-author network detection
python phase2.py --orcid 0000-0000-0000-0000

# Phase 3: Affiliation matching (includes Phase 1 + 2 automatically)
python phase3.py --orcid 0000-0000-0000-0000

# Also accepts OpenAlex IDs
python phase3.py --openalex-id A0000000000
```

### Common flags (all phases)

```bash
--export results.json      # Export summary to JSON
--trajectory / -t          # Show cumulative career trajectory by year
--since 2010               # Only include works from 2010 onward
--no-orcid-check           # Skip ORCID cross-validation
--no-audit                 # Skip audit file generation (not recommended)
--verbose / -v             # Verbose output
```

### Phase 2+ flags

```bash
--depth 1|2|3              # Co-author graph depth (default 2)
--herocon-weights file.json # Custom HEROCON weight configuration
```

### Phase 3 flags

```bash
--confirm / -c             # Review ORCID-flagged works interactively before scoring
```

---

## How It Works

### BARON vs HEROCON

**BARON** is binary. Every citation is either in-group (weight 0) or external (weight 1). No partial credit.

**HEROCON** is graduated. In-group citations get partial credit based on relationship proximity. A co-author's citation still counts — just less than a stranger's.

### Full Classification Table

| Class | Phase | BARON | HEROCON | Description |
|-------|-------|-------|---------|-------------|
| `SELF` | 1 | 0 | 0.0 | Self-citation — no credit |
| `VENUE_SELF_GOVERNANCE` | 4 | 0 | 0.05 | Researcher governs citing venue *(Phase 4)* |
| `SAME_DEPT` | 3 | 0 | 0.1 | Same department, no co-authorship |
| `VENUE_EDITOR_COAUTHOR` | 4 | 0 | 0.15 | Venue editor is co-author *(Phase 4)* |
| `DIRECT_COAUTHOR` | 2 | 0 | 0.2 | Shared ≥1 publication |
| `VENUE_EDITOR_AFFIL` | 4 | 0 | 0.3 | Venue editor at same institution *(Phase 4)* |
| `SAME_INSTITUTION` | 3 | 0 | 0.4 | Same university, different department |
| `VENUE_COMMITTEE` | 4 | 0 | 0.4 | Committee member in network *(Phase 4)* |
| `TRANSITIVE_COAUTHOR` | 2 | 0 | 0.5 | Co-author's co-author |
| `SAME_PARENT_ORG` | 3 | 0 | 0.7 | Different institution, shared parent org |
| `EXTERNAL` | — | 1 | 1.0 | No detected relationship — full credit |
| `UNKNOWN` | — | — | — | Insufficient metadata — excluded from scores |

*HEROCON weights are configurable experimental defaults, not empirically calibrated values.*

### Co-Authorship Strength (Phase 2)

Not all co-authorships are equal. Each co-author edge has a strength score:

```
strength = shared_papers × exp(-0.1 × years_since_last_collab)
```

A co-author you published 10 papers with last year has much higher strength than someone you wrote 1 paper with a decade ago. The strength score is logged in audit metadata for each classification.

### Co-Author Graph Depth (Phase 2+)

The `--depth` flag controls how many hops of co-authorship are considered in-group:

```
Researcher (depth 0)
├── Co-author A (depth 1) — 12 shared papers
│   ├── A's co-author X (depth 2)
│   └── A's co-author Y (depth 2)
├── Co-author B (depth 1) — 3 shared papers
│   └── B's co-author Z (depth 2)
└── ...
```

| Depth | In-group includes | Best for |
|-------|-------------------|----------|
| `1` | Only your direct co-authors | Large, loosely collaborative fields |
| `2` | Co-authors + their co-authors | Most researchers (default) |
| `3` | Three hops out | Small, tightly-knit fields |

Higher depth = more people classified as in-group = lower BARON and HEROCON scores.

**Important:** The depth-2 expansion uses only co-authorship edges visible in the researcher's own publication record. It does not fetch the full publication history of each co-author. This makes the graph a conservative undercount of the true transitive network.

### Temporal Affiliation Matching (Phase 3)

A citation from 2022 should be matched against where both researchers were *in 2022*, not where they are today.

**Building the timeline.** For every work in OpenAlex, the `authorships` field records each author's institution at the time of that specific publication. Phase 3 extracts these into a per-author timeline:

```
Author A:
  2018 → Enchanted Forest University  (from paper W001)
  2019 → Enchanted Forest University  (from paper W002)
  2021 → Dragon Peak Research Centre  (from paper W003)
  2023 → Dragon Peak Research Centre  (from paper W004)
```

**Matching at citation time.** When a citation from 2020 needs to be classified, the system looks up the citer's affiliation at 2020. If no exact year match exists, it uses the closest earlier year (2019 above).

**Institution hierarchy.** Two institutions can be related without sharing the same ROR ID. Phase 3 resolves this using ROR parent/child relationships:

```
The Enchanted Realms Consortium (parent)
├── Enchanted Forest University
├── Dragon Peak Research Centre
├── Mermaid Lagoon Institute of Technology
└── ...
```

A citation from Enchanted Forest University to a researcher at Dragon Peak Research Centre → `SAME_PARENT_ORG`.

**Department detection.** ROR lacks department-level data for most institutions. Phase 3 uses a heuristic: extract department-like phrases from raw affiliation strings and compare. When uncertain, the system conservatively assigns `SAME_INSTITUTION` rather than `SAME_DEPT`.

---

## Interactive Confirmation Mode (`--confirm`)

When ORCID cross-validation flags potentially misattributed works, you can review them interactively before scoring:

```bash
python phase3.py --orcid 0000-0000-0000-0000 --confirm
```

The `--confirm` flag triggers a two-stage workflow:

1. **Validate first.** The tool fetches works, runs ORCID validation, and displays any flagged works with their reasons.
2. **You decide.** A prompt lets you choose which flagged works to exclude from scoring.

### Example session

```
Confirm mode: fetching works and validating against ORCID...

  ⚠ 3 work(s) flagged:

    1. Rapunzel's Tower: A Recursive Descent into Hair-Braiding Algorithms (2015)
       Affiliation(s) faraway kingdom polytechnic never appear in known works
    2. The Glass Slipper Problem in Combinatorial Optimization (2009)
       Affiliation(s) enchanted castle institute never appear in known works
    3. Snow White and the Seven Clustering Algorithms (2007)
       Affiliation(s) mirror mirror analytics lab never appear in known works

  Exclude which? (all / none / 1,3,5 / 1-3,5)
  > 1,3
```

### Input format

| Input | Effect |
|-------|--------|
| `all` or `a` | Exclude all flagged works |
| `none` or `n` | Keep all flagged works (proceed with everything) |
| `1,3,5` | Exclude specific works by number |
| `1-3,5` | Ranges and individual numbers can be mixed |

After your selection, the full Phase 3 pipeline runs with the chosen exclusions. The audit trail records which works were excluded and why.

**Note:** `--confirm` requires ORCID validation to be active. It has no effect when combined with `--no-orcid-check` or when the researcher has no ORCID on their OpenAlex profile.

---

## Example Output

### Progressive score display (Phase 3)

Each phase shows scores at every detection step with deltas:

```
Step 1 — Self-citation detection:
  BARON  86.7%                      (198 self-citations removed)

Step 2 — Co-author network:
  BARON  68.4%  ↓18.3%    HEROCON 74.1%    (273 co-author citations detected)

Step 3 — Affiliation matching:
  BARON  61.2%  ↓7.2%     HEROCON 70.5%    (107 institutional citations)

─── Final ─────────────────────────────
  BARON  61.2%             HEROCON 70.5%
  Gap     9.3%
```

### Full score panel (Phase 3)

```
╭─── BARON & HEROCON v0.3 — Affiliation Matching ─╮
│ XXXX YYYY                                    │
│ ORCID: 0000-0000-0000-0000                       │
│ OpenAlex: A0000000000  |  Works: 87              │
╰──────────────────────────────────────────────────╯

╭─── Score ────────────────────────────────────────╮
│ BARON v0.3                            61.2%      │
│ HEROCON v0.3                          70.5%      │
│   Gap (HEROCON − BARON)                9.3%      │
│                                                  │
│   External citations          911   (61.2%)      │
│                                                  │
│   Co-author in-group:                            │
│     Self-citations            198   (13.3%)      │
│     Direct co-author          187   (12.6%)      │
│     Transitive co-author       86    (5.8%)      │
│                                                  │
│   Affiliation in-group:                          │
│     Same department             23    (1.5%)     │
│     Same institution            61    (4.1%)     │
│     Same parent org             23    (1.5%)     │
│                                                  │
│   Total citations                      1489      │
│   Classifiable                 1357   (91.1%)    │
│   Reliability                         HIGH       │
╰──────────────────────────────────────────────────╯
```

### Career trajectory (with `--trajectory`)

```
╭─── Career Trajectory (cumulative) ────╮
│ Year  Citations  BARON    HEROCON     │
│ 2018         9   88.9%     —          │
│ 2019        28   82.1%   86.3%       │
│ 2020        67   74.6%   80.2%       │
│ 2021       134   70.1%   76.8%       │
│ 2022       198   68.4%   74.1%       │
╰───────────────────────────────────────╯
```

### Typical score progression across phases

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| BARON | 86.7% | 68.4% | 61.2% |
| HEROCON | — | 74.1% | 70.5% |
| Gap | — | 5.7% | 9.3% |
| Classes | 2 | 4 | 7 |

The BARON drop from Phase 1→2 is typically 10–25 percentage points. Phase 2→3 drops 5–15 points, depending on how concentrated the career has been within one or two institutions.

---

## Customizing HEROCON Weights

HEROCON weights are **experimental defaults**. The tool supports full customization.

### Create a custom weights file

Save as JSON. Any classification not specified uses the default:

```json
{
    "SELF": 0.0,
    "DIRECT_COAUTHOR": 0.3,
    "TRANSITIVE_COAUTHOR": 0.6,
    "SAME_DEPT": 0.2,
    "SAME_INSTITUTION": 0.5,
    "SAME_PARENT_ORG": 0.8,
    "EXTERNAL": 1.0
}
```

### Use custom weights

```bash
python phase3.py --orcid 0000-0000-0000-0000 --herocon-weights my_weights.json
```

Custom weights are logged in both the audit trail and JSON export.

### When to customize

- **Highly collaborative field** — increase co-author weights (e.g., 0.4 instead of 0.2) since co-author citations are more normal
- **Small field** — transitive co-author at depth 2 might cover your whole community; increase that weight
- **Stricter analysis** — set all in-group weights closer to 0.0 (HEROCON approaches BARON)
- **Lenient analysis** — set weights closer to 1.0 (HEROCON approaches raw citation count)

---

## ORCID Cross-Validation — Author Identity

OpenAlex uses algorithmic author disambiguation that can merge works from different researchers with similar names. All phases automatically validate against the researcher's ORCID record using a **smart two-mode system**:

**High ORCID coverage (≥70%):** ORCID used as a hard filter — only works in both ORCID and OpenAlex enter the scoring pipeline.

**Low ORCID coverage (<70%):** All OpenAlex works kept, but **affiliation anomaly detection** flags works from institutions never associated with the researcher. Only flagged works are excluded.

If the publication span looks suspiciously wide (>25 years):

```
⚠ Publication span is 52 years (1973–2025). This may indicate name collision
  with a different researcher. If works before a certain year are not yours,
  re-run with: --since YEAR
```

### The `--since` flag

```bash
python phase3.py --orcid 0000-0000-0000-0000 --since 2010 --trajectory
```

Explicitly sets the career start year — all works before excluded. Cleanest fix for name collisions. The researcher always knows when their career started. No guessing, no silent filtering.

### The `--confirm` flag

```bash
python phase3.py --orcid 0000-0000-0000-0000 --confirm
```

Interactive review of ORCID-flagged works before scoring. See [Interactive Confirmation Mode](#interactive-confirmation-mode---confirm) above for full details.

---

## Audit Trail — Full Transparency

Every run generates a comprehensive, timestamped JSON audit file in `./audits/`. This is **on by default** — researchers deserve to see exactly how their score was computed.

### Naming convention

```
audits/Researcher_Name_Citation_Constellation_Scores_BARON_61.2_HEROCON_70.5_Orcid_0000000000000000_timestamp_20260315_215252_audit_report.json
```

Timestamps prevent overwrites between runs.

### What's in an audit file

- Every work analyzed (title, authors, venue, year)
- Every citation link (which paper cited which)
- Every classification decision with a **human-readable rationale**
- The full co-author graph with edge weights, distances, and strength (Phase 2+)
- The affiliation timeline and institution hierarchy (Phase 3)
- ORCID validation results
- The complete score computation with breakdown

### Example: co-author classification (Phase 2)

```json
{
  "citing_work": {
    "id": "W0000000005",
    "title": "Rapunzel's Tower: A Recursive Descent into Hair-Braiding Algorithms",
    "year": 2023,
    "authors": [
      { "id": "A0000000002", "name": "Dr. CCCC DDDD" }
    ]
  },
  "cited_work": {
    "id": "W0000000006",
    "title": "The Three Bears Conjecture in Load Balancing",
    "year": 2021
  },
  "classification": "DIRECT_COAUTHOR",
  "confidence": 1.0,
  "phase_detected": 2,
  "rationale": "Citing author 'Dr. CCCC DDDD' is a direct co-author of target (graph distance 1, 5 shared papers)",
  "metadata": {
    "closest_author_id": "A0000000002",
    "closest_author_name": "Dr. CCCC DDDD",
    "graph_distance": 1,
    "shared_papers": 5,
    "coauthor_strength": 4.524,
    "last_collab_year": 2023
  }
}
```

### Example: affiliation classification (Phase 3)

```json
{
  "citing_work": {
    "id": "W0000000003",
    "title": "The Glass Slipper Problem in Combinatorial Optimization",
    "year": 2023,
    "authors": [
      { "id": "A0000000001", "name": "Prof. AAAA BBBB" }
    ]
  },
  "cited_work": {
    "id": "W0000000004",
    "title": "Once Upon a Tensor: Fairy Tale Embeddings for NLP",
    "year": 2022
  },
  "classification": "SAME_INSTITUTION",
  "confidence": 1.0,
  "phase_detected": 3,
  "rationale": "Citing author at same institution 'Enchanted Forest University' (ROR: 00xx00xx0), different department from target",
  "metadata": {
    "citing_author_id": "A0000000001",
    "citing_institution": "Enchanted Forest University",
    "citing_institution_ror": "00xx00xx0",
    "citing_affil_year": 2023,
    "target_institution": "Enchanted Forest University",
    "target_institution_ror": "00xx00xx0",
    "target_affil_year": 2022,
    "temporal_concurrent": false
  }
}
```

### Example: affiliation timeline in audit (Phase 3)

```json
{
  "affiliation_data": {
    "target_affiliation_history": [
      {
        "year": 2018,
        "institution": "Enchanted Forest University",
        "ror_id": "00xx00xx0",
        "source_work": "W0000000001",
        "department": null
      },
      {
        "year": 2024,
        "institution": "Dragon Peak Research Centre",
        "ror_id": "00yy00yy0",
        "source_work": "W0000000002",
        "department": null
      }
    ],
    "target_institutions": {
      "00xx00xx0": {
        "name": "Enchanted Forest University",
        "country": "XX",
        "type": "education",
        "parent_ror": null
      }
    },
    "timeline_stats": {
      "total_authors_tracked": 412,
      "total_affiliation_records": 2834
    }
  }
}
```

### Disabling audit (not recommended)

```bash
python phase1.py --orcid 0000-0000-0000-0000 --no-audit
```

---

## JSON Export Format

```json
{
  "version": "v0.3",
  "phase": 3,
  "created_at": "2026-03-12T14:30:22",
  "disclaimer": "BARON and HEROCON measure citation network structure, not research quality...",
  "config": { "coauthor_depth": 2 },
  "researcher": {
    "openalex_id": "A0000000000",
    "orcid": "0000-0000-0000-0000",
    "display_name": "Dr. XXXX YYYY",
    "works_count": 87,
    "cited_by_count": 1489
  },
  "score": {
    "baron_v03": 62.8,
    "herocon_v03": 71.9,
    "data_quality_pct": 91.1,
    "reliability": "HIGH",
    "herocon_weights": {
      "SELF": 0.0,
      "DIRECT_COAUTHOR": 0.2,
      "TRANSITIVE_COAUTHOR": 0.5,
      "SAME_DEPT": 0.1,
      "SAME_INSTITUTION": 0.4,
      "SAME_PARENT_ORG": 0.7,
      "EXTERNAL": 1.0
    },
    "breakdown": {
      "total_citations": 1489,
      "classifiable_citations": 1357,
      "unknown_citations": 132,
      "data_quality_pct": 91.1,
      "reliability": "HIGH",
      "self_citations": 198,
      "direct_coauthor_citations": 187,
      "transitive_coauthor_citations": 86,
      "same_dept_citations": 23,
      "same_institution_citations": 48,
      "same_parent_org_citations": 18,
      "external_citations": 853
    }
  },
  "coauthor_stats": {
    "graph_nodes": 234,
    "graph_edges": 891,
    "direct_coauthors": 31,
    "transitive_coauthors": 203,
    "top_coauthors": [
      {
        "name": "Prof. AAAA BBBB",
        "openalex_id": "A0000000001",
        "shared_papers": 12,
        "strength": 10.86,
        "last_collab": 2025
      }
    ]
  },
  "ingestion_stats": { "..." : "..." }
}
```

---

## Configuration

Edit the top of `client.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENALEX_MAILTO` | `your-email@example.com` | Your email for OpenAlex polite pool |
| `PER_PAGE` | `200` | Results per API page (max 200) |
| `MAX_CONCURRENT` | `5` | Concurrent API requests |
| `RATE_LIMIT_DELAY` | `0.1` | Seconds between request batches |

---

## Architecture

```
ORCID / OpenAlex ID
        │
        ▼
┌─────────────────┐
│ OpenAlex + ROR  │  client.py
└────────┬────────┘
         │
    ┌────┼────────────┐
    ▼    ▼            ▼
┌──────┐┌──────┐┌──────────┐
│ P1   ││ P2   ││ P3       │
│ self ││ co-  ││ affil    │
│ cite ││ auth ││ timeline │
└──┬───┘└──┬───┘└────┬─────┘
   └───────┼─────────┘
           ▼
    BARON   (strict, binary)
    HEROCON (weighted, graduated)
           │
           ▼
    audit.py → audits/baron_{id}_phase{N}.json
```

### Phase 4 Ecosystem (planned)

```
pulsar-helm 🌟              astrolabe 🔭              citation-constellation ✨
┌────────────────┐    ┌────────────────────┐    ┌──────────────────────────┐
│ Qwen 3.5 8B    │    │ Venue governance   │    │ phase4.py                │
│ llama.cpp      │───▶│ Scrape + Extract   │───▶│ VENUE_* classification   │
│ /v1/chat/...   │    │ Entity resolution  │    │ Reads astrolabe DB       │
│ k8s: pulsar    │    │ k8s: astrolabe     │    │ CLI on laptop            │
└────────────────┘    └────────────────────┘    └──────────────────────────┘
```

## File Structure

```
citation-constellation/
├── models.py           # Shared data models (all phases)
├── client.py           # OpenAlex + ROR API clients
├── orcid_validate.py   # ORCID cross-validation
├── audit.py            # Transparent audit logger
├── phase1.py           # Phase 1: Self-citation baseline
├── phase2.py           # Phase 2: Co-author network
├── phase3.py           # Phase 3: Affiliation matching
├── requirements.txt
├── README.md           # This file
└── audits/             # Auto-generated audit trail files
    ├── baron_..._phase1_20260312_143022.json
    ├── baron_..._phase2_20260312_143044.json
    └── baron_..._phase3_20260312_143155.json
```

---

## Known Limitations

**Incomplete transitive graph (Phase 2).** The co-author graph is built only from the target researcher's publications. Co-author A's other collaborators are invisible unless they also appear on the target's papers. This is a conservative undercount.

**No temporal decay in BARON classification.** A co-author from 15 years ago is treated the same as a current one for BARON (binary in/out). The strength score captures recency and is logged in the audit, but BARON v0.2+ uses binary classification.

**HEROCON weights are experimental.** The graduated weights are informed by intuition, not empirical data. Configurable via `--herocon-weights`. The weights used are always logged in audit files and exports.

**Affiliation data coverage (Phase 3).** OpenAlex work-level affiliations are present for ~75% of recent works, less for older ones. Missing data → UNKNOWN classification (excluded from scores). The reliability rating (HIGH/MODERATE/LOW/VERY LOW) makes this visible.

**Department-level matching is noisy (Phase 3).** ROR lacks department identifiers for most institutions. Heuristic-based matching on raw affiliation strings. When uncertain, defaults conservatively to `SAME_INSTITUTION`.

**ROR coverage (Phase 3).** Smaller or newer institutions may lack ROR IDs. Fallback: raw string matching with lower confidence.

**Affiliation timing gaps (Phase 3).** When neither the citer nor the target has affiliation data near the citation year, the system uses the nearest available data point. Flagged in audit as `temporal_concurrent: null`.

**Dual affiliations (Phase 3).** Researchers with multiple simultaneous affiliations may trigger matches on either. Phase 3 checks all affiliations and keeps the strongest match.

**Author ID quality.** OpenAlex's author disambiguation is imperfect. Cross-referencing with ORCID helps but isn't available for all authors.

---

## Roadmap

- [x] **Phase 1:** Self-citation baseline
- [x] **Phase 2:** Co-author network detection
- [x] **Phase 3:** Affiliation matching (temporal)
- [ ] **Phase 4:** Venue governance detection (AI-driven, local LLM)
- [ ] **Phase 5:** Percentiles, dashboard & API

### What Phase 4 will add

Phase 3's `EXTERNAL` bucket still includes citations from venues where the target researcher or their network holds governance roles. Phase 4 uses a three-repo architecture:

- **[pulsar-helm](https://github.com/citation-cosmograph/pulsar-helm)** 🌟 — Helm chart deploying Qwen 3.5 8B on k8s via llama.cpp. OpenAI-compatible API. CPU-only.
- **[astrolabe](https://github.com/citation-cosmograph/astrolabe)** 🔭 — Venue governance database. Scrapes editorial boards, extracts structured data via pulsar's LLM, resolves entities against OpenAlex. Grows incrementally.
- **phase4.py** (this repo) — Reads astrolabe's database, reclassifies EXTERNAL citations with venue governance overlap.

The signal chain: **pulsar** (LLM) powers **astrolabe** (venue mapping), which feeds **citation-constellation** (scoring).

New classifications: `VENUE_SELF_GOVERNANCE` (0.05), `VENUE_EDITOR_COAUTHOR` (0.15), `VENUE_EDITOR_AFFIL` (0.3), `VENUE_COMMITTEE` (0.4).

---

## API Dependencies

All free and open — no institutional subscription required:

- [OpenAlex](https://openalex.org/) — Primary data source. ~260M works, ~100M authors, ~200K venues, ~2.8B citation links.
- [ORCID Public API](https://orcid.org/) — Author identity validation. Researcher-claimed works list.
- [ROR](https://ror.org/) — Institution hierarchy (Phase 3+). Parent-child relationships.

---

## Disclaimer

This tool is provided as infrastructure for **self-reflection and science policy research**.

> BARON and HEROCON measure citation network structure, not research quality, impact, or integrity. They describe where in the social graph citations originate. They should not be used for hiring, promotion, or funding decisions. See the audit trail for full classification details.

This disclaimer is carried inline with every output — CLI display, JSON export, and audit file.

---

## License

MIT
