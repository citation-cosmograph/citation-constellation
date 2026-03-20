"""
citation-constellation/app/RESEARCH_PAPER.py
=======================================
Information about the research paper
"""

RESEARCH_PAPER = """

# Where do your citations come from? Citation-Constellation: Decomposing citation profiles by network proximity with BARON and HEROCON scores

**Mahbub Ul Alam**

SciLifeLab Data Centre, Sweden

---

## Abstract

We introduce two complementary bibliometric scores — BARON (Boundary-Anchored Research Outreach Network score) and HEROCON (Holistic Equilibrated Research Outreach CONstellation score) — that decompose a researcher's citation profile by the network relationship between citing and cited authors. Unlike existing metrics that treat all citations as equivalent signals of impact, BARON and HEROCON classify each incoming citation across multiple layers: self-citation, co-authorship graph distance, temporal institutional affiliation, and venue governance structure. BARON provides a strict binary score counting only citations from outside the detected collaborative network, while HEROCON applies configurable graduated weights giving partial credit to in-group citations based on relationship proximity. We present an open-source tool implementing four detection phases, with particular emphasis on the engineering contributions: ORCID-validated author identity resolution, temporal affiliation matching via the Research Organization Registry (ROR), an UNKNOWN classification for citations with insufficient metadata, AI-agent-driven venue governance extraction using a locally deployed language model, and comprehensive audit trails documenting every classification decision. We position these scores as structural diagnostics describing where in the social graph citations originate, explicitly not as quality indicators, and discuss alignment with the responsible research assessment movement (DORA, Leiden Manifesto). We acknowledge that the graduated HEROCON weights are experimental and require empirical calibration, and identify sensitivity analysis and cross-validation with citation motivation studies as priorities for future work.

**Keywords:** bibliometrics, citation network structure, co-authorship analysis, author disambiguation, responsible research assessment, open science, venue governance

---

## 1. Introduction

The quantification of research impact is a central concern of modern science policy, institutional evaluation, and individual career assessment. Metrics such as the h-index (Hirsch, 2005), citation count, and journal impact factor have become deeply embedded in academic hiring, promotion, and funding decisions. Yet these metrics share a fundamental limitation: they treat all citations as equivalent signals of impact, regardless of the relationship between the citing and cited researchers. This limitation has been noted by numerous scholars (Seglen, 1997; Bornmann & Daniel, 2005; Costas & Bordons, 2007; Hicks et al., 2015; Waltman, 2016).

A citation from an independent researcher who discovers a paper through literature search carries a different epistemic weight than a citation from a direct co-author, a colleague in the same department, or a member of the same editorial board. The former represents genuine external reach — evidence that the work has found relevance beyond its originating community. The latter, while not illegitimate, reflects the natural amplification effects of collaborative networks, institutional proximity, and professional relationships. This phenomenon — the tendency for citation patterns to follow social network structure — has been extensively studied in the literature on invisible colleges (Crane, 1972; Zuccala, 2006), co-authorship networks (Newman, 2001, 2004; Glänzel & Schubert, 2005; Moody, 2004), and citation homophily (Wallace, Larivière, & Gingras, 2012; Wagner & Leydesdorff, 2005).

We acknowledge that the underlying insight — that citation patterns are shaped by social network proximity — is well-established in network science and scientometrics. The contribution of this work is primarily in **implementation architecture and engineering**: we present an open-source tool that operationalizes this insight into a practical, multi-layer detection system with several novel technical features. Specifically, we contribute:

1. **A phased detection architecture** that progressively deepens network analysis from self-citation through co-authorship graphs, temporal affiliation matching, and venue governance detection, with each phase producing an independently meaningful score.

2. **ORCID-validated author identity resolution** that addresses the critical challenge of disambiguation error contaminating citation analysis.

3. **An UNKNOWN classification** that honestly reports citations with insufficient metadata rather than defaulting them to EXTERNAL, preventing systematic bias against researchers with poor metadata coverage.

4. **Comprehensive audit transparency** where every classification decision is documented with a human-readable rationale in a structured JSON file, enabling full reproducibility and contestability.

5. **AI-agent-driven venue governance extraction** using a locally deployed language model to build a persistent, incrementally expanding database of editorial board and program committee membership across all academic disciplines.

6. **A dual-score framework** — BARON (strict binary) and HEROCON (graduated weighted) — where the gap between scores serves as a diagnostic of inner-circle dependence. We emphasize that the HEROCON weights are experimental defaults informed by intuition about relationship proximity, not empirically calibrated values.

We present these tools as structural diagnostics, not quality indicators. BARON and HEROCON describe where in the social graph citations originate. They should not be used for hiring, promotion, or funding decisions.

---

## 2. Related Work

### 2.1. Citation-Based Research Impact Metrics

The h-index (Hirsch, 2005) remains the most widely recognized single-number measure of research impact. While elegant in its simplicity, the h-index has well-documented limitations: it is field-dependent, penalizes early-career researchers, and cannot distinguish between different types of citations (Waltman & van Eck, 2012; Bornmann & Daniel, 2005; Costas & Bordons, 2007). Seglen (1997) made the classic argument that journal impact factors should not be used for evaluating individual research, a critique that extends to all metrics treating citations as homogeneous signals.

The g-index (Egghe, 2006) and field-weighted citation impact (Waltman et al., 2011) address some limitations but share the fundamental problem of treating all citations equally regardless of source. Waltman (2016) provides a comprehensive review of citation impact indicators, concluding that existing approaches remain inadequate for capturing the multidimensional nature of research influence. Leydesdorff and Bornmann (2011) demonstrated how fractional counting of citations affects impact measurement across fields, further highlighting normalization challenges.

### 2.2. Self-Citation Analysis

Aksnes (2003) demonstrated that self-citations constitute a significant fraction of total citations, particularly for researchers in small fields. Kacem et al. (2020) provided a comprehensive analysis of self-citation patterns across disciplines.

Critically, Ioannidis (2015) introduced a generalized view of self-citation that extends beyond direct author self-citation to include co-author self-citation, collaborative self-citation, and coercive induced self-citation. This taxonomy is directly relevant to our multi-layer approach: our BARON and HEROCON scores operationalize a similar decomposition, extending Ioannidis's conceptual framework into a computable, auditable system.

Fowler and Aksnes (2007) demonstrated that self-citation increases subsequent citation from others, suggesting a strategic dimension to self-referencing. Seeber et al. (2019) explicitly framed self-citations as strategic responses to the use of metrics for career decisions, directly connecting to our Goodhart's Law concerns (Section 6.3).

### 2.3. Network-Aware Citation Analysis

The study of network effects on citation behavior has a rich history. **Our work builds directly on this literature rather than replacing it.** We package existing insights into a unified, multi-layer scoring framework with engineering features (ORCID validation, audit transparency, UNKNOWN classification) that address practical deployment challenges.

**Invisible colleges and hidden networks.** Crane (1972) introduced the concept of invisible colleges — informal networks of scientists who communicate and influence each other's work outside formal institutional structures. Zuccala (2006) developed a formal model for studying invisible colleges that reconciles structural and processual perspectives. These invisible colleges are precisely the "hidden networks" that our tool attempts to make visible through network decomposition.

**Co-authorship and citation.** Newman (2001, 2004) established foundational methods for analyzing scientific collaboration networks. Glänzel and Schubert (2005) examined the relationship between co-authorship patterns and citation impact, finding that collaborative papers receive more citations. Moody (2004) traced the evolution of social science collaboration networks, revealing increasing disciplinary cohesion. Our Phase 2 co-author graph detection operationalizes these findings.

**Collaboration networks and citation proximity.** Most directly relevant to our work, Wallace, Larivière, and Gingras (2012) examined citation proximity using degrees of separation in co-author networks, finding that while direct self-citations are relatively constant across fields (~10% in natural sciences, ~20% in social sciences), citations to co-author network members vary substantially. Their approach of measuring citation at different network distances is conceptually identical to our BARON/HEROCON decomposition. Our contribution extends their analysis with temporal affiliation matching, venue governance detection, ORCID identity validation, and a tool that any researcher can run on their own profile.

**Institutional and geographic effects.** Larivière and Gingras (2010) demonstrated the Matthew Effect in citation — cumulative advantage where already-cited work receives disproportionate further citation, partly mediated by institutional prestige. Wagner and Leydesdorff (2005) analyzed international collaboration network structure and its relationship to citation patterns. Pan, Kaski, and Fortunato (2012) uncovered the role of geography in shaping citation and collaboration networks, with temporal dynamics relevant to our temporal affiliation matching approach.

**Citation homophily and diversity.** Hofstra, Kulkarni, Galvez, He, Jurafsky, and McFarland (2020) documented the diversity–innovation paradox: underrepresented groups innovate at higher rates but their contributions are discounted. This finding is relevant to our framework because it suggests that citation network structure may systematically disadvantage researchers whose networks are less embedded in dominant citation communities. Our UNKNOWN classification and data quality reporting attempt to make such biases visible rather than hiding them.

### 2.4. Citation Cartels and Gaming

Baccini, De Nicolao, and Petrovich (2019) documented citation gaming at national scale. The broader literature on "citation rings," "mutual citation clubs," and "invisible colleges" of strategic citation (Crane, 1972; Zuccala, 2006) has analyzed exactly the type of network-mediated citation our tool detects. Edwards and Roy (2017) described perverse incentives in academic publishing that encourage metric optimization. Smaldino and McElreath (2016) modeled the evolutionary pressure for bad science driven by metric optimization. Meho (2025) found institutions with publication surges of up to 965% driven by strategic metric optimization. These patterns illustrate Goodhart's Law as articulated by Fire and Guestrin (2019).

Our tool does not detect gaming *per se* — it detects network structure. The distinction matters: in-group citation is normal and often appropriate. But making network composition visible creates accountability infrastructure.

### 2.5. Author Disambiguation and Identity

Accurate author disambiguation is foundational to any citation-based metric. Ferreira, Gonçalves, and Laender (2012) surveyed automatic methods for disambiguation. OpenAlex (Priem et al., 2022) uses machine learning for disambiguation. Shen and Barabási (2014) studied collective credit allocation in science, finding that credit is distributed unevenly across collaboration networks. Schulz, Mazloumian, Petersen, Penner, and Helbing (2014) exploited citation networks for large-scale disambiguation, demonstrating that network structure itself provides signal for identity resolution — a finding that validates our use of co-author graphs as identity evidence.

ORCID (Haak et al., 2012) provides researcher-maintained persistent identifiers. We use ORCID as a trust anchor for validating algorithmically assigned works, addressing a critical practical challenge that many bibliometric tools overlook.

### 2.6. Institutional Affiliation and ROR

The Research Organization Registry (ROR) provides persistent identifiers for research organizations with hierarchical structure (Lammey, 2020). OpenAlex integrates ROR identifiers into affiliation data. However, ROR coverage is incomplete for smaller institutions, and department-level granularity is often unavailable.

### 2.7. Responsible Research Assessment

The Declaration on Research Assessment (DORA, 2012) calls for moving away from single-number metrics. The Leiden Manifesto (Hicks et al., 2015) establishes principles including that quantitative evaluation should support, not replace, qualitative expert judgment. Wilsdon et al. (2015), in *The Metric Tide*, provided a comprehensive UK policy framework for responsible metrics use. De Rijcke, Wouters, Rushforth, Franssen, and Hammarfelt (2016) reviewed the effects of indicator use on research behavior, finding that metrics can distort the practices they aim to measure.

Brembs (2018) demonstrated that prestigious science journals struggle to reach even average reliability, questioning whether venue prestige should be conflated with research quality — a finding relevant to our venue governance detection, which separates the structural fact of editorial connection from any quality judgment.

### 2.8. Positioning Our Contribution

We do not claim that the *insight* — that citation patterns reflect network structure — is novel. This has been established by decades of research from Crane (1972) through Wallace et al. (2012) and beyond. Our contribution is the **engineering and packaging**: a multi-phase open-source tool that combines network detection layers with identity validation, honest data quality reporting, full audit transparency, and AI-driven venue governance extraction into a system that any researcher can run on their own profile. The BARON/HEROCON dual-score framework provides an interpretable summary, but the audit trail is the real product.

---

## 3. Methodology

### 3.1. Conceptual Framework

We conceptualize a researcher's citation profile as concentric network layers, from most proximate (self) to most distant (external). Each layer represents a relationship type that could mediate citation behavior:

- **Layer 0 — Self:** Citing own prior work.
- **Layer 1 — Direct co-authors:** Shared at least one publication.
- **Layer 2 — Transitive co-authors:** Co-authors of co-authors (configurable depth, default 2).
- **Layer 3 — Institutional colleagues:** Same institution/department, even without co-authorship.
- **Layer 4 — Venue governance:** Editorial board or program committee overlap with citing venue.
- **Layer 5 — External:** No detected relationship.

BARON treats all layers 0–4 as in-group (weight = 0) and only counts fully external citations (weight = 1). HEROCON assigns graduated weights:

| Layer | Relationship | BARON | HEROCON | Rationale |
|-------|-------------|-------|---------|-----------|
| 0 | Self-citation | 0 | 0.0 | No credit — researcher is citing themselves |
| 1 | Direct co-author | 0 | 0.2 | Low credit — strongest collaborative tie |
| 2 | Transitive co-author | 0 | 0.5 | Moderate credit — indirect tie, weaker influence pathway |
| 3a | Same department | 0 | 0.1 | Very low credit — strongest proximity without co-authorship; forced proximity may reduce citation choice |
| 3b | Same institution, different dept | 0 | 0.4 | Moderate credit — institutional connection but cross-departmental; more likely reflects genuine intellectual engagement |
| 3c | Same parent organization | 0 | 0.7 | High credit — tenuous institutional link; shared parent org (e.g., University of California system) provides minimal direct influence |
| 4a | Venue self-governance | 0 | 0.05 | Near-zero — researcher directly governs the venue; strongest structural pathway to citation |
| 4b | Venue editor is co-author | 0 | 0.15 | Low credit — compound relationship (co-authorship + editorial) |
| 4c | Venue editor at same institution | 0 | 0.3 | Moderate credit — institutional link through editorial channel |
| 4d | Committee member in network | 0 | 0.4 | Moderate credit — weaker governance connection |
| — | External | 1 | 1.0 | Full credit — no detected relationship |

**On the weight ordering.** A reviewer might question why same-department (0.1) is weighted lower than direct co-author (0.2). Our reasoning: department colleagues who have never co-authored represent *forced proximity* — they share a physical and administrative space regardless of intellectual choice. A distant co-author was a *chosen* collaborator. However, the co-author's citation may also reflect genuine intellectual engagement with the specific work, justifying slightly more credit than pure proximity. Similarly, transitive co-author (0.5) exceeds same-institution-different-department (0.4) because the transitive link may reflect intellectual community membership, while a different-department colleague at the same university may have no substantive relationship beyond administrative structure.

**We acknowledge these weights are experimental defaults, not empirically calibrated values.** They are informed by intuition about the structural mechanisms through which different relationship types could mediate citation behavior. We provide full weight customization via `--herocon-weights path/to/weights.json` and identify empirical weight calibration as a priority for future work (Section 7.2). Sensitivity analysis examining score stability under weight perturbation is planned.

**Score computation:**

**BARON** = (external citations / classifiable citations) × 100

**HEROCON** = (Σ w_i for each classifiable citation *i*) / classifiable citations × 100

where *w_i* is the HEROCON weight for citation *i*'s classification, and "classifiable" excludes UNKNOWN citations (see Section 3.5).

**Diagnostic gap** = HEROCON − BARON: the proportion of impact attributable to in-group citations under graduated weighting.

### 3.2. Phased Implementation Architecture

Each phase adds a detection layer and produces a usable score. Later phases incorporate earlier layers, so Phase 4 performs all detection in a single run.

#### 3.2.1. Phase 1: Self-Citation Baseline

For each researcher publication, fetch all incoming citations from OpenAlex. Check whether any author ID on the citing work matches the target researcher. Classify as SELF or NON_SELF.

BARON v0.1 = percentage of NON_SELF citations.

#### 3.2.2. Phase 2: Co-Author Network Detection

Construct a co-authorship graph from the target researcher's publications. Each author pair sharing a paper creates a weighted edge:

*strength(a, b) = shared_papers(a, b) × exp(−0.1 × years_since_last_collaboration)*

The exponential decay with rate 0.1 yields a half-life of approximately 7 years (ln(2)/0.1 ≈ 6.93). This reflects the intuition that recent collaborators are more "in-group" than distant ones. We note that the specific decay rate is not empirically grounded — alternative rates (e.g., 0.05 for a ~14-year half-life, or 0.2 for a ~3.5-year half-life) would be equally defensible. The decay function currently modulates co-authorship strength metadata logged in audit files but does not affect BARON classification (which uses binary in/out). Future work on HEROCON weight calibration could incorporate strength-weighted penalties.

BFS to configurable depth *d* (default 2) from the target researcher. Classify by graph distance: 0 → SELF, 1 → DIRECT_COAUTHOR, 2 → TRANSITIVE_COAUTHOR, >*d* → EXTERNAL.

HEROCON is introduced in this phase with the 4-class taxonomy.

#### 3.2.3. Phase 3: Temporal Affiliation Matching

Citations not classified as SELF or co-author are checked for institutional affiliation overlap at the time of citation. We build an affiliation timeline from work-level affiliation data in OpenAlex (each authorship record includes the author's institution at time of publication). Institutional relationships are resolved using ROR parent-child hierarchy and OpenAlex lineage data, producing four tiers: SAME_DEPT, SAME_INSTITUTION, SAME_PARENT_ORG, DIFFERENT.

When affiliation data is insufficient for classification, citations are labeled UNKNOWN (see Section 3.5).

#### 3.2.4. Phase 4: Venue Governance Detection

This phase detects citations flowing through venues where the target researcher or their network holds governance roles. Rather than fragile per-publisher web scrapers, we use a locally deployed language model (Qwen 3.5 8B, Q4_K_M quantized) to extract structured governance data from venue editorial board pages.

The venue governance pipeline operates in two stages:

**Stage 1 — Database construction.** For each venue in the researcher's citing works, the system fetches the editorial board page (via httpx or Cloudflare Crawl API for JS-rendered sites), feeds the raw HTML to the local LLM for structured extraction (member name, role, institution, ORCID), and performs entity resolution against OpenAlex author profiles. Results are cached in a persistent database with confidence scores and timestamps.

**Stage 2 — Citation reclassification.** For each citation currently classified as EXTERNAL, check whether the citing venue has governance overlap with the target researcher or their network. Classify as VENUE_SELF_GOVERNANCE (target on editorial board), VENUE_EDITOR_COAUTHOR (venue editor is co-author), VENUE_EDITOR_AFFIL (venue editor at same institution), or VENUE_COMMITTEE (committee member in network).

The venue governance database is designed for incremental growth: each new researcher analysis contributes new venues. A nightly job refreshes stale entries.

#### 3.2.5. Phase 5: Field Normalization and Percentiles (Proposed)

Field-normalized percentile ranks comparing a researcher's scores against peer cohorts (same field, similar career length, comparable publication volume). This addresses field-dependence: BARON 70% in theoretical physics means something different than 70% in biomedical research. This phase is not yet implemented.

### 3.3. Author Identity Validation via ORCID

A critical challenge encountered during development was author disambiguation error in OpenAlex. Researchers with common names may have works misattributed to their profile from other researchers with similar names. This contamination undermines scoring accuracy, as misattributed works bring incorrect co-authors, affiliations, and citations.

We address this through ORCID cross-validation using a smart two-mode system:

- **High ORCID coverage (≥70%):** ORCID is used as a hard filter — only works in both ORCID and OpenAlex enter scoring.
- **Low ORCID coverage (<70%):** All OpenAlex works are kept, but affiliation anomaly detection flags works from institutions never associated with the researcher.

Additionally, if the publication span exceeds 25 years, a warning suggests using `--since YEAR` to set the career start explicitly — the cleanest user-driven fix for name collision.

### 3.4. Transparency and Audit Trail

Every run produces a timestamped JSON audit file documenting: the researcher profile, every work analyzed, every citation link, every classification decision with a human-readable rationale, the co-author graph, the affiliation timeline and institution hierarchy, data quality metrics, and the score computation.

Every output carries an inline disclaimer: "BARON and HEROCON measure citation network structure, not research quality, impact, or integrity."

### 3.5. The UNKNOWN Classification and Data Quality Reporting

OpenAlex work-level affiliations are present for approximately 75% of recent works, with lower coverage for older publications, non-English research, and certain fields. When affiliation data is missing, the system cannot determine whether a citation is genuinely external or institutional.

Early versions defaulted such citations to EXTERNAL, creating systematic bias: researchers with poor metadata (often in developing countries or underrepresented fields) received artificially inflated BARON scores. This is both technically incorrect and ethically problematic.

We address this with UNKNOWN: citations are classified UNKNOWN when (a) the target researcher has no affiliation data for the relevant time period, or (b) no citing author has affiliation data for the citation year. UNKNOWN citations are excluded from both BARON and HEROCON calculations.

**Data quality metrics:**
- **Classifiable citations:** Count and percentage with sufficient metadata.
- **Reliability rating:** HIGH (≥85%), MODERATE (≥70%), LOW (≥50%), VERY LOW (<50%).

**Limitations of the UNKNOWN approach.** We acknowledge that excluding UNKNOWN citations from the denominator creates a different form of selection bias: if UNKNOWN citations are systematically different from classifiable ones (e.g., disproportionately from developing countries with poor metadata, or from older publications), then the BARON/HEROCON scores computed on classifiable citations may not represent the true citation distribution. The reliability rating provides a coarse signal of this risk, but it does not validate that HIGH reliability actually correlates with score stability. We identify a sensitivity analysis — examining how scores change under different assumptions about UNKNOWN citations (e.g., all-EXTERNAL vs. all-in-group vs. proportional allocation) — as a priority for future work.

---

## 4. Implementation

### 4.1. Technology Stack

Python 3.11+ CLI application using Typer, Rich, and httpx. No database required for Phases 1–3 (all data in memory, persisted via audit JSON). Phase 4 adds a persistent venue governance database (SQLite/PostgreSQL) and a locally deployed Qwen 3.5 8B language model (Q4_K_M quantized, served via llama.cpp on Kubernetes).

### 4.2. Data Sources

**OpenAlex** (Priem et al., 2022) — primary source. 260M+ works, 100M+ authors, 200K+ venues, 2.8B+ citation links. Free.
**ORCID Public API v3.0** — identity validation. Free.
**ROR API v2** — institutional hierarchy. Free.
**Cloudflare Crawl API** — JS-rendered venue pages (Phase 4). Free tier, 6 req/min.

### 4.3. Modular Architecture

- `models.py` — Data classes, HEROCON weights, scoring functions.
- `client.py` — Async API clients with rate limiting, pagination, retry.
- `orcid_validate.py` — ORCID cross-validation.
- `audit.py` — Audit trail builder.
- `phase1.py` through `phase4.py` — Phase-specific pipelines and classifiers.
- `venue_governance.py` — Venue database construction pipeline (Phase 4).

### 4.4. Performance

For ~80 publications and ~1500 citations, Phase 3 completes in under 90 seconds with ~100–150 OpenAlex API calls. Phase 4 adds venue governance lookups; cached venues add negligible overhead, while new venue scraping + LLM extraction adds 10–30 seconds per uncached venue.

---

## 5. Results and Demonstration

### 5.1. Score Progression Across Phases

As detection layers deepen, BARON decreases as more in-group relationships are identified:

| Phase | Detection Layers | Classes | BARON | HEROCON | Gap |
|-------|-----------------|---------|-------|---------|-----|
| 1 | Self-citation | 2 | High | — | — |
| 2 | + Co-author network | 4 | Moderate | Moderate-High | Small |
| 3 | + Affiliation matching | 7 | Lower | Moderate | Larger |
| 4 | + Venue governance | 11 | Lowest | Moderate | Largest |

The typical BARON drop from Phase 1→2 is 10–25 percentage points. Phase 2→3 drops 5–15 points. Phase 3→4 drops 3–8 points, depending on venue governance coverage.

### 5.2. The Diagnostic Value of the Gap

A researcher with BARON 60% and HEROCON 65% (gap: 5%) has minimal inner-circle effect. BARON 40% and HEROCON 65% (gap: 25%) has a large effect — the network provides substantial citation amplification.

Neither pattern is inherently good or bad. A large-gap researcher may be a productive lab leader. A small-gap researcher may be an independent theorist with cross-disciplinary reach.

### 5.3. ORCID Cross-Validation Impact

In testing, OpenAlex had merged works from a different researcher with a similar name. The ORCID layer correctly excluded misattributed works, preventing contamination of the co-author graph and affiliation timeline. DOI-based matching resolved 70–85% of works; title-based fuzzy matching recovered an additional 10–15%.

### 5.4. Venue Governance Detection

Phase 4 analysis revealed that for a representative researcher with publications in 15–20 unique venues, 2–4 venues had editorial board overlap with the researcher's network. The self-governance fraction — the percentage of citations from venues where the researcher holds a governance role — ranged from 0% (no editorial service) to 12% in a case with extensive editorial board membership. This metric is independently reportable and provides concrete, verifiable structural information.

### 5.5. Limitations of Current Validation

We acknowledge that the current demonstration is descriptive rather than validational. We have not yet established that BARON/HEROCON scores correlate with (or meaningfully diverge from) independent measures of citation motivation, research quality, or integrity. Validation would require showing, for example, that:

- BARON correlates with self-citation rates in predictable ways (it does by construction for Phase 1, but the relationship becomes less obvious for later phases).
- Scores differ significantly between researchers known to be highly collaborative vs. independent.
- ORCID validation meaningfully changes scores for researchers with common names.
- The HEROCON–BARON gap distinguishes structural patterns that experts recognize as different collaboration modes.

We identify such validation as a critical priority for future work (Section 7).

---

## 6. Discussion

### 6.1. Framing: Structure, Not Quality

BARON and HEROCON measure **citation network structure** — where in the social graph citations originate — not research quality, impact, or integrity. A low BARON score might indicate a productive lab leader, a small-field researcher, or an insular practice. The tool cannot distinguish these cases.

This reframing is not modesty; it is epistemic honesty. The analogy is structural analysis in engineering: documenting where the forces are, not judging whether the bridge is beautiful.

### 6.2. Alignment with Responsible Research Assessment

DORA (2012) calls for moving beyond single-number metrics. The Leiden Manifesto (Hicks et al., 2015) requires that quantitative evaluation support qualitative judgment. Wilsdon et al. (2015) articulated a UK policy framework for responsible metrics. De Rijcke et al. (2016) documented how indicator use distorts research behavior.

BARON and HEROCON sit in tension with this movement: they are new quantitative metrics at a time when the field moves toward narrative assessment. We resolve this by positioning them as **supporting evidence for narrative evaluation**, not standalone metrics. The audit trail is the real value — it enriches qualitative judgment with structural context.

### 6.3. The Goodhart Vulnerability

If BARON/HEROCON were adopted for evaluation, researchers would optimize for them. The strategies are predictable: soliciting citations from strangers (artificial), avoiding citation of relevant co-author work (scientifically harmful), publishing in unfamiliar venues (strategically distorting). Edwards and Roy (2017) documented similar perverse incentives. Smaldino and McElreath (2016) modeled the evolutionary dynamics.

**Specific gaming strategies for our metrics:** A researcher could inflate BARON by (a) publishing under multiple name variants to split their co-author graph, (b) rotating institutional affiliations to create artificial "external" status, (c) establishing reciprocal citation arrangements with researchers outside their detected network, or (d) strategically managing ORCID records to exclude works with dense in-group citation. These are not theoretical — similar strategies have been documented for h-index manipulation (Seeber et al., 2019; Meho, 2025).

Our mitigation: (a) prominent disclaimers in every output, (b) data quality reporting that makes scores visibly approximate, (c) positioning for self-reflection and policy research, not individual evaluation. We acknowledge these guardrails are imperfect.

### 6.4. The Case for HEROCON as Experimental

The HEROCON weights are experimental defaults. We do not have empirical evidence for the specific values. A sensitivity analysis examining how scores change under ±0.1 weight perturbation is planned as immediate future work. Preliminary informal testing suggests that HEROCON scores are relatively stable under small weight changes for researchers with diverse citation profiles, but can shift substantially for researchers whose citations are concentrated in a single classification category (e.g., predominantly co-author citations). Formal analysis is needed.

BARON, by contrast, is binary and requires no weight calibration. It is the methodologically robust contribution. HEROCON is a promising direction requiring empirical grounding.

### 6.5. Limitations

**Coverage bias.** OpenAlex is English-heavy and recent-heavy (Zheng et al., 2025). Researchers in non-English-language research traditions or with older publication records may have systematically lower coverage, affecting both BARON scores and reliability ratings.

**Temporal resolution limits.** Affiliation data is derived from publication-time institutional records, not from employment records. A researcher who changes institutions mid-year may have citations misclassified until a publication at the new institution establishes the timeline entry.

**The small-field problem.** In a 50-person research community, nearly everyone may be a co-author's co-author at depth 2. BARON would classify most citations as in-group, yielding a low score that reflects field size rather than citation practice. Field normalization (Phase 5) partially addresses this.

**ORCID selection bias.** Researchers with complete ORCID records tend to be more organized, more affiliated with well-resourced institutions, and more likely to be in Western academic systems. Our ORCID-based validation thus provides better protection for researchers who need it least.

**Author disambiguation remains imperfect.** Despite ORCID cross-validation, researchers without ORCID records cannot benefit from this safeguard.

**HEROCON weights are not empirically calibrated.** See Section 6.4.

**UNKNOWN creates a conditioned sample.** See Section 3.5.

**Department-level matching is noisy.** ROR lacks department-level identifiers for most institutions.

**Venue governance database coverage.** Phase 4's incremental database means first-time analyses in underserved fields will have limited venue coverage. Coverage improves with use.

**The tool detects correlation, not causation.** A citation classified as DIRECT_COAUTHOR may represent a genuinely motivated citation. The classification identifies structural potential for network-mediated citation, not actuality.

**No empirical validation against ground truth.** See Section 5.5.

### 6.6. Use Cases

We identify three appropriate use cases, in order of decreasing confidence:

1. **Science policy research.** Analyzing citation network structure at the field level (e.g., "what fraction of citations in computational biology come from within collaboration networks?") is the safest use case. Aggregate patterns are more robust than individual scores.

2. **Self-reflection.** A researcher examining their own citation profile to understand structural composition. The audit trail makes this actionable.

3. **Contextualizing evaluation.** Providing structural context alongside other evaluation evidence. For example: "This candidate's 500 citations include a BARON score of 72%, indicating that most citations originate from outside their immediate network." This should supplement, never replace, expert judgment.

We explicitly discourage use in hiring, promotion, or funding decisions as a standalone criterion.

---

## 7. Future Work

### 7.1. Sensitivity Analysis (Priority)

Formal analysis of score stability under: (a) HEROCON weight perturbation (±0.1 per weight), (b) different UNKNOWN imputation strategies (all-EXTERNAL, all-in-group, proportional), (c) different co-author graph depths, (d) different temporal decay rates. This is the most urgent methodological gap.

### 7.2. Empirical Weight Calibration

The HEROCON weights require grounding in evidence. Possible approaches: (a) survey-based citation motivation studies to estimate the probability that citations across different relationship types are "network-mediated" vs. "independently motivated," (b) field-specific weight optimization using known collaborative vs. independent researcher profiles, (c) information-theoretic approaches that maximize the discriminative power of the HEROCON–BARON gap across researcher types.

### 7.3. Cross-Validation with Citation Motivation Studies

Validating classifications against ground-truth data on citation motivation. If survey data on why researchers cite particular works becomes available, we could assess whether EXTERNAL classifications genuinely reflect intellectual motivation and whether in-group classifications genuinely reflect network mediation.

### 7.4. Field-Normalized Percentile Scoring (Phase 5)

Cross-field comparability through percentile ranks against peer cohorts.

### 7.5. Confidence Intervals

Bootstrap confidence intervals reflecting sample size: BARON 72% with 95% CI [68%, 76%] for a well-cited researcher vs. BARON 72% with CI [45%, 99%] for one with 15 citations.

### 7.6. Temporal Career Trajectory Analysis

Computing BARON/HEROCON as time series to answer: "Did external reach grow after changing institutions?" "Did BARON decline after establishing a large lab?"

### 7.7. Multi-Source Data Fusion

Cross-referencing OpenAlex with Semantic Scholar, CrossRef, and DBLP for improved coverage and accuracy.

---

## 8. Conclusion

We have introduced BARON and HEROCON, two scores that reveal the network composition of a researcher's citation profile. The primary contributions are engineering and architectural: (1) a multi-layer detection system combining self-citation analysis, co-authorship graph traversal, temporal affiliation matching, and AI-driven venue governance extraction; (2) ORCID-based identity validation addressing author disambiguation error; (3) an UNKNOWN classification for honest data quality reporting; (4) comprehensive audit transparency with human-readable rationales; and (5) a dual-score framework where the gap between strict (BARON) and graduated (HEROCON) scores serves as a structural diagnostic.

We emphasize that these scores measure citation network structure, not research quality. BARON is the methodologically robust contribution (binary, no weight calibration needed). HEROCON is an experimental extension requiring empirical calibration. The audit trail is the true product: every decision documented, every uncertainty flagged.

The tool is open-source. We welcome empirical evaluations — particularly citation motivation surveys that could ground HEROCON weights in evidence, and cross-field analyses revealing how network structure varies across disciplines, career stages, and collaboration norms.

---

### Notes on Nomenclature

¹ **BARON** — The acronym BARON was chosen because the historical concept of a *Marcher Baron* — a feudal lord charged with securing the outer boundaries of a realm — resonates with what this score measures. Just as Marcher Barons anchored the borders so that the interior of a kingdom could function with legitimacy, the BARON score anchors the integrity of a researcher's overall citation metrics by measuring strictly boundary-spanning outreach. It focuses entirely on external validation: citations that cross beyond the researcher's immediate academic circle. The BARON score thus serves as the foundational threshold governing the broader HEROCON score; without demonstrated external reach, the constellation cannot take shape. The name also carries connotations of domain stewardship — a Baron manages and is accountable for what lies within their boundaries, much as a researcher is accountable for the structural composition of their citation profile.

² **HEROCON** — The name derives from the constellation Hercules (abbreviated *Her* in astronomical catalogues; IAU designation). In Greek mythology, Heracles was transformed into a constellation after his death — placed among the stars as an eternal monument to strength, perseverance, and labors that transcended mortal limits. The HEROCON score similarly maps a researcher's total scholarly influence as a grand constellation. In this metaphor, localized collaborations — co-authors, departmental colleagues, institutional peers — form bright, dense clusters of stars. But a constellation cannot be confined to a single cluster; it must stretch across the sky to earn its name. The BARON score provides the anchoring boundary stars that give the constellation its shape; without broad external validation, a dense local cluster remains just that — a cluster, not a figure of legend. The constellation's brightest star, *Rasalgethi* (α Herculis, from the Arabic *ra's al-jāthī*, "the kneeler's head"), carries a further resonance: true scholarly leadership, like the kneeling Hercules, requires humility. A high HEROCON score demonstrates that a researcher honors the contributions of their immediate community while recognizing that an enduring legacy is achieved by illuminating the broader scholarly universe beyond it (Ridpath, 2018).

**Reference for nomenclature:** Ridpath, I. (2018). *Star Tales*. Lutterworth Press. [For the mythology and etymology of the constellation Hercules and Rasalgethi.]

---

## References

Aksnes, D. W. (2003). A macro study of self-citation. *Scientometrics*, 56(2), 235–246.

Baccini, A., De Nicolao, G., & Petrovich, E. (2019). Citation gaming induced by bibliometric evaluation: A country-level comparative analysis. *PLoS ONE*, 14(9), e0221212.

Bornmann, L., & Daniel, H. D. (2005). Does the h-index for ranking of scientists really work? *Scientometrics*, 65(3), 391–392.

Brembs, B. (2018). Prestigious science journals struggle to reach even average reliability. *Frontiers in Human Neuroscience*, 12, 37.

Bu, Y., Waltman, L., & Huang, Y. (2018). A multidimensional framework for characterizing the citation impact of scientific publications. *Quantitative Science Studies*, 2(1), 155–183.

Costas, R., & Bordons, M. (2007). The h-index: Advantages, limitations and its relation with other bibliometric indicators at the micro level. *Journal of Informetrics*, 1(3), 193–203.

Crane, D. (1972). *Invisible Colleges: Diffusion of Knowledge in Scientific Communities*. University of Chicago Press.

de Rijcke, S., Wouters, P. F., Rushforth, A. D., Franssen, T. P., & Hammarfelt, B. (2016). Evaluation practices and effects of indicator use — a literature review. *Research Evaluation*, 25(2), 161–169.

DORA. (2012). San Francisco Declaration on Research Assessment. https://sfdora.org/

Edwards, M. A., & Roy, S. (2017). Academic research in the 21st century: Maintaining scientific integrity in a climate of perverse incentives and hypercompetition. *Environmental Engineering Science*, 34(1), 51–61.

Egghe, L. (2006). Theory and practise of the g-index. *Scientometrics*, 69(1), 131–152.

Ferreira, A. A., Gonçalves, M. A., & Laender, A. H. F. (2012). A brief survey of automatic methods for author name disambiguation. *ACM SIGMOD Record*, 41(2), 15–26.

Fire, M., & Guestrin, C. (2019). Over-optimization of academic publishing metrics: Observing Goodhart's Law in action. *GigaScience*, 8(6), giz053.

Fowler, J. H., & Aksnes, D. W. (2007). Does self-citation pay? *Scientometrics*, 72(3), 427–437.

Glänzel, W., & Schubert, A. (2005). Analysing scientific networks through co-authorship. In *Handbook of Quantitative Science and Technology Research* (pp. 257–276). Springer.

Haak, L. L., Fenner, M., Paglione, L., Pentz, E., & Ratner, H. (2012). ORCID: A system to uniquely identify researchers. *Learned Publishing*, 25(4), 259–264.

Hicks, D., Wouters, P., Waltman, L., de Rijcke, S., & Rafols, I. (2015). The Leiden Manifesto for research metrics. *Nature*, 520(7548), 429–431.

Hirsch, J. E. (2005). An index to quantify an individual's scientific research output. *Proceedings of the National Academy of Sciences*, 102(46), 16569–16572.

Hofstra, B., Kulkarni, V. V., Galvez, S. M.-N., He, B., Jurafsky, D., & McFarland, D. A. (2020). The diversity–innovation paradox in science. *Proceedings of the National Academy of Sciences*, 117(17), 9284–9291.

Ioannidis, J. P. A. (2015). A generalized view of self-citation: Direct, co-author, collaborative, and coercive induced self-citation. *Journal of Psychosomatic Research*, 78(1), 7–11.

Ioannidis, J. P. A., Baas, J., Klavans, R., & Boyack, K. W. (2019). A standardized citation metrics author database annotated for scientific field. *PLoS Biology*, 17(8), e3000384.

Kacem, A., Flatt, J. W., & Mayr, P. (2020). Tracking self-citations in academic publishing. *Scientometrics*, 123(2), 1157–1179.

Lammey, R. (2020). Solutions for identification problems: A look at the Research Organization Registry. *Science Editing*, 7(1), 65–69.

Larivière, V., & Gingras, Y. (2010). The impact factor's Matthew Effect: A natural experiment in bibliometrics. *Journal of the American Society for Information Science and Technology*, 61(2), 424–427.

Leydesdorff, L., & Bornmann, L. (2011). How fractional counting of citations affects the impact factor: Normalization in terms of differences in citation potentials among fields of science. *Journal of the American Society for Information Science and Technology*, 62(2), 217–229.

Meho, L. I. (2025). Gaming the metrics? Bibliometric anomalies and the integrity crisis in global university rankings. *Scientometrics*.

Moody, J. (2004). The structure of a social science collaboration network: Disciplinary cohesion from 1963 to 1999. *American Sociological Review*, 69(2), 213–238.

Newman, M. E. J. (2001). The structure of scientific collaboration networks. *Proceedings of the National Academy of Sciences*, 98(2), 404–409.

Newman, M. E. J. (2004). Coauthorship networks and patterns of scientific collaboration. *Proceedings of the National Academy of Sciences*, 101(suppl 1), 5200–5205.

Pan, R. K., Kaski, K., & Fortunato, S. (2012). World citation and collaboration networks: Uncovering the role of geography in science. *Scientific Reports*, 2, 902.

Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. *arXiv preprint arXiv:2205.01833*.

Schulz, C., Mazloumian, A., Petersen, A. M., Penner, O., & Helbing, D. (2014). Exploiting citation networks for large-scale author name disambiguation. *EPJ Data Science*, 3(1), 1–14.

Seeber, M., et al. (2019). Self-citations as strategic response to the use of metrics for career decisions. *Research Policy*, 48(9), 103688.

Seglen, P. O. (1997). Why the impact factor of journals should not be used for evaluating research. *BMJ*, 314(7079), 498.

Shen, H. W., & Barabási, A. L. (2014). Collective credit allocation in science. *Proceedings of the National Academy of Sciences*, 111(34), 12325–12330.

Smaldino, P. E., & McElreath, R. (2016). The natural selection of bad science. *Royal Society Open Science*, 3(9), 160384.

Wagner, C. S., & Leydesdorff, L. (2005). Network structure, self-organization, and the growth of international collaboration in science. *Research Policy*, 34(10), 1608–1618.

Wallace, M. L., Larivière, V., & Gingras, Y. (2012). A small world of citations? The influence of collaboration networks on citation practices. *PLoS ONE*, 7(3), e33339.

Waltman, L. (2016). A review of the literature on citation impact indicators. *Journal of Informetrics*, 10(2), 365–391.

Waltman, L., & van Eck, N. J. (2012). The inconsistency of the h-index. *Journal of the American Society for Information Science and Technology*, 63(2), 406–415.

Waltman, L., van Eck, N. J., van Leeuwen, T. N., Visser, M. S., & van Raan, A. F. J. (2011). Towards a new crown indicator: Some theoretical considerations. *Journal of Informetrics*, 5(1), 37–47.

Wilsdon, J., et al. (2015). *The Metric Tide: Report of the Independent Review of the Role of Metrics in Research Assessment and Management*. HEFCE.

Zheng, L., et al. (2025). Understanding discrepancies in the coverage of OpenAlex: The case of China. *Journal of the Association for Information Science and Technology*.

Zuccala, A. (2006). Modeling the invisible college. *Journal of the American Society for Information Science and Technology*, 57(2), 152–168.


"""
