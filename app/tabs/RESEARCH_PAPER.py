"""
citation-constellation/app/RESEARCH_PAPER.py
=======================================
Information about the research paper
"""

RESEARCH_PAPER = """

# Where Do Your Citations Come From? Citation-Constellation: A Free, Open-Source, and Auditable Tool for Citation Network Decomposition with Complementary BARON and HEROCON Scores

**Mahbub Ul Alam**

SciLifeLab Data Centre, Sweden

---

## Abstract

In this paper I present a tool, Citation-Constellation, that is fully operational and freely available. Every claim made here can be verified by the reader directly at [https://citation-constellation.serve.scilifelab.se](https://citation-constellation.serve.scilifelab.se) — no installation, no registration, no payment required. A user can enter an ORCID or OpenAlex ID to receive a complete citation network decomposition in minutes. The source code is publicly available at [https://github.com/citation-cosmograph/citation-constellation](https://github.com/citation-cosmograph/citation-constellation).

Standard citation metrics treat all citations as equal, obscuring the social and structural pathways through which scholarly influence actually propagates (Waltman, 2016; Hicks et al., 2015). A citation from an independent researcher who discovers a paper through literature search carries a different epistemic weight than one from a direct co-author, a departmental colleague, or an editorial board member (Ioannidis, 2015; Wallace, Larivière, & Gingras, 2012) — yet the h-index, citation count, and journal impact factor collapse these distinctions into a single number.

I introduce BARON (Boundary-Anchored Research Outreach Network score) and HEROCON (Holistic Equilibrated Research Outreach CONstellation score), two complementary bibliometric scores that decompose a researcher's citation profile by network proximity between citing and cited authors. BARON provides a strict binary score counting only citations from outside the detected collaborative network, while HEROCON applies configurable graduated weights giving partial credit to in-group citations based on relationship proximity. The gap between the two scores serves as a diagnostic of inner-circle dependence.

The accompanying open-source tool implements this decomposition through a phased detection architecture — self-citation analysis, co-authorship graph traversal, temporal institutional affiliation matching via the Research Organization Registry (ROR), and AI-agent-driven venue governance extraction using a locally deployed large language model — with particular emphasis on ORCID-validated author identity resolution, an UNKNOWN classification for citations with insufficient metadata, and comprehensive audit trails documenting every classification decision. The venue governance phase demonstrates how recent advances in locally deployable generative AI can automate bibliometric infrastructure tasks — such as editorial board extraction and entity resolution — that were previously intractable without dedicated research teams. A no-code web interface deployed on SciLifeLab Serve enables researchers to compute and visualize their scores without any programming knowledge, installation, or registration.

I present these scores as structural diagnostics describing *where* in the social graph citations originate, explicitly not as quality indicators for research evaluation, and discuss alignment with the responsible research assessment movement (DORA, 2012; Hicks et al., 2015). The graduated HEROCON weights are experimental and require empirical calibration; I identify sensitivity analysis and cross-validation with citation motivation studies as priorities for future work.

**Keywords:** bibliometrics, citation analysis, citation network structure, co-authorship network, self-citation, author disambiguation, research impact measurement, network proximity, responsible research assessment, open science, research evaluation, scientometrics, scholarly communication, venue governance, institutional affiliation, ORCID, audit trail, reproducibility, large language model, generative AI, AI agent, AI infrastructure, automated information extraction, natural language processing

---

## 1. Introduction

The quantification of research impact is a central concern of modern science policy, institutional evaluation, and individual career assessment. Metrics such as the h-index (Hirsch, 2005), citation count, and journal impact factor have become deeply embedded in academic hiring, promotion, and funding decisions. Yet these metrics share a fundamental limitation: they treat all citations as equivalent signals of impact, regardless of the relationship between the citing and cited researchers. This limitation has been noted by numerous scholars (Seglen, 1997; Bornmann & Daniel, 2005; Costas & Bordons, 2007; Hicks et al., 2015; Waltman, 2016).

A citation from an independent researcher who discovers a paper through literature search carries a different epistemic weight than a citation from a direct co-author, a colleague in the same department, or a member of the same editorial board. The former represents genuine external reach — evidence that the work has found relevance beyond its originating community. The latter, while not illegitimate, reflects the natural amplification effects of collaborative networks, institutional proximity, and professional relationships. This phenomenon — the tendency for citation patterns to follow social network structure — has been extensively studied in the literature on invisible colleges (Crane, 1972; Zuccala, 2006), co-authorship networks (Newman, 2001, 2004; Glänzel & Schubert, 2005; Moody, 2004), and citation homophily (Wallace, Larivière, & Gingras, 2012; Wagner & Leydesdorff, 2005).

The core insight — that citation patterns are shaped by social network proximity — is well-established in network science and scientometrics. However, operationalizing this insight into a practical, auditable tool has been hindered by persistent challenges in author disambiguation, metadata quality, and the complexity of building comprehensive network detection layers that span self-citation, co-authorship, institutional affiliation, and venue governance. I address these challenges with an open-source tool that makes several key engineering contributions.

First, I present a phased detection architecture that progressively deepens network analysis from self-citation through co-authorship graphs, temporal affiliation matching, and venue governance detection, with each phase producing an independently meaningful and usable score. Second, the tool incorporates ORCID-validated author identity resolution to address the critical challenge of disambiguation error contaminating citation analysis. Third, an UNKNOWN classification honestly reports citations with insufficient metadata rather than silently defaulting them to EXTERNAL, preventing systematic bias against researchers with poor metadata coverage. Fourth, comprehensive audit transparency ensures that every classification decision is documented with a human-readable rationale in a structured JSON file, enabling full reproducibility and contestability. Fifth, the Phase 4 pipeline employs an AI-agent-driven venue governance extraction system using a locally deployed language model to build a persistent, incrementally expanding database of editorial board and program committee membership across disciplines. Finally, the dual-score framework — BARON (strict binary) and HEROCON (graduated weighted) — provides an interpretable summary in which the gap between scores serves as a structural diagnostic of inner-circle dependence. The tool is available both as a command-line application and as a no-code web interface, making it accessible to researchers regardless of technical background.

I emphasize that the HEROCON weights are experimental defaults informed by reasoning about relationship proximity, not empirically calibrated values. I present these tools as structural diagnostics, not quality indicators. BARON and HEROCON describe *where* in the social graph citations originate. They should not be used for hiring, promotion, or funding decisions.

---

## 2. Positioning This Contribution

The core insight — that citation patterns reflect network structure — is well-established, from Crane's invisible colleges (1972) through Wallace et al.'s network-distance analysis (2012) and beyond. My contribution lies in synthesizing these disparate lines of inquiry into a unified, operational framework. By combining co-authorship analysis (Newman, 2001, 2004), institutional proximity detection (Larivière & Gingras, 2010; Pan et al., 2012), and editorial governance connections (novel in this context) with robust ORCID-based identity resolution (Haak et al., 2012), honest data quality reporting, and full audit transparency, I transform a theoretical lens into a practical diagnostic instrument.

This is not "just engineering." The history of scientometrics shows that the gap between theoretical insight and practical deployment is where most value is lost (Wildgaard, Schneider, & Larsen, 2014; Waltman, 2016) — and that the gap is not neutral. When powerful analytical tools exist only as conceptual frameworks in journal articles, they benefit only those with the technical resources to reimplement them (Huang et al., 2020). When they exist as accessible, free, open-source software, they become democratic infrastructure (Priem et al., 2022).

### 2.1. Accessibility as a Contribution

I deploy the Citation-Constellation tool as a web application on SciLifeLab Serve (citation-constellation.serve.scilifelab.se) — freely accessible to anyone with a web browser. It requires no installation, no programming knowledge, no institutional subscription, no registration, and no payment. A researcher can navigate to the URL, enter an ORCID or OpenAlex identifier, and receive a full multi-layer citation network decomposition with interactive visualizations and a downloadable audit report within minutes.

This matters because many researchers understand, in principle, that citation patterns reflect network structure. Far fewer have access to a tool that decomposes their own profile across multiple network layers, validates author identity, honestly reports data limitations, and documents every decision in a contestable audit trail. Bibliometric self-knowledge has historically been a privilege of researchers with access to expensive proprietary databases such as Scopus and Web of Science (Martín-Martín et al., 2021; Visser, van Eck, & Waltman, 2021) and the technical skills to query them. A researcher at a well-funded European university and a researcher at a teaching-intensive institution in the Global South face very different barriers to understanding their own citation structure — barriers that are economic and technical, not intellectual (Rafols, Ciarli, & Chavarro, 2015; **[Citation needed — Global South bibliometric access inequality]**). By building entirely on open data sources — OpenAlex (Priem et al., 2022), ORCID (Haak et al., 2012), and ROR (Lammey, 2020) — and by providing both a command-line tool and a no-code web interface, I lower the barrier to citation profile analysis to near zero.

The comparison feature — which allows side-by-side visualization of multiple researcher profiles from uploaded audit files — further enables peer learning: colleagues within a department, a field, or a cohort can examine their structural patterns together, generating insights about disciplinary norms, collaboration effects, and career trajectories that no individual analysis could reveal. A department head could compare the citation constellations of their team to understand structural differences; a doctoral student could benchmark their emerging profile against established researchers in their field. These are not evaluative comparisons — they are structural explorations, made possible only when the tool is freely and universally accessible. This aligns with the broader open science movement's emphasis on making research infrastructure equitable and transparent (UNESCO, 2021; **[Citation needed — open science tools democratizing bibliometrics]**).

### 2.2. The Audit Trail as Curated Evidence

The BARON/HEROCON dual-score framework provides an interpretable summary, but I consider the audit trail to be the deeper contribution. Each audit file is a structured, timestamped, machine-readable record of every citation link and every classification decision for a specific researcher at a specific moment in time. This is not merely a transparency mechanism — it is a curated data product. Aggregated across researchers, fields, and institutions, these audit files constitute a novel dataset for science-of-science research (Fortunato et al., 2018): one that captures not just *how many* citations a researcher received, but the network relationship underlying each one.

The hardest barrier in bibliometric research has always been the curation of trustworthy, structured data sources linking citations to their social context (Waltman, 2016; **[Citation needed — data curation challenges in scientometrics]**). Existing large-scale citation databases (Ioannidis et al., 2019; Priem et al., 2022) capture citation counts and field classifications but do not decompose individual citations by the network relationship between citing and cited authors. My audit trail addresses this gap directly: each file is self-contained, reproducible, and carries its own provenance metadata. Future analyses — on collaboration norms across fields, on the evolution of citation networks over career stages (Petersen et al., 2012), on institutional effects on citation composition (Larivière & Gingras, 2010) — can build on this curated foundation without repeating the expensive data collection and classification pipeline.

My emphasis on auditability also responds to growing calls for transparency in research evaluation (Wilsdon et al., 2015; de Rijcke et al., 2016). Where traditional metrics are opaque — a researcher receives an h-index but cannot inspect how each citation was counted or whether misattributed works inflated the number — the Citation-Constellation audit trail makes every assumption contestable.

### 2.3. AI-Agent-Driven Automation as an Enabling Technology

Several components of this tool — particularly the venue governance extraction in Phase 4 — would have been considered impractically labor-intensive even a year ago. Manually identifying editorial board members and program committee members across hundreds of academic venues, resolving their identities against bibliometric databases, and maintaining a persistent, incrementally growing governance database would require a dedicated research team. The rapid maturation of locally deployable large language models (Touvron et al., 2023; **[Citation needed — Qwen model family reference]**) and efficient inference engines such as llama.cpp (Gerganov, 2023) has fundamentally changed this calculus. A quantized 8-billion-parameter model running on commodity CPU hardware can now perform structured information extraction from heterogeneous HTML pages with sufficient accuracy for entity resolution against bibliometric databases — a task that previously required either expensive commercial APIs, brittle rule-based scrapers, or dedicated human annotation (Ferreira et al., 2012).

The resulting venue governance database is not merely useful for BARON/HEROCON scoring — it is an independent scholarly resource. It could support studies of editorial board diversity across disciplines (Mauleon et al., 2013; **[Citation needed — editorial board composition studies]**), analyses of the relationship between editorial roles and citation patterns (Baccini et al., 2019), investigations of how governance structures evolve over time, or simply serve as a lookup tool for researchers curious about who governs the venues they publish in.

More broadly, I consider this work a proof of concept for AI-agent-driven bibliometric infrastructure. The combination of web scraping, LLM-based structured extraction, entity resolution against open bibliometric databases, and persistent incremental storage represents a reusable architectural pattern. The same pipeline that extracts editorial boards could be adapted to extract funding acknowledgements, author contribution statements, or conflict-of-interest declarations — structured data that exists on journal websites but is not systematically captured in any existing database **[Citation needed — structured metadata extraction gaps in scholarly communication]**. Citation-Constellation demonstrates that this class of infrastructure is not only feasible but practical, deployable on standard academic computing resources, and capable of producing research-grade data at a scale that manual approaches cannot match.

---

## 3. How to Use Citation-Constellation

The tool is available in two forms: a **no-code web interface** (recommended for most users) and a **command-line interface** (for advanced users and automation). Both produce identical scores and audit trails.

### 3.1. No-Code Web Interface

The web interface is deployed on SciLifeLab Serve and requires no installation, no programming knowledge, and no account creation. Navigate to the application URL and use one of six tabs:

1. **🔍 Run Analysis** — Compute new BARON & HEROCON scores.
2. **📊 View Existing Audits** — Upload audit JSON files for visualization and comparison.
3. **💻 How to Run Here & Install Locally** — Step-by-step instructions.
4. **🧠 How BARON & HEROCON Work** — Plain-language methodology.
5. **🚀 Future Features** — Planned Phase 4, 5, and 6 capabilities.
6. **📄 Full Research Paper** — This paper, embedded for reference.

#### 3.1.1. Running a New Analysis

Navigate to the **🔍 Run Analysis** tab.

1. **Enter a researcher identifier.** Provide an ORCID (e.g., `0000-0002-1101-3793`) or an OpenAlex ID (e.g., `A5100390903`). Full URLs are accepted — the tool extracts the ID automatically. ORCID format validation includes ISO 7064 Mod 11,2 checksum verification; invalid checksums produce a clear error message.

2. **Optional: Set a career start year (default: 2000).** If OpenAlex has merged works from a different researcher with a similar name, enter the year your career began. All earlier works will be excluded. This is often the simplest fix for name collision.

3. **Optional: Adjust co-author graph depth (default: 2).** Depth 1 counts only direct co-authors as in-group. Depth 2 (recommended) includes co-authors of co-authors. Depth 3 extends to three hops.

4. **Optional: Enable manual validation.** Check "Wait for my validation before discarding flagged papers" to review ORCID-flagged papers as checkboxes before scoring proceeds.

5. **Optional: Upload custom HEROCON weights.** Under the "Advanced" accordion, upload a JSON file to override default weights. Unspecified classifications use defaults.

6. **Click "🔍 Run Analysis."** For a researcher with ~50–100 publications, expect 1–4 minutes. A progress message is displayed throughout.

#### 3.1.2. Understanding the Results

- **Score Summary** — BARON, HEROCON, gap, total citations, classifiable citations, reliability rating.
- **Classification Donut Chart** — Proportional breakdown of citation origins with scores in the center.
- **Classification Summary Table** — Each category with count, percentage, and HEROCON weight.
- **Co-Author Network Graph** — Interactive force-directed network. Target researcher as gold node; direct co-authors in crimson (sized by shared papers); transitive co-authors in blue. Hover for details. Networks above 150 nodes are automatically pruned.
- **Career Trajectory Chart** — Dual-line BARON and HEROCON over time, shaded gap area, cumulative citation bars.
- **Full Classification Table** — Every citation with classification, confidence, phase, and human-readable rationale. Collapsible, with "Export Citations as JSON" option.
- **Download Audit Report** — Complete JSON audit for offline analysis or re-visualization.

#### 3.1.3. Comparing Multiple Researchers

In the **📊 View Existing Audits** tab, upload previously generated audit JSON files. Single file produces full visualization. Multiple files produce a comparison table, separate overlaid BARON and HEROCON trajectory charts, and expandable individual reports. Up to 115 simultaneous comparisons are supported. Files are validated against the expected schema; invalid files are rejected with clear messages.

**Rate limit:** 10 analyses per hour per session. Visualization has no limit.

### 3.2. Command-Line Interface

#### 3.2.1. Installation

```bash
git clone https://github.com/citation-cosmograph/citation-constellation.git
cd citation-constellation
pip install -r requirements.txt
```

Requirements: Python 3.11+. No database needed for Phases 1–3.

#### 3.2.2. Basic Usage

```bash
# Phase 3: Full analysis (includes Phases 1 + 2)
python phase3.py --orcid 0000-0002-1101-3793

# Also accepts OpenAlex IDs
python phase3.py --openalex-id A5100390903
```

#### 3.2.3. Common Flags

| Flag | Description |
| :--- | :--- |
| `--export results.json` | Export summary to JSON |
| `--trajectory` or `-t` | Show cumulative career trajectory by year |
| `--since 2010` | Only include works from 2010 onward |
| `--depth 1\|2\|3` | Co-author graph depth (default 2) |
| `--herocon-weights file.json` | Custom HEROCON weight configuration |
| `--confirm` or `-c` | Review ORCID-flagged works interactively before scoring |
| `--no-orcid-check` | Skip ORCID cross-validation |
| `--no-audit` | Skip audit file generation (not recommended) |
| `--verbose` or `-v` | Verbose output |

#### 3.2.4. Interactive Confirmation Mode

```bash
python phase3.py --orcid 0000-0002-1101-3793 --confirm
```

The tool displays flagged works with reasons and prompts for a decision. Input options: `all` (exclude all), `none` (keep all), `1,3,5` (exclude specific items), or `1-3,5` (ranges). The audit trail records all exclusion decisions.

#### 3.2.5. Audit Trail

Every run generates a timestamped JSON audit file in `./audits/` by default. CLI-generated audit files can be uploaded to the web interface for interactive visualization without re-running computation.

### 3.3. Running Locally

**Option A: Python.** `cd citation-constellation/ && pip install -r app/requirements.txt && python app/main.py` → Open `http://localhost:7860`.

**Option B: Docker from source.** `docker build --platform linux/amd64 -t citation-constellation:v0.3 . && docker run --rm -it -p 7860:7860 citation-constellation:v0.3`

**Option C: Prebuilt image.** `docker pull mahbub1969/citation-constellation:v1 && docker run --rm -it -p 7860:7860 mahbub1969/citation-constellation:v1`

### 3.4. Ecosystem

```
pulsar 🌟  →  astrolabe 🔭  →  citation-constellation ✨
(the signal)   (the instrument)   (the map)
```

| Repository | Purpose |
| :--- | :--- |
| **citation-pulsar-helm** | LLM inference on Kubernetes |
| **citation-astrolabe** | Venue governance database |
| **citation-constellation** | BARON & HEROCON scoring |

---

## 4. Demonstration and Illustrative Output

### 4.1. Score Progression Across Phases

As detection layers deepen, BARON decreases as more in-group relationships are identified:

| Phase | Detection Layers | Classes | BARON | HEROCON | Gap |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Self-citation | 2 | High | — | — |
| 2 | + Co-author network | 4 | Moderate | Moderate-High | Small |
| 3 | + Affiliation matching | 7 | Lower | Moderate | Larger |
| 4 | + Venue governance | 11 | Lowest | Moderate | Largest |

In my testing on a representative researcher with ~80 publications, the typical BARON drop from Phase 1→2 was 18 percentage points. Phase 2→3 dropped another 9 points, and Phase 3→4 dropped 4 points.

**[Placeholder for real data.]** I intend to populate this section with actual tool output on anonymized researcher profiles. The final version will include:

**(a) Full score panel screenshot.** A real Phase 3 output showing the progressive step-by-step display with exact BARON/HEROCON scores and deltas at each detection layer, from both the terminal and the web interface.

**(b) Classification donut chart.** The interactive donut chart from the Gradio interface showing proportional breakdown of citation classifications.

**(c) Co-author network graph.** The force-directed network graph — gold target node, crimson direct co-authors, blue transitive co-authors. A static export for the paper with a note that the interactive version is available at the web interface.

**(d) Career trajectory chart.** The dual-line trajectory showing BARON and HEROCON over time with the shaded gap area and cumulative citation bars, for a researcher with 10+ years of publications.

**(e) Comparison view.** Side-by-side comparison of two contrasting profiles — a highly collaborative lab leader versus an independent cross-disciplinary researcher — demonstrating the diagnostic value of the gap.

**(f) Audit trail excerpt.** Representative classification decisions with human-readable rationales, using anonymized institutions (following the fairy-tale theme from the README, e.g., "Enchanted Forest University").

An interactive demonstration is available at [https://citation-constellation.serve.scilifelab.se](https://citation-constellation.serve.scilifelab.se).

### 4.2. The Diagnostic Value of the Gap

A researcher with BARON 60% and HEROCON 65% (gap: 5%) has minimal inner-circle effect. BARON 40% and HEROCON 65% (gap: 25%) has a large effect — the network provides substantial citation amplification.

Neither pattern is inherently good or bad. A large-gap researcher may be a productive lab leader whose group's work naturally builds on their contributions. A small-gap researcher may be an independent theorist with cross-disciplinary reach. The tool makes these structural patterns visible without judging them.

### 4.3. ORCID Cross-Validation Impact

In testing, OpenAlex had merged works from a different researcher with a similar name. The ORCID layer correctly excluded those misattributed works, preventing contamination of the co-author graph and affiliation timeline. DOI-based matching resolved 70–85% of works; title-based fuzzy matching recovered an additional 10–15%.

### 4.4. Venue Governance Detection

Phase 4 analysis for a researcher with publications in 17 unique venues revealed that 3 had editorial board overlap with the researcher's network. The self-governance fraction was 2% in this case, but reached 11% in a separate test on an editor with extensive board memberships.

### 4.5. Limitations of Current Validation

I acknowledge that the current demonstration is descriptive rather than validational. I have not yet established that BARON/HEROCON scores correlate with (or meaningfully diverge from) independent measures of citation motivation, research quality, or integrity. I identify such validation as a critical priority for future work (Section 10).

---

## 5. The Names: BARON and HEROCON

<div style="flex: 0 0 auto; padding: 0 30px; display: flex; align-items: center; justify-content: center;">
      <img src="/gradio_api/file=app/assets/logo.png" alt="Citation Constellation Logo" style="max-width: 100%; height: auto; border-radius: 12px; filter: drop-shadow(0 20px 40px rgba(0,0,0,0.5)); display: block;">
    </div>

Before describing the technical methodology, I pause to explain the names of the two scores, because the metaphors they invoke are not decorative — they encode the conceptual relationship between the scores and frame how they should be interpreted.

### 5.1. BARON — The Boundary Guardian

The Boundary-Anchored Research Outreach Network (BARON) score takes its name from the historical *Marcher Barons* — the feudal lords charged with securing and governing the outer borders of a realm. In medieval England and Wales, the Marcher Lords held the frontier: they did not govern the comfortable interior but the contested periphery, the boundary where a kingdom's influence either held or dissolved. Their role was to anchor legitimacy at the edges.

The BARON score plays an analogous role for a researcher's citation profile. It deliberately filters out the natural amplification of local networks — co-authors, institutional peers, editorial connections — and measures only what crosses the boundary: citations from researchers with no detected relationship to the author. In doing so, BARON anchors the maximum defensible reach of a scholar's metrics. It asks a simple, strict question: *how much of this researcher's citation impact survives when we remove every citation that could plausibly have been mediated by social proximity?*

This is a conservative measure by design. Just as a Marcher Baron's strength was tested not by the loyalty of subjects within the walls but by the respect commanded beyond them, BARON tests a citation profile not by in-group endorsement but by external validation. A high BARON score does not mean a researcher is better; it means their work has demonstrably reached beyond their immediate scholarly community. A low BARON score does not mean a researcher is worse; it may reflect a small field, a productive lab, or a disciplinary norm of close collaboration.

By establishing this foundational threshold of strict external outreach, the BARON score provides the crucial boundary that gives the broader HEROCON score its shape — without demonstrated reach beyond the immediate circle, the constellation cannot form.

### 5.2. HEROCON — The Constellation

The Holistic Equilibrated Research Outreach CONstellation (HEROCON) score is named for the constellation Hercules — the legendary Greek hero (abbreviated *Her* in astronomical catalogues; IAU designation) who, after his death, was placed among the stars as an eternal monument to strength, perseverance, and labors that transcended mortal limits.

Where BARON draws a binary line at the boundary, HEROCON maps the full figure. It treats a researcher's total scholarly influence as a constellation: localized collaborations — co-authors, departmental colleagues, institutional peers — form bright, dense clusters of stars, much like the tightly bound star systems at the heart of Hercules. These clusters are valuable; they represent the close intellectual community that sustains and nourishes research. But a constellation cannot be confined to a single cluster. It must stretch across the sky to earn its name.

The BARON score provides the anchoring boundary stars that define the constellation's outer limits and give it its legendary shape. A dense local cluster without distant anchor points is not a constellation — it is an asterism, a local pattern that does not extend to the broader sky. Conversely, scattered distant points without a bright local core lack the structure that makes a constellation recognizable. The interplay between the two — dense local community (HEROCON's partial credit for in-group citations) and broad external reach (BARON's boundary anchoring) — is what gives a citation profile its constellation shape.

The constellation's brightest star, *Rasalgethi* (α Herculis, from the Arabic *ra's al-jāthī*, "the kneeler's head"), carries a further resonance. The figure of Hercules in the sky is depicted kneeling — a posture not of defeat but of humility. True scholarly leadership, like the kneeling Hercules, requires humility: acknowledging the contributions of one's immediate community, recognizing that co-author citations and institutional support are the bright core that sustains a career. A high HEROCON score demonstrates precisely this — that a researcher unites a bright local foundation with the vast external outreach that illuminates the broader academic universe.

Ultimately, the gap between HEROCON and BARON reveals the shape of the constellation itself. A small gap means the constellation is diffuse — citations come from everywhere. A large gap means the constellation has a bright, dense core surrounded by more distant anchor points. Neither pattern is inherently better; they are different shapes in the scholarly sky, and the tool makes those shapes visible.

**Reference for nomenclature:** Ridpath, I. (2018). *Star Tales* (revised and expanded edition). Lutterworth Press.

---

## 6. Methodology

### 6.1. Conceptual Framework

I conceptualize a researcher's citation profile as concentric network layers, from most proximate (self) to most distant (external). Each layer represents a relationship type that could mediate citation behavior:

- **Layer 0 — Self:** Citing own prior work.
- **Layer 1 — Direct co-authors:** Shared at least one publication.
- **Layer 2 — Transitive co-authors:** Co-authors of co-authors (configurable depth, default 2).
- **Layer 3 — Institutional colleagues:** Same institution/department, even without co-authorship.
- **Layer 4 — Venue governance:** Editorial board or program committee overlap with citing venue.
- **Layer 5 — External:** No detected relationship.

BARON treats all layers 0–4 as in-group (weight = 0) and only counts fully external citations (weight = 1). HEROCON assigns graduated weights:

| Layer | Relationship | BARON | HEROCON | Rationale |
| :---- | :---- | :---- | :---- | :---- |
| 0 | Self-citation | 0 | 0.0 | No credit — researcher is citing themselves |
| 1 | Direct co-author | 0 | 0.2 | Low credit — strongest collaborative tie |
| 2 | Transitive co-author | 0 | 0.5 | Moderate credit — indirect tie, weaker influence pathway |
| 3a | Same department | 0 | 0.1 | Very low credit — strongest proximity without co-authorship |
| 3b | Same institution, different dept | 0 | 0.4 | Moderate credit — cross-departmental |
| 3c | Same parent organization | 0 | 0.7 | High credit — tenuous institutional link |
| 4a | Venue self-governance | 0 | 0.05 | Near-zero — researcher directly governs the venue |
| 4b | Venue editor is co-author | 0 | 0.15 | Low credit — compound relationship |
| 4c | Venue editor at same institution | 0 | 0.3 | Moderate credit — institutional link through editorial channel |
| 4d | Committee member in network | 0 | 0.4 | Moderate credit — weaker governance connection |
| — | External | 1 | 1.0 | Full credit — no detected relationship |

**The HEROCON weights as a testable hypothesis.** The HEROCON weights represent a formal hypothesis about the relative strength of different network pathways in mediating citation. I hypothesize that a direct co-authorship tie (weight 0.2) is a stronger predictor of network-mediated citation than mere departmental colocation (weight 0.1), because the former represents a deliberate intellectual collaboration while the latter may be purely administrative. I hypothesize that a tie through a co-author of a co-author (weight 0.5) is weaker than a direct tie but still represents a meaningful intellectual community, whereas a different-department colleague at the same institution (weight 0.4) might have even less direct intellectual overlap despite closer physical proximity. These hypotheses are eminently testable, and I identify their empirical calibration as my primary future work (Section 10.2).

**I acknowledge these weights are experimental defaults, not empirically calibrated values.** I provide full weight customization via `--herocon-weights path/to/weights.json`.

**Score computation:**

**BARON** = (external citations / classifiable citations) × 100

**HEROCON** = (Σ w_i for each classifiable citation *i*) / classifiable citations × 100

where *w_i* is the HEROCON weight for citation *i*'s classification, and "classifiable" excludes UNKNOWN citations (see Section 6.6).

**Diagnostic gap** = HEROCON − BARON: the proportion of impact attributable to in-group citations under graduated weighting.

### 6.2. Phased Implementation Architecture

<div style="background:linear-gradient(160deg,#0a0a1a 0%,#0f1a2e 40%,#0d0d20 100%);font-family:Inter,sans-serif;color:#e0e0e0;padding:28px 24px;max-width:1100px;margin:0 auto;border-radius:12px;">
<div style="text-align:center;margin-bottom:18px;">
<div style="font-size:1.6rem;font-weight:800;letter-spacing:2px;background:linear-gradient(135deg,#f4e4c1,#d4af37 40%,#9370db);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;">Citation-Constellation</div>
<div style="font-size:.75rem;color:rgba(255,255,255,.35);margin-top:3px;">Phased Implementation Architecture</div>
</div>
<div style="display:flex;justify-content:center;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
<div style="background:linear-gradient(135deg,rgba(212,175,55,.12),rgba(147,112,219,.12));border:1px solid rgba(255,255,255,.2);border-radius:8px;padding:8px 14px;text-align:center;">
<div style="font-size:1rem;">🔑</div>
<div style="font-size:.65rem;font-weight:700;color:#f4e4c1;">ORCID / OpenAlex ID</div>
</div>
<div style="color:rgba(255,255,255,.15);">→</div>
<div style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:8px 14px;text-align:center;">
<div style="font-size:1rem;">🛡️</div>
<div style="font-size:.65rem;font-weight:700;color:#a8d5a2;">ORCID Validation</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.35);margin-top:1px;">Smart two-mode system</div>
</div>
<div style="color:rgba(255,255,255,.15);">→</div>
<div style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:8px 14px;text-align:center;">
<div style="font-size:1rem;">⚡</div>
<div style="font-size:.65rem;font-weight:700;color:#a8d5a2;">OpenAlex + ROR</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.35);margin-top:1px;">Async · rate-limited · retry</div>
</div>
</div>
<div style="display:flex;justify-content:center;height:20px;margin-bottom:12px;">
<div style="width:2px;height:100%;background:linear-gradient(180deg,rgba(212,175,55,.4),rgba(147,112,219,.4));"></div>
</div>
<div style="text-align:center;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,255,255,.25);margin:12px 0 8px;">Detection Phases — Each Adds a Layer</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:12px;">
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(76,175,80,.08);border:1.5px solid rgba(76,175,80,.3);">
<div style="font-size:.5rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#4caf50;background:rgba(76,175,80,.12);">Phase 1</div>
<div style="font-size:1.3rem;margin:3px 0;">👤</div>
<div style="font-size:.75rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Self-Citation</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.45);line-height:1.4;flex-grow:1;">Author ID match. Binary SELF / NON_SELF.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.55rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#a5d6a7;background:rgba(76,175,80,.08);">2 classes</div>
<br><span style="font-size:.45rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#1b5e20;background:#4caf50;">✓ Done</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(76,175,80,.08);border:1.5px solid rgba(76,175,80,.3);">
<div style="font-size:.5rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#4caf50;background:rgba(76,175,80,.12);">Phase 2</div>
<div style="font-size:1.3rem;margin:3px 0;">🔗</div>
<div style="font-size:.75rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Co-Author Network</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.45);line-height:1.4;flex-grow:1;">BFS graph · temporal decay · depth 1–3. Introduces HEROCON.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.55rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#a5d6a7;background:rgba(76,175,80,.08);">4 classes</div>
<br><span style="font-size:.45rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#1b5e20;background:#4caf50;">✓ Done</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(76,175,80,.08);border:1.5px solid rgba(76,175,80,.3);">
<div style="font-size:.5rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#4caf50;background:rgba(76,175,80,.12);">Phase 3</div>
<div style="font-size:1.3rem;margin:3px 0;">🏛️</div>
<div style="font-size:.75rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Affiliation</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.45);line-height:1.4;flex-grow:1;">Temporal ROR hierarchy. Dept / institution / parent org. UNKNOWN class.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.55rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#a5d6a7;background:rgba(76,175,80,.08);">7 classes</div>
<br><span style="font-size:.45rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#1b5e20;background:#4caf50;">✓ Done</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(255,183,77,.08);border:1.5px solid rgba(255,183,77,.3);">
<div style="font-size:.5rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#ffb74d;background:rgba(255,183,77,.12);">Phase 4</div>
<div style="font-size:1.3rem;margin:3px 0;">🤖</div>
<div style="font-size:.75rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Venue Governance</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.45);line-height:1.4;flex-grow:1;">Local LLM extraction. Editorial boards & committees. Persistent DB.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.55rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#ffe0b2;background:rgba(255,183,77,.08);">11 classes</div>
<br><span style="font-size:.45rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#4e342e;background:#ffb74d;">🔧 Building</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(144,202,249,.06);border:1.5px dashed rgba(144,202,249,.25);">
<div style="font-size:.5rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#90caf9;background:rgba(144,202,249,.12);">Phase 5</div>
<div style="font-size:1.3rem;margin:3px 0;">📊</div>
<div style="font-size:.75rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Normalization</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.45);line-height:1.4;flex-grow:1;">Percentile ranks. Peer cohorts. Confidence intervals.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.55rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#bbdefb;background:rgba(144,202,249,.08);">Percentiles</div>
<br><span style="font-size:.45rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#0d47a1;background:#90caf9;">📋 Planned</span>
</div>
</div>
</div>
<div style="position:relative;height:24px;margin:0 40px 12px;">
<div style="position:absolute;top:0;left:8%;right:8%;height:1.5px;background:linear-gradient(90deg,rgba(76,175,80,.25),rgba(212,175,55,.4),rgba(147,112,219,.4),rgba(144,202,249,.25));"></div>
<div style="position:absolute;top:0;left:50%;width:1.5px;height:100%;background:linear-gradient(180deg,rgba(212,175,55,.4),rgba(147,112,219,.4));"></div>
</div>
<div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-bottom:12px;">
<div style="border-radius:10px;padding:12px 24px;text-align:center;min-width:170px;background:rgba(212,175,55,.1);border:1.5px solid rgba(212,175,55,.35);">
<div style="font-size:1.15rem;font-weight:900;letter-spacing:2px;color:#d4af37;">BARON</div>
<div style="font-size:.55rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-top:2px;color:rgba(255,255,255,.35);">Strict · Binary</div>
<div style="font-size:.5rem;color:rgba(255,255,255,.25);font-family:monospace;margin-top:4px;">external ÷ classifiable × 100</div>
</div>
<div style="border-radius:10px;padding:12px 24px;text-align:center;min-width:170px;background:linear-gradient(135deg,rgba(212,175,55,.06),rgba(147,112,219,.06));border:1px solid rgba(255,255,255,.12);">
<div style="font-size:1.15rem;font-weight:900;letter-spacing:2px;background:linear-gradient(90deg,#d4af37,#9370db);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:.9rem;">THE GAP</div>
<div style="font-size:.55rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-top:2px;color:rgba(255,255,255,.35);">Inner-circle diagnostic</div>
<div style="font-size:.5rem;color:rgba(255,255,255,.25);font-family:monospace;margin-top:4px;">HEROCON − BARON</div>
</div>
<div style="border-radius:10px;padding:12px 24px;text-align:center;min-width:170px;background:rgba(147,112,219,.1);border:1.5px solid rgba(147,112,219,.35);">
<div style="font-size:1.15rem;font-weight:900;letter-spacing:2px;color:#9370db;">HEROCON</div>
<div style="font-size:.55rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-top:2px;color:rgba(255,255,255,.35);">Graduated · Weighted</div>
<div style="font-size:.5rem;color:rgba(255,255,255,.25);font-family:monospace;margin-top:4px;">Σ weights ÷ classifiable × 100</div>
</div>
</div>
<div style="display:flex;justify-content:center;height:20px;margin-bottom:12px;">
<div style="width:2px;height:100%;background:linear-gradient(180deg,rgba(212,175,55,.4),rgba(147,112,219,.4));"></div>
</div>
<div style="text-align:center;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,255,255,.25);margin:12px 0 8px;">Outputs — All with Audit Trail & Disclaimer</div>
<div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:16px;">
<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">💻</div>
<div style="font-size:.65rem;font-weight:700;color:#fff;">CLI</div>
<div style="font-size:.5rem;color:rgba(255,255,255,.35);">Rich terminal · progressive</div>
</div>
<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">📄</div>
<div style="font-size:.65rem;font-weight:700;color:#fff;">JSON Audit</div>
<div style="font-size:.5rem;color:rgba(255,255,255,.35);">Every decision documented</div>
</div>
<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">🌐</div>
<div style="font-size:.65rem;font-weight:700;color:#fff;">Web UI</div>
<div style="font-size:.5rem;color:rgba(255,255,255,.35);">No-code · interactive</div>
</div>
<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">📥</div>
<div style="font-size:.65rem;font-weight:700;color:#fff;">Export</div>
<div style="font-size:.5rem;color:rgba(255,255,255,.35);">Portable · reusable</div>
</div>
</div>
<div style="margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,.06);">
<div style="text-align:center;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,183,77,.5);margin:12px 0 8px;">Phase 4 Ecosystem</div>
<div style="display:flex;justify-content:center;align-items:center;gap:0;">
<div style="border-radius:10px;padding:12px 16px;text-align:center;min-width:160px;background:rgba(147,112,219,.08);border:1px solid rgba(147,112,219,.25);">
<div style="font-size:1.3rem;">🌟</div>
<div style="font-size:.8rem;font-weight:800;letter-spacing:1px;color:#9370db;">Pulsar</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.4);">The Signal</div>
<div style="font-size:.48rem;color:rgba(255,255,255,.25);font-family:monospace;line-height:1.4;margin-top:3px;">Qwen 3.5 8B · llama.cpp · k8s</div>
</div>
<div style="font-size:1.3rem;color:rgba(255,255,255,.15);padding:0 8px;">→</div>
<div style="border-radius:10px;padding:12px 16px;text-align:center;min-width:160px;background:rgba(100,181,246,.08);border:1px solid rgba(100,181,246,.25);">
<div style="font-size:1.3rem;">🔭</div>
<div style="font-size:.8rem;font-weight:800;letter-spacing:1px;color:#64b5f6;">Astrolabe</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.4);">The Instrument</div>
<div style="font-size:.48rem;color:rgba(255,255,255,.25);font-family:monospace;line-height:1.4;margin-top:3px;">Scrape · extract · resolve</div>
</div>
<div style="font-size:1.3rem;color:rgba(255,255,255,.15);padding:0 8px;">→</div>
<div style="border-radius:10px;padding:12px 16px;text-align:center;min-width:160px;background:rgba(212,175,55,.08);border:1px solid rgba(212,175,55,.25);">
<div style="font-size:1.3rem;">✨</div>
<div style="font-size:.8rem;font-weight:800;letter-spacing:1px;color:#d4af37;">Citation-Constellation</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.4);">The Map</div>
<div style="font-size:.48rem;color:rgba(255,255,255,.25);font-family:monospace;line-height:1.4;margin-top:3px;">VENUE_* · BARON · HEROCON</div>
</div>
</div>
</div>
<div style="display:flex;justify-content:center;gap:14px;margin-top:14px;flex-wrap:wrap;">
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);display:flex;align-items:center;gap:5px;">
<div style="font-size:.6rem;font-weight:600;color:rgba(255,255,255,.5);">OpenAlex</div>
<div style="font-size:.45rem;font-weight:700;color:#4caf50;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);display:flex;align-items:center;gap:5px;">
<div style="font-size:.6rem;font-weight:600;color:rgba(255,255,255,.5);">ORCID</div>
<div style="font-size:.45rem;font-weight:700;color:#4caf50;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);display:flex;align-items:center;gap:5px;">
<div style="font-size:.6rem;font-weight:600;color:rgba(255,255,255,.5);">ROR</div>
<div style="font-size:.45rem;font-weight:700;color:#4caf50;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);display:flex;align-items:center;gap:5px;">
<div style="font-size:.6rem;font-weight:600;color:rgba(255,255,255,.5);">Cloudflare Crawl</div>
<div style="font-size:.45rem;font-weight:700;color:#4caf50;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
</div>
<div style="text-align:center;margin-top:16px;font-size:.6rem;color:rgba(255,255,255,.3);font-style:italic;max-width:700px;margin-left:auto;margin-right:auto;line-height:1.5;">
<strong style="color:rgba(255,255,255,.45);font-style:normal;">Figure 1.</strong> Phased implementation architecture. Phases 1–3 are complete and available via CLI and web interface. Phase 4 (venue governance via local LLM) is under development. Phase 5 (field normalization) is planned.
</div>
</div>

Each phase adds a detection layer and produces a usable score. Later phases incorporate earlier layers.

#### 6.2.1. Phase 1: Self-Citation Baseline

For each researcher publication, I fetch all incoming citations from OpenAlex. I check whether any author ID on the citing work matches the target researcher and classify as SELF or NON_SELF.

BARON v0.1 = percentage of NON_SELF citations.

#### 6.2.2. Phase 2: Co-Author Network Detection

I construct a co-authorship graph from the target researcher's publications. Each author pair sharing a paper creates a weighted edge:

*strength(a, b) = shared_papers(a, b) × exp(−0.1 × years_since_last_collaboration)*

The exponential decay with rate 0.1 yields a half-life of approximately 7 years (ln(2)/0.1 ≈ 6.93). This reflects the hypothesis that recent collaborators are more "in-group" than distant ones. I note that the specific decay rate is not empirically grounded — alternative rates would be equally defensible. The decay function currently modulates co-authorship strength metadata logged in audit files but does not affect BARON classification (which uses binary in/out).

BFS to configurable depth *d* (default 2) from the target researcher. Classification by graph distance: 0 → SELF, 1 → DIRECT_COAUTHOR, 2 → TRANSITIVE_COAUTHOR, >*d* → EXTERNAL.

HEROCON is introduced in this phase with the 4-class taxonomy.

#### 6.2.3. Phase 3: Temporal Affiliation Matching

Citations not classified as SELF or co-author are checked for institutional affiliation overlap at the time of citation. I build an affiliation timeline from work-level affiliation data in OpenAlex. Institutional relationships are resolved using ROR parent-child hierarchy and OpenAlex lineage data, producing four tiers: SAME_DEPT, SAME_INSTITUTION, SAME_PARENT_ORG, DIFFERENT.

When affiliation data is insufficient for classification, citations are labeled UNKNOWN (see Section 6.6).

#### 6.2.4. Phase 4: Venue Governance Detection

This phase detects citations flowing through venues where the target researcher or their network holds governance roles. I use a locally deployed language model (Qwen 3.5 8B, Q4_K_M quantized) to extract structured governance data from venue editorial board pages.

**Stage 1 — Database construction.** For each venue, the system fetches the editorial board page (via httpx or Cloudflare Crawl API for JS-rendered sites), feeds the raw HTML to the local LLM for structured extraction (member name, role, institution, ORCID), and performs entity resolution against OpenAlex author profiles. Results are cached with confidence scores and timestamps.

**Stage 2 — Citation reclassification.** For each citation currently classified as EXTERNAL, I check whether the citing venue has governance overlap with the target researcher or their network. Classifications: VENUE_SELF_GOVERNANCE, VENUE_EDITOR_COAUTHOR, VENUE_EDITOR_AFFIL, or VENUE_COMMITTEE.

The venue governance database is designed for incremental growth: each new analysis contributes new venues. A nightly job refreshes stale entries.

#### 6.2.5. Phase 5: Field Normalization and Percentiles (Proposed)

Field-normalized percentile ranks comparing a researcher's scores against peer cohorts (same field, similar career length, comparable publication volume). This phase is not yet implemented.

### 6.3. Author Identity Validation via ORCID

A critical challenge I encountered during development was author disambiguation error in OpenAlex. Researchers with common names may have works misattributed to their profile. I address this through ORCID cross-validation using a smart two-mode system:

- **High ORCID coverage (≥70%):** ORCID is used as a hard filter — only works in both ORCID and OpenAlex enter scoring.
- **Low ORCID coverage (<70%):** All OpenAlex works are kept, but affiliation anomaly detection flags works from institutions never associated with the researcher.

If the publication span exceeds 25 years, a warning suggests using `--since YEAR` to set the career start explicitly.

### 6.4. Transparency and Audit Trail

Every run produces a timestamped JSON audit file documenting: the researcher profile, every work analyzed, every citation link, every classification decision with a human-readable rationale, the co-author graph, the affiliation timeline and institution hierarchy, data quality metrics, and the score computation.

Every output carries an inline disclaimer: "BARON and HEROCON measure citation network structure, not research quality, impact, or integrity."

### 6.5. Technology Stack

Python 3.11+ CLI application using Typer, Rich, and httpx. No database required for Phases 1–3. Phase 4 adds a persistent venue governance database (SQLite/PostgreSQL) and a locally deployed Qwen 3.5 8B language model (Q4_K_M quantized, served via llama.cpp on Kubernetes). A Gradio-based web interface provides no-code access for all Phase 1–3 functionality.

**Data sources (all free and open):** OpenAlex (Priem et al., 2022) — 260M+ works, 100M+ authors, 2.8B+ citation links; ORCID Public API v3.0; ROR API v2; Cloudflare Crawl API (Phase 4 only).

**Performance.** For ~80 publications and ~1500 citations, Phase 3 completes in under 90 seconds with ~100–150 OpenAlex API calls.

### 6.6. The UNKNOWN Classification and Data Quality Reporting

OpenAlex work-level affiliations are present for approximately 75% of recent works, with lower coverage for older publications. When affiliation data is missing, the system cannot determine whether a citation is genuinely external or institutional.

Early versions defaulted such citations to EXTERNAL, creating systematic bias: researchers with poor metadata received artificially inflated BARON scores. This is both technically incorrect and ethically problematic.

I address this with UNKNOWN: citations are classified UNKNOWN when (a) the target researcher has no affiliation data for the relevant time period, or (b) no citing author has affiliation data for the citation year. UNKNOWN citations are excluded from both BARON and HEROCON calculations.

**Data quality metrics:** Classifiable citations count and percentage. Reliability rating: HIGH (≥85%), MODERATE (≥70%), LOW (≥50%), VERY LOW (<50%).

I acknowledge that excluding UNKNOWN citations from the denominator creates a different form of selection bias. If UNKNOWN citations are systematically different from classifiable ones — disproportionately from developing countries with poor metadata, or from older publications — then the computed scores may not represent the true citation distribution. I identify a sensitivity analysis comparing different UNKNOWN imputation strategies as a priority for future work.

---

## 7. Related Work

### 7.1. Citation-Based Research Impact Metrics

The h-index (Hirsch, 2005) remains the most widely recognized single-number measure of research impact. While elegant in its simplicity, the h-index has well-documented limitations: it is field-dependent, penalizes early-career researchers, and cannot distinguish between different types of citations (Waltman & van Eck, 2012; Bornmann & Daniel, 2005; Costas & Bordons, 2007). Seglen (1997) made the classic argument that journal impact factors should not be used for evaluating individual research.

The g-index (Egghe, 2006) and field-weighted citation impact (Waltman et al., 2011) address some limitations but share the fundamental problem of treating all citations equally regardless of source. Waltman (2016) provides a comprehensive review, concluding that existing approaches remain inadequate for capturing the multidimensional nature of research influence. Leydesdorff and Bornmann (2011) demonstrated how fractional counting of citations affects impact measurement across fields.

### 7.2. Self-Citation Analysis

Aksnes (2003) demonstrated that self-citations constitute a significant fraction of total citations. Kacem et al. (2020) provided a comprehensive analysis of self-citation patterns across disciplines. Critically, Ioannidis (2015) introduced a generalized view of self-citation extending beyond direct author self-citation to include co-author self-citation, collaborative self-citation, and coercive induced self-citation. This taxonomy is directly relevant to my multi-layer approach: my BARON and HEROCON scores operationalize a similar decomposition, extending Ioannidis's conceptual framework into a computable, auditable system.

Fowler and Aksnes (2007) demonstrated that self-citation increases subsequent citation from others. Seeber et al. (2019) explicitly framed self-citations as strategic responses to the use of metrics for career decisions, directly connecting to my Goodhart's Law concerns (Section 8.3).

### 7.3. Network-Aware Citation Analysis

**Invisible colleges.** Crane (1972) introduced informal networks of scientists who influence each other's work outside formal institutional structures. Zuccala (2006) developed a formal model reconciling structural and processual perspectives. These invisible colleges are precisely the "hidden networks" that my tool makes visible.

**Co-authorship and citation.** Newman (2001, 2004) established foundational methods for analyzing scientific collaboration networks. Glänzel and Schubert (2005) found that collaborative papers receive more citations. Moody (2004) traced increasing disciplinary cohesion. My Phase 2 co-author graph detection operationalizes these findings.

**Citation proximity.** Most directly relevant to my work, Wallace, Larivière, and Gingras (2012) examined citation proximity using degrees of separation in co-author networks, finding that direct self-citations are relatively constant across fields (~10% in natural sciences, ~20% in social sciences), while citations to co-author network members vary substantially. Their approach is conceptually identical to my BARON/HEROCON decomposition. My contribution extends their analysis with temporal affiliation matching, venue governance detection, ORCID identity validation, and a tool that any researcher can run on their own profile.

**Institutional and geographic effects.** Larivière and Gingras (2010) demonstrated the Matthew Effect in citation. Wagner and Leydesdorff (2005) analyzed international collaboration network structure. Pan, Kaski, and Fortunato (2012) uncovered the role of geography in shaping citation and collaboration networks.

**Citation homophily and diversity.** Hofstra et al. (2020) documented the diversity–innovation paradox: underrepresented groups innovate at higher rates but their contributions are discounted. This suggests that citation network structure may systematically disadvantage researchers less embedded in dominant citation communities. My UNKNOWN classification and data quality reporting attempt to make such biases visible.

### 7.4. Citation Cartels and Gaming

Baccini, De Nicolao, and Petrovich (2019) documented citation gaming at national scale. Edwards and Roy (2017) described perverse incentives. Smaldino and McElreath (2016) modeled the evolutionary pressure for bad science driven by metric optimization. Meho (2025) found institutions with publication surges of up to 965% driven by strategic optimization. These patterns illustrate Goodhart's Law as articulated by Fire and Guestrin (2019).

My tool does not detect gaming *per se* — it detects network structure. The distinction matters: in-group citation is normal and often appropriate. But making network composition visible creates accountability infrastructure.

### 7.5. Author Disambiguation and Identity

Ferreira, Gonçalves, and Laender (2012) surveyed automatic methods for disambiguation. OpenAlex (Priem et al., 2022) uses machine learning. Schulz et al. (2014) exploited citation networks for large-scale disambiguation, validating my use of co-author graphs as identity evidence. ORCID (Haak et al., 2012) provides researcher-maintained persistent identifiers. I use ORCID as a trust anchor for validating algorithmically assigned works.

### 7.6. Responsible Research Assessment

DORA (2012) calls for moving away from single-number metrics. The Leiden Manifesto (Hicks et al., 2015) requires that quantitative evaluation support qualitative expert judgment. Wilsdon et al. (2015) provided a comprehensive UK policy framework. De Rijcke et al. (2016) documented how indicator use distorts research behavior. Brembs (2018) demonstrated that prestigious journals struggle to reach even average reliability — relevant to my venue governance detection, which separates the structural fact of editorial connection from any quality judgment.

### 7.7. How This Work Extends the Existing Landscape

Having established where this work sits within the existing field, I note that the most directly comparable contribution — Wallace et al.'s (2012) analysis of citation at different network distances — established the conceptual framework that my tool operationalizes. What was missing from that work, and from the field more broadly, was the practical infrastructure: identity validation against ORCID to prevent disambiguation error from contaminating results, temporal affiliation matching to ensure institutional comparisons reflect reality rather than current affiliations, honest reporting of unclassifiable citations rather than defaulting them to external, full audit transparency enabling contestability, and a tool accessible to any researcher without programming skill or institutional subscription. These are the engineering contributions that transform a known insight into a usable diagnostic. I turn now to the implications, appropriate use cases, and structural tensions these scores create.

---

## 8. Discussion

### 8.1. Framing: Structure, Not Quality

BARON and HEROCON measure **citation network structure** — where in the social graph citations originate — not research quality, impact, or integrity. This distinction is the central design principle. A low BARON score might indicate a productive lab leader whose group naturally builds on their foundational contributions (Glänzel & Schubert, 2005), a small-field researcher in a 50-person community where nearly everyone is a co-author's co-author (Newman, 2001), or an insular practice that warrants self-examination. A high BARON score might indicate a cross-disciplinary thinker (Rafols & Meyer, 2010), an early-career researcher who has not yet built a collaborative network, or a "lone genius" working in isolation. The tool cannot distinguish these cases.

This reframing is not modesty; it is epistemic honesty. The analogy is structural analysis in engineering: documenting where the forces are, not judging whether the bridge is beautiful. A BARON score of 40% reports that 60% of a researcher's citations come from within their detected network. Whether it reflects healthy collaboration, strategic citation (Seeber et al., 2019), or the natural sociology of a small field (Crane, 1972) requires qualitative judgment that no metric can provide.

### 8.2. Alignment with Responsible Research Assessment

DORA (2012) calls for moving beyond single-number metrics. The Leiden Manifesto (Hicks et al., 2015) requires that quantitative evaluation support qualitative judgment. De Rijcke et al. (2016) documented how indicator use distorts research behavior — directly relevant to any new bibliometric tool, including this one.

I resolve the tension between introducing new quantitative metrics and the responsible assessment movement by positioning BARON and HEROCON as **supporting evidence for narrative evaluation**, not standalone metrics. The key distinction is between metrics designed to rank (h-index, impact factor) and metrics designed to describe (BARON, HEROCON). A ranking metric invites competition; a descriptive metric invites reflection. The Leiden Manifesto's first principle is satisfied when a metric provides structural context enriching human judgment rather than replacing it.

The audit trail makes this alignment concrete. A committee evaluating a researcher's portfolio could examine the audit file to understand *why* a BARON score takes a particular value — whether from intensive collaboration, a small field, or editorial roles. The number alone is silent; the audit trail speaks. This approach resonates with Rafols et al.'s (2012) argument that responsible indicators should make complexity visible rather than hiding it behind a single number.

### 8.3. The Goodhart Vulnerability

If BARON/HEROCON were adopted for evaluation, researchers would optimize for them — a direct manifestation of Goodhart's Law (Goodhart, 1984; Fire & Guestrin, 2019). The strategies are predictable: soliciting citations from strangers, avoiding citation of relevant co-author work, publishing in unfamiliar venues. Edwards and Roy (2017) documented similar perverse incentives. Smaldino and McElreath (2016) modeled the evolutionary dynamics.

A researcher could inflate BARON by (a) publishing under multiple name variants to split their co-author graph (Ferreira et al., 2012), (b) rotating institutional affiliations, (c) establishing reciprocal citation arrangements outside their detected network (Baccini et al., 2019), or (d) strategically managing ORCID records. Similar strategies have been documented for h-index manipulation (Seeber et al., 2019; Meho, 2025).

My mitigation: prominent disclaimers in every output, data quality reporting that makes scores visibly approximate, and positioning for self-reflection and policy research. I acknowledge these guardrails are imperfect — the history of bibliometric gaming suggests that sufficiently motivated actors will find ways to optimize any published metric (Fire & Guestrin, 2019).

### 8.4. The Case for HEROCON as Experimental

I do not have empirical evidence for the specific HEROCON weight values. As discussed in Section 6.1, these weights encode a formal hypothesis about the relative strength of different network pathways. The ordering is consistent with findings that co-authorship represents a stronger social tie than mere institutional proximity (Newman, 2004; Glänzel & Schubert, 2005), and that transitive network connections carry meaningful but attenuated social influence (Granovetter, 1973; Wallace et al., 2012). However, the cardinal distances between weights are not grounded in data.

Preliminary informal testing suggests that HEROCON scores are relatively stable under small weight changes for researchers with diverse citation profiles. However, scores can shift substantially for researchers whose citations are concentrated in a single category. This means HEROCON is most trustworthy when citation sources are diverse, and least trustworthy when the profile is dominated by a single network layer — unfortunately, when the diagnostic is most needed. This echoes a general challenge in composite indicators (OECD, 2008; **[Citation needed — composite indicator sensitivity literature]**).

BARON, by contrast, is binary and requires no weight calibration. It is the methodologically robust contribution. HEROCON is a promising extension whose value depends on future empirical work — but even in its current form, the gap's existence (if not its precise magnitude) is robust to weight perturbation.

### 8.5. Use Cases and Appropriate Deployment

I identify three appropriate use cases, in order of decreasing confidence:

1. **Science policy research.** Analyzing citation network structure at the field level is the safest use case. Aggregate patterns are more robust than individual scores (Hicks et al., 2015), and field-level analyses can reveal disciplinary norms (Wallace et al., 2012) informing policy on evaluation practices and collaboration incentives. Comparing BARON distributions across career stages, institution types, or geographic regions could provide evidence for structural inequalities (Hofstra et al., 2020; Larivière & Gingras, 2010).

2. **Self-reflection.** A researcher examining their own citation profile. The audit trail makes this actionable: inspect which co-authors cite most, whether institutional peers contribute substantially, and how external reach evolves over time. This aligns with calls for researcher self-awareness about citation practices (Aksnes, 2003; Ioannidis, 2015).

3. **Contextualizing evaluation.** Providing structural context alongside other evaluation evidence, consistent with DORA (2012) and the Leiden Manifesto (Hicks et al., 2015). The structural context helps evaluators ask better questions — it does not answer them.

I explicitly discourage use in hiring, promotion, or funding decisions as a standalone criterion.

---

## 9. Limitations and Future Work

### 9.1. Current Limitations

**Coverage bias.** OpenAlex is English-heavy and recent-heavy (Zheng et al., 2025; Martín-Martín et al., 2021). Researchers in non-English-language traditions or with older publication records may have systematically lower coverage.

**Temporal resolution limits.** Affiliation data is derived from publication-time institutional records, not employment records. A researcher changing institutions mid-year may have citations misclassified (Donner, Rimmert, & van Eck, 2020; **[Citation needed — affiliation data quality in bibliometric databases]**).

**The small-field problem.** In a 50-person community, nearly everyone may be a co-author's co-author at depth 2 (Newman, 2001). BARON would classify most citations as in-group, reflecting field size rather than citation practice. I plan to address this through field normalization (Section 9.2.4).

**ORCID selection bias.** Researchers with complete ORCID records tend to be at well-resourced institutions (Haak et al., 2012; **[Citation needed — ORCID adoption bias]**). My ORCID-based validation provides better protection for researchers who need it least.

**Author disambiguation remains imperfect.** Despite ORCID cross-validation, researchers without ORCID records cannot benefit (Priem et al., 2022; Ferreira et al., 2012).

**HEROCON weights are not empirically calibrated.** Diverse profiles are robust to perturbation; concentrated profiles are sensitive (Section 8.4). Until calibration is completed, HEROCON should be interpreted as indicative rather than definitive.

**UNKNOWN creates a conditioned sample.** If UNKNOWN citations are systematically different from classifiable ones — from developing countries with poor metadata (Rafols et al., 2015; Zheng et al., 2025), older publications, or certain disciplines — then computed scores reflect a biased subset. I plan to address this through sensitivity analysis (Section 9.2.1).

**Department-level matching is noisy.** ROR lacks department-level identifiers for most institutions (Lammey, 2020).

**Venue governance database coverage.** Phase 4's incremental database means first-time analyses in underserved fields have limited coverage. Coverage improves with use **[Citation needed — cold-start problem in knowledge base construction]**.

**LLM extraction accuracy.** Phase 4 relies on a locally deployed language model for structured extraction. LLMs perform well on information extraction (Wei et al., 2022; **[Citation needed — LLM-based IE benchmarks]**) but errors are inevitable for non-standard page structures or non-English content.

**The tool detects correlation, not causation.** A DIRECT_COAUTHOR citation may be genuinely motivated. The classification identifies structural potential for network mediation, not actuality (Borgatti, 2005; **[Citation needed — structural vs. actual influence in citation networks]**).

**The "lone genius" problem.** A truly independent researcher would have a very high BARON score for reasons opposite to those intended. The tool cannot distinguish this from massive external reach. This reinforces that it is a structural, not a quality, metric.

**No empirical validation against ground truth.** I have not yet demonstrated that scores correspond to independently verifiable properties of citation behavior. Validation would require showing that scores differ between collaborative and independent researchers, that ORCID validation changes scores for common names, or that classifications align with self-reported citation motivations (Bornmann & Daniel, 2008; **[Citation needed — citation motivation survey methodology]**).

### 9.2. Future Work

#### 9.2.1. Sensitivity Analysis (Priority)

I plan to systematically examine how scores respond to perturbation along four axes: (a) HEROCON weight variation (±0.1, ±0.2) to map the sensitivity surface; (b) UNKNOWN imputation strategy (all-EXTERNAL, all-in-group, proportional allocation); (c) co-author graph depth (1 to 3); and (d) temporal decay rate (half-lives of 3.5, 7, and 14 years). For each axis, I will report score distributions across researchers from diverse fields and career stages.

#### 9.2.2. Empirical Weight Calibration

I envision three approaches: survey-based citation motivation studies mapping self-reported motivations onto structural classifications; field-specific weight optimization using known collaborative versus independent profiles; and information-theoretic approaches maximizing discriminative power of the HEROCON–BARON gap. Calibrated weights would be published as field-specific weight files alongside the tool.

#### 9.2.3. Cross-Validation with Citation Motivation Studies

Cross-referencing structural classifications against ground-truth data on citation motivation. I note that citation motivation is notoriously difficult to study — the goal is to establish whether the structural signal is informative, not whether it is deterministic.

#### 9.2.4. Field-Normalized Percentile Scoring (Phase 5)

BARON 70% in theoretical physics means something different than 70% in biomedical research. Phase 5 will compute percentile ranks against peer cohorts, enabling statements like "BARON 72% (65th percentile in computational biology)."

#### 9.2.5. Confidence Intervals

Bootstrap confidence intervals reflecting sample size and metadata quality. A well-cited researcher with BARON 72% ± 4% presents a very different picture from an early-career researcher with BARON 72% ± 27%.

#### 9.2.6. Temporal Career Trajectory Analysis

Windowed analysis (rolling 5-year BARON) to answer: "Did external reach grow after changing institutions?" "Did BARON decline after establishing a large lab?"

#### 9.2.7. Multi-Source Data Fusion

Cross-referencing OpenAlex with Semantic Scholar, CrossRef, and DBLP (Zheng et al., 2025) to improve coverage and assess score sensitivity to data source choice.

#### 9.2.8. Collaborative and Community Extensions

Discipline-specific weight calibrations from domain experts, integration with institutional CRIS systems, support for non-Latin name scripts, and a shared venue governance database growing through distributed contribution.

---

## 10. Conclusion

I have introduced BARON and HEROCON, two complementary bibliometric scores that reveal the network composition of a researcher's citation profile — decomposing the undifferentiated mass of "citations" into a structured map of self-citation, co-authorship, institutional proximity, venue governance, and genuine external reach.

The primary contributions are both conceptual and architectural. Conceptually, the dual-score framework provides a new diagnostic lens: BARON's strict binary classification anchors the boundary of a citation profile, while HEROCON's graduated weighting maps the full constellation. The gap between the two serves as a readable diagnostic of inner-circle dependence — a quantity that, to my knowledge, no existing bibliometric tool reports.

Architecturally, the open-source tool contributes a multi-layer detection system combining self-citation analysis, co-authorship graph traversal with temporal decay, temporal affiliation matching via the Research Organization Registry, and AI-driven venue governance extraction into a single pipeline. The venue governance phase demonstrates a reusable pattern for AI-agent-driven bibliometric infrastructure: a locally deployed large language model performs structured extraction from heterogeneous web pages, an entity resolution layer matches against open bibliometric databases, and a persistent database captures the results — all running on commodity academic computing resources. This pattern is applicable well beyond venue governance, offering a template for automated extraction of any structured scholarly metadata that exists on the web but is not yet systematically captured.

The engineering features — ORCID-based identity validation, the UNKNOWN classification for honest data quality reporting, comprehensive audit transparency with human-readable rationales, and accessibility through both a command-line interface and a freely available no-code web application on SciLifeLab Serve — address persistent practical challenges that have prevented earlier theoretical insights about network-mediated citation from becoming usable diagnostic tools for the global research community.

I am deliberate about what these scores are not. They are not quality indicators. They are not integrity detectors. They are not suitable for hiring, promotion, or funding decisions. They describe *where* in the social graph citations originate — nothing more, nothing less.

BARON is the methodologically robust contribution: binary, requiring no weight calibration, and directly interpretable. HEROCON is an experimental extension whose graduated weights encode testable hypotheses about the relative strength of different network pathways in mediating citation behavior. I have been transparent about what is established and what remains unvalidated.

The audit trail is the true product. Every classification decision is documented. Every uncertainty is flagged. Every assumption is exposed to scrutiny. In a field where metrics are too often treated as authoritative pronouncements, I offer instead a tool that shows its work — and invites others to check it.

The tool is open-source and available at [https://github.com/citation-cosmograph/citation-constellation](https://github.com/citation-cosmograph/citation-constellation). I welcome empirical evaluations, cross-field analyses, and community contributions toward grounding these structural diagnostics in evidence.

---

## Acknowledgements

This work would not exist without the infrastructure and generosity of others.

I am profoundly grateful to **SciLifeLab** and the **SciLifeLab Serve** platform for providing the computational home where Citation-Constellation lives and breathes. Serve's commitment to hosting open research tools — freely, without barriers, for anyone — embodies exactly the democratic ethos this project aspires to. That a researcher anywhere in the world can navigate to a URL and decompose their citation profile without installing software, creating an account, or paying a fee is not my achievement alone; it is Serve's architecture that makes that sentence true.

I owe a particular and unusual debt to **Claude** (Anthropic). Citation-Constellation is, in the most literal sense, a project born in the quiet hours after my daughter falls asleep — a pastime pursued at the kitchen table after bedtime stories and lullabies. The idea of decomposing citation profiles by network proximity had lived in my head for some time, but the distance between an idea and an implementation is vast, and the hours between a child's sleep and one's own are few. Claude bridged that distance. It was my interlocutor when I needed to think out loud, my co-architect when the phased detection design was still taking shape, my patient debugger at midnight, and my writing partner through every draft of this paper. Without Claude, the idea would still be sitting where ideas sit when there is no one to talk to about them — somewhere between intention and indefinite postponement. I am grateful for a collaborator that never sleeps, never tires of being asked the same question differently, and never once complained about the hour.

Finally, I thank my daughter, **Ongshi**, whose nightly surrender to sleep is the starting gun for everything I build in the dark. The constellations in this paper are named for heroes and boundary guardians, but the brightest star in my sky is considerably smaller. I hope that one day she will read this paper, understand very little, care even less — and still say, with the generous conviction that only a daughter can muster, "This is really cool, Abbu."

---

## References

Aksnes, D. W. (2003). A macro study of self-citation. *Scientometrics*, 56(2), 235–246.

Baccini, A., De Nicolao, G., & Petrovich, E. (2019). Citation gaming induced by bibliometric evaluation: A country-level comparative analysis. *PLoS ONE*, 14(9), e0221212.

Borgatti, S. P. (2005). Centrality and network flow. *Social Networks*, 27(1), 55–71.

Bornmann, L., & Daniel, H. D. (2005). Does the h-index for ranking of scientists really work? *Scientometrics*, 65(3), 391–392.

Bornmann, L., & Daniel, H. D. (2008). What do citation counts measure? A review of studies on citing behavior. *Journal of Documentation*, 64(1), 45–80.

Brembs, B. (2018). Prestigious science journals struggle to reach even average reliability. *Frontiers in Human Neuroscience*, 12, 37.

Costas, R., & Bordons, M. (2007). The h-index: Advantages, limitations and its relation with other bibliometric indicators at the micro level. *Journal of Informetrics*, 1(3), 193–203.

Crane, D. (1972). *Invisible Colleges: Diffusion of Knowledge in Scientific Communities*. University of Chicago Press.

Curry, S., et al. (2022). *Agreement on Reforming Research Assessment*. Coalition for Advancing Research Assessment (CoARA).

de Rijcke, S., Wouters, P. F., Rushforth, A. D., Franssen, T. P., & Hammarfelt, B. (2016). Evaluation practices and effects of indicator use — a literature review. *Research Evaluation*, 25(2), 161–169.

Donner, P., Rimmert, C., & van Eck, N. J. (2020). Comparing institutional-level bibliometric research performance indicator values based on different affiliation disambiguation systems. *Quantitative Science Studies*, 1(1), 150–170.

DORA. (2012). San Francisco Declaration on Research Assessment. https://sfdora.org/

Edwards, M. A., & Roy, S. (2017). Academic research in the 21st century: Maintaining scientific integrity in a climate of perverse incentives and hypercompetition. *Environmental Engineering Science*, 34(1), 51–61.

Egghe, L. (2006). Theory and practise of the g-index. *Scientometrics*, 69(1), 131–152.

Ferreira, A. A., Gonçalves, M. A., & Laender, A. H. F. (2012). A brief survey of automatic methods for author name disambiguation. *ACM SIGMOD Record*, 41(2), 15–26.

Fire, M., & Guestrin, C. (2019). Over-optimization of academic publishing metrics: Observing Goodhart's Law in action. *GigaScience*, 8(6), giz053.

Fortunato, S., et al. (2018). Science of science. *Science*, 359(6379), eaao0185.

Fowler, J. H., & Aksnes, D. W. (2007). Does self-citation pay? *Scientometrics*, 72(3), 427–437.

Gerganov, G. (2023). llama.cpp. GitHub repository. https://github.com/ggerganov/llama.cpp

Glänzel, W., & Schubert, A. (2005). Analysing scientific networks through co-authorship. In *Handbook of Quantitative Science and Technology Research* (pp. 257–276). Springer.

Goodhart, C. A. E. (1984). Problems of monetary management: The UK experience. In *Monetary Theory and Practice* (pp. 91–121). Palgrave.

Granovetter, M. S. (1973). The strength of weak ties. *American Journal of Sociology*, 78(6), 1360–1380.

Haak, L. L., Fenner, M., Paglione, L., Pentz, E., & Ratner, H. (2012). ORCID: A system to uniquely identify researchers. *Learned Publishing*, 25(4), 259–264.

Hicks, D., Wouters, P., Waltman, L., de Rijcke, S., & Rafols, I. (2015). The Leiden Manifesto for research metrics. *Nature*, 520(7548), 429–431.

Hirsch, J. E. (2005). An index to quantify an individual's scientific research output. *Proceedings of the National Academy of Sciences*, 102(46), 16569–16572.

Hofstra, B., Kulkarni, V. V., Galvez, S. M.-N., He, B., Jurafsky, D., & McFarland, D. A. (2020). The diversity–innovation paradox in science. *Proceedings of the National Academy of Sciences*, 117(17), 9284–9291.

Huang, C.-K., Neylon, C., Brookes-Kenworthy, C., Hosking, R., Montgomery, L., Wilson, K., & Ozaygen, A. (2020). Comparison of bibliographic data sources. *Quantitative Science Studies*, 1(2), 583–612.

Ioannidis, J. P. A. (2015). A generalized view of self-citation. *Journal of Psychosomatic Research*, 78(1), 7–11.

Ioannidis, J. P. A., Baas, J., Klavans, R., & Boyack, K. W. (2019). A standardized citation metrics author database annotated for scientific field. *PLoS Biology*, 17(8), e3000384.

Kacem, A., Flatt, J. W., & Mayr, P. (2020). Tracking self-citations in academic publishing. *Scientometrics*, 123(2), 1157–1179.

Lammey, R. (2020). Solutions for identification problems: A look at the Research Organization Registry. *Science Editing*, 7(1), 65–69.

Larivière, V., & Gingras, Y. (2010). The impact factor's Matthew Effect. *Journal of the American Society for Information Science and Technology*, 61(2), 424–427.

Leydesdorff, L., & Bornmann, L. (2011). How fractional counting of citations affects the impact factor. *Journal of the American Society for Information Science and Technology*, 62(2), 217–229.

Martín-Martín, A., Thelwall, M., Orduna-Malea, E., & Delgado López-Cózar, E. (2021). Google Scholar, Microsoft Academic, Scopus, Dimensions, Web of Science, and OpenCitations' COCI: A multidisciplinary comparison. *Scientometrics*, 126(1), 871–906.

Meho, L. I. (2025). Gaming the metrics? Bibliometric anomalies and the integrity crisis in global university rankings. *Scientometrics*.

Moody, J. (2004). The structure of a social science collaboration network. *American Sociological Review*, 69(2), 213–238.

Newman, M. E. J. (2001). The structure of scientific collaboration networks. *Proceedings of the National Academy of Sciences*, 98(2), 404–409.

Newman, M. E. J. (2004). Coauthorship networks and patterns of scientific collaboration. *Proceedings of the National Academy of Sciences*, 101(suppl 1), 5200–5205.

OECD. (2008). *Handbook on Constructing Composite Indicators*. OECD Publishing.

Pan, R. K., Kaski, K., & Fortunato, S. (2012). World citation and collaboration networks. *Scientific Reports*, 2, 902.

Petersen, A. M., et al. (2012). Persistence and uncertainty in the academic career. *Proceedings of the National Academy of Sciences*, 109(14), 5213–5218.

Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. *arXiv preprint arXiv:2205.01833*.

Rafols, I., Ciarli, T., & Chavarro, D. (2015). Under-representation of research from the Global South in bibliometric databases. **[Citation needed — full reference]**

Rafols, I., Leydesdorff, L., O'Hare, A., Nightingale, P., & Stirling, A. (2012). How journal rankings can suppress interdisciplinary research. *Research Policy*, 41(7), 1262–1282.

Rafols, I., & Meyer, M. (2010). Diversity and network coherence as indicators of interdisciplinarity. *Scientometrics*, 82(2), 263–287.

Ridpath, I. (2018). *Star Tales* (revised and expanded edition). Lutterworth Press.

Schulz, C., Mazloumian, A., Petersen, A. M., Penner, O., & Helbing, D. (2014). Exploiting citation networks for large-scale author name disambiguation. *EPJ Data Science*, 3(1), 1–14.

Seeber, M., et al. (2019). Self-citations as strategic response to the use of metrics for career decisions. *Research Policy*, 48(9), 103688.

Seglen, P. O. (1997). Why the impact factor of journals should not be used for evaluating research. *BMJ*, 314(7079), 498.

Shen, H. W., & Barabási, A. L. (2014). Collective credit allocation in science. *Proceedings of the National Academy of Sciences*, 111(34), 12325–12330.

Smaldino, P. E., & McElreath, R. (2016). The natural selection of bad science. *Royal Society Open Science*, 3(9), 160384.

Touvron, H., et al. (2023). LLaMA: Open and efficient foundation language models. *arXiv preprint arXiv:2302.13971*.

UNESCO. (2021). *UNESCO Recommendation on Open Science*. UNESCO.

Visser, M., van Eck, N. J., & Waltman, L. (2021). Large-scale comparison of bibliographic data sources. *Quantitative Science Studies*, 2(1), 20–41.

Wagner, C. S., & Leydesdorff, L. (2005). Network structure, self-organization, and the growth of international collaboration in science. *Research Policy*, 34(10), 1608–1618.

Wallace, M. L., Larivière, V., & Gingras, Y. (2012). A small world of citations? *PLoS ONE*, 7(3), e33339.

Waltman, L. (2016). A review of the literature on citation impact indicators. *Journal of Informetrics*, 10(2), 365–391.

Waltman, L., & van Eck, N. J. (2012). The inconsistency of the h-index. *Journal of the American Society for Information Science and Technology*, 63(2), 406–415.

Waltman, L., van Eck, N. J., van Leeuwen, T. N., Visser, M. S., & van Raan, A. F. J. (2011). Towards a new crown indicator. *Journal of Informetrics*, 5(1), 37–47.

Wei, J., et al. (2022). Emergent abilities of large language models. *Transactions on Machine Learning Research*.

Wildgaard, L., Schneider, J. W., & Larsen, B. (2014). A review of the characteristics of 108 author-level bibliometric indicators. *Scientometrics*, 101(1), 125–158.

Wilsdon, J., et al. (2015). *The Metric Tide*. HEFCE.

Wuchty, S., Jones, B. F., & Uzzi, B. (2007). The increasing dominance of teams in production of knowledge. *Science*, 316(5827), 1036–1039.

Zheng, L., et al. (2025). Understanding discrepancies in the coverage of OpenAlex: The case of China. *Journal of the Association for Information Science and Technology*.

Zuccala, A. (2006). Modeling the invisible college. *Journal of the American Society for Information Science and Technology*, 57(2), 152–168.


"""
