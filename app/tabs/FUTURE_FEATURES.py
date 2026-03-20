"""
citation-constellation/app/FUTURE_FEATURES.py
=======================================
Information about how BARON and HEROCON work
"""

FUTURE_FEATURES = """


**Future Features**

### Phase 4: Venue Governance Detection via Local LLM and AI Agent

This phase will introduce detection of citations from academic venues where a researcher or their professional network holds governance roles. The system will identify connections through editorial boards, program committees, and organizing committees of journals and conferences, revealing structural pathways where venue governance relationships might influence citation patterns.

**Technical Implementation**

- A quantized Qwen 3.5 8B language model will be deployed via llama.cpp on Kubernetes to serve as a local extraction engine
- An AI agent pipeline will scrape venue editorial board pages using httpx and Cloudflare Crawl API for JavaScript-rendered sites
- Raw HTML will be fed to the local LLM through an OpenAI-compatible API endpoint to extract structured member names, roles, institutions, and ORCID identifiers
- Entity resolution algorithms will match extracted governance members against OpenAlex author profiles using ORCID and affiliation data
- High-confidence matches will be stored in a persistent PostgreSQL database with timestamped entries and confidence scores
- Nightly Kubernetes CronJobs will refresh governance data older than 12 months and queue new venues for incremental database expansion
- The classification layer will cross-reference each citing venue against the database to detect self-governance, editor co-authorship, and institutional editorial connections

---

### Phase 5: Field Normalization and Comparative Analytics

- The system will classify researchers into fields using OpenAlex concept tags and hierarchical topic classifications
- Peer cohorts will be automatically sampled by matching field, career length, and publication volume parameters
- Bootstrap resampling methods will calculate confidence intervals for BARON and HEROCON scores to reflect statistical uncertainty
- Field-normalized percentile ranks will be computed by comparing individual scores against peer cohort distributions
- A web-based dashboard will render interactive visualizations of network structure, ego graphs, and temporal career trajectories
- A REST API endpoint will expose score computation and audit data for programmatic access and integration

---

### Phase 6: Validation and Advanced Diagnostics

- Sensitivity analysis will be conducted to test score stability under perturbations of the HEROCON weights and decay constants
- Alternative imputation strategies for UNKNOWN classifications will be evaluated to assess selection bias effects
- Cross-validation studies will correlate network classifications with ground-truth citation motivation surveys
- Temporal trajectory analysis will compute rolling BARON/HEROCON scores across career years to identify trend patterns
- Multi-source data fusion will integrate Semantic Scholar, CrossRef, and DBLP to improve coverage and reduce single-source dependency
- Empirical calibration frameworks will be established to ground HEROCON weights in observed citation behavior rather than theoretical defaults
"""
