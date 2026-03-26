"""
citation-constellation/app/tabs/HOW_TO_RUN.py
=======================================
Information about how to run this tool
"""

HOW_TO_RUN = """


# How to Run Here & Install Locally


> 📸 **New here?** See **Section 5** at the bottom for demo screenshots of what the output looks like.

---

## 1. Using the Web App

This interface runs on [SciLifeLab Serve](https://serve.scilifelab.se) and requires no installation.

### Running a New Analysis

Click the **"🔍 Run Analysis"** tab.

1.  **Enter a researcher identifier** in the input field:
    *   An ORCID (e.g., `0000-0000-0000-0000`)
    *   An OpenAlex ID (e.g., `A0000000000`)
    *   You may paste the full URL (e.g., `https://orcid.org/...` or `https://openalex.org/authors/A...`) — the tool extracts the ID automatically.
2.  *(Optional)* **Set a career start year** to exclude older publications. This helps resolve name collisions if OpenAlex has merged profiles of researchers with similar names. You can verify the correct year by checking the researcher's first entry on Google Scholar or ORCID.
3.  *(Optional)* **Adjust the co-author graph depth** (default: 2):
    *   **Depth 1** — Only direct co-authors are in-group. Strictest. Best for large, loosely collaborative fields.
    *   **Depth 2** — Co-authors + their co-authors. Recommended default.
    *   **Depth 3** — Three hops. Largest in-group. Best for small, tightly-knit fields.
4.  *(Optional)* **Enable "Wait for my validation"** to review and confirm potentially misattributed papers flagged by ORCID validation before they are excluded from scoring.
5.  *(Optional)* **Upload a custom HEROCON weights JSON** file to override the default classification weights (see the Advanced section below for the file format).
6.  Click **"Run Analysis"**.

The tool will fetch data from OpenAlex and ORCID, then process it through all three detection phases. Results display BARON and HEROCON scores, interactive visualizations (donut chart, co-author network graph, career trajectory), and a downloadable JSON audit report.

**Rate limit:** 10 analyses per hour per session.

### Visualizing Existing Reports

Click the **"📊 View Existing Audits"** tab to upload previously downloaded JSON audit reports.

*   **Single file** → Full visualization: score breakdown donut, co-author network graph, career trajectory chart, and full citation classification table.
*   **Multiple files** → Side-by-side comparison: score comparison table, overlaid BARON trajectory chart, overlaid HEROCON trajectory chart, plus individual report details in expandable sections.

You can visualize your own past results or audit files shared by colleagues without waiting for computation.

> 💡 **Trajectory chart requires the `--trajectory` flag.** If you generated the audit file using the CLI without the `--trajectory` or `-t` flag, the trajectory chart will not be available in the web app. All other visualizations will still work normally.

---

## 2. Installing & Using the CLI

For command-line use, batch processing, or large profiles, install the tool locally.

### Installation

```bash
git clone https://github.com/citation-cosmograph/citation-constellation.git
cd citation-constellation
pip install -r requirements.txt
```

**Requirements:** Python 3.11+, pip.

### The Three Phases

Citation-Constellation provides three progressive analysis phases. Each builds on the previous:

| Phase | Script | Detects | Scores |
|-------|--------|---------|--------|
| **Phase 1** | `phase1.py` | Self-citations only | BARON v0.1 |
| **Phase 2** | `phase2.py` | Self + co-author network | BARON v0.2 + HEROCON v0.2 |
| **Phase 3** | `phase3.py` | Self + co-authors + institutional affiliations | BARON v0.3 + HEROCON v0.3 |

**Phase 3 is recommended** for the most comprehensive analysis. Phases 1 and 2 are useful for quick checks or when you want to see the progressive impact of each detection layer.

### Quick Start (Phase 3 — Recommended)

```bash
# Using ORCID (with trajectory for web visualization)
python phase3.py --orcid 0000-0000-0000-0000 --trajectory

# Using OpenAlex ID
python phase3.py --openalex-id A0000000000 --trajectory

# Full example with all common options
python phase3.py --orcid 0000-0000-0000-0000 --since 2010 --depth 2 --trajectory --export results.json
```

### Running Phase 1 (Self-Citation Baseline)

The fastest phase — classifies citations as SELF or NON_SELF only.

```bash
python phase1.py --orcid 0000-0000-0000-0000
python phase1.py --openalex-id A0000000000
```

**Phase 1 options:**

| Flag | Description |
|------|-------------|
| `--orcid` | Researcher ORCID identifier |
| `--openalex-id` | OpenAlex author ID (e.g., `A0000000000`) |
| `--since YEAR` | Exclude works published before this year |
| `--trajectory` / `-t` | Compute and display cumulative career trajectory |
| `--export FILE` | Export summary to a JSON file |
| `--no-audit` | Skip audit file generation (not recommended) |
| `--no-orcid-check` | Skip ORCID cross-validation |
| `--verbose` / `-v` | Enable verbose logging |

### Running Phase 2 (Co-Author Network)

Builds a co-author graph and classifies citations by graph distance.

```bash
python phase2.py --orcid 0000-0000-0000-0000 --trajectory
python phase2.py --orcid 0000-0000-0000-0000 --depth 3 --trajectory
```

**Phase 2 adds these options on top of Phase 1:**

| Flag | Description |
|------|-------------|
| `--depth` / `-d` | Co-author graph depth: 1, 2, or 3 (default: 2) |
| `--herocon-weights FILE` | Path to custom HEROCON weights JSON file |

### Running Phase 3 (Affiliation Matching)

The most comprehensive analysis. Adds temporal institutional affiliation matching using ROR hierarchy data.

```bash
python phase3.py --orcid 0000-0000-0000-0000 --trajectory
python phase3.py --orcid 0000-0000-0000-0000 --depth 2 --since 2010 --trajectory --export results.json
python phase3.py --orcid 0000-0000-0000-0000 --confirm --trajectory
```

**Phase 3 adds this option on top of Phase 2:**

| Flag | Description |
|------|-------------|
| `--confirm` / `-c` | Interactive review: inspect ORCID-flagged works and choose which to exclude before scoring. Accepts `all`, `none`, specific indices (`1,3,5`), or ranges (`1-3,5`). |

### Complete CLI Reference (Phase 3)

```bash
python phase3.py \\
    --orcid 0000-0000-0000-0000 \\   # OR --openalex-id A0000000000
    --since 2010 \\                    # Exclude pre-2010 works
    --depth 2 \\                       # Co-author graph depth (1/2/3)
    --trajectory \\                    # Compute career trajectory (IMPORTANT for web viz)
    --confirm \\                       # Interactive review of flagged works
    --herocon-weights weights.json \\  # Custom HEROCON weights
    --export results.json \\           # Export summary JSON
    --no-orcid-check \\                # Skip ORCID validation
    --no-audit \\                      # Skip audit file (not recommended)
    --verbose                          # Verbose logging
```

### Output Files

*   **Console:** Scores, progressive breakdown (Phase 1 → 2 → 3 deltas), and summary print to stdout.
*   **Audit trail:** A comprehensive JSON file is saved to `./audits/` by default. The filename encodes the researcher name, scores, identifier, and timestamp. Example:
    ```
    Mahbub-Ul-Alam_Citation-Constellation-Audit-Report_BARON-Score_84.9_HEROCON-Score_85.9_ORCID-ID_0000-0002-1101-3793_Generated-Time_20260315_215252.json
    ```
*   **Export JSON** (with `--export`): A lighter summary file with scores, breakdown, and optional trajectory — without the full citation-level audit detail.

### Custom HEROCON Weights

You can override the default HEROCON scoring weights by providing a JSON file with `--herocon-weights`. Any classification not specified falls back to its default value.

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

**Default weights** (for reference):

| Classification | Default Weight | Meaning |
|----------------|---------------|---------|
| `SELF` | 0.0 | No credit |
| `DIRECT_COAUTHOR` | 0.2 | Low partial credit |
| `TRANSITIVE_COAUTHOR` | 0.5 | Moderate partial credit |
| `SAME_DEPT` | 0.1 | Very low credit |
| `SAME_INSTITUTION` | 0.4 | Moderate credit |
| `SAME_PARENT_ORG` | 0.7 | High credit |
| `EXTERNAL` | 1.0 | Full credit |
| `NON_SELF` | 1.0 | Phase 1 fallback |

> ⚠️ These defaults are **experimental heuristics**, not empirically calibrated values. You are encouraged to test custom weights if you have domain-specific reasoning to support them.

### ORCID Cross-Validation

When a researcher has an ORCID, the tool automatically cross-validates OpenAlex's work list against the ORCID record:

*   **High ORCID coverage (≥70%):** ORCID is used as a hard filter — only works found in both ORCID and OpenAlex enter the scoring pipeline.
*   **Low ORCID coverage (<70%):** All OpenAlex works are kept, but affiliation anomaly detection flags works from institutions never associated with the researcher. Flagged works are excluded from scoring.

Use `--confirm` to interactively review flagged works before they are excluded. Use `--no-orcid-check` to skip validation entirely.

> 💡 **Publication span warning:** If the span between the earliest and latest publication exceeds 25 years, the tool warns that this may indicate a name collision. Use `--since YEAR` to exclude pre-career works.

---

## 3. Installing the Web App Locally

You can run this Gradio interface on your own machine. The local web interface provides the same experience as the hosted version.

### Option A: Run with Python (simplest)

No Docker needed — just Python.

```bash
cd citation-constellation/
pip install -r app/requirements.txt
python app/main.py
```

Open your browser to `http://localhost:7860`.

**Requirements:** Python 3.11+, pip.

---

### Option B & C: Running with Docker

Options B (build from source) and C (prebuilt image) both require Docker. If you don't have Docker installed yet, follow the instructions below for your operating system.

#### Installing Docker Desktop

<details>
<summary><strong>🪟 Windows</strong></summary>

1.  **System requirements:** Windows 10 (build 19041+) or Windows 11, with WSL 2 enabled.
2.  **Enable WSL 2** (if not already):
    ```powershell
    wsl --install
    ```
    Restart your computer after this completes.
3.  **Download Docker Desktop** from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
4.  Run the installer (`.exe`) and follow the prompts. Ensure **"Use WSL 2 instead of Hyper-V"** is checked.
5.  Restart your computer when prompted.
6.  Open **Docker Desktop** from the Start menu and wait for the engine to start (the whale icon in the system tray turns steady).
7.  **Verify** in a terminal (PowerShell or Command Prompt):
    ```powershell
    docker --version
    docker run hello-world
    ```

> 💡 If you see errors about WSL 2, run `wsl --update` in an elevated PowerShell and restart Docker Desktop.

</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

1.  **System requirements:** macOS 12 (Monterey) or later. Works on both Intel and Apple Silicon (M1/M2/M3/M4) Macs.
2.  **Download Docker Desktop** from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/). Choose the correct chip:
    *   **Apple Silicon** (M1/M2/M3/M4) → "Mac with Apple chip"
    *   **Intel** → "Mac with Intel chip"
3.  Open the downloaded `.dmg` file and drag **Docker** to the **Applications** folder.
4.  Launch **Docker** from Applications. Grant the permissions it requests (privileged helper, network).
5.  Wait for the whale icon in the menu bar to stop animating.
6.  **Verify** in Terminal:
    ```bash
    docker --version
    docker run hello-world
    ```

> 💡 On Apple Silicon Macs, Docker runs both `linux/arm64` and `linux/amd64` images (the latter via Rosetta 2 emulation). Native `arm64` images will be significantly faster.

</details>

<details>
<summary><strong>🐧 Linux (Ubuntu / Debian)</strong></summary>

You can install either **Docker Desktop** (GUI) or **Docker Engine** (CLI only). For a server or headless machine, Docker Engine is lighter.

**Option 1: Docker Desktop (GUI)**

1.  Download the `.deb` package from [docs.docker.com/desktop/install/linux/ubuntu](https://docs.docker.com/desktop/install/linux/ubuntu/).
2.  Install:
    ```bash
    sudo apt update
    sudo apt install ./docker-desktop-<version>-amd64.deb
    ```
3.  Launch Docker Desktop from your application menu.

**Option 2: Docker Engine (CLI only — recommended for servers)**

```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc 2>/dev/null

# Add Docker's official GPG key and repository
sudo apt update
sudo apt install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Run Docker without sudo (optional but recommended)
sudo usermod -aG docker $USER
newgrp docker
```

**Verify:**
```bash
docker --version
docker run hello-world
```

> 💡 For **Fedora**, **Arch**, or other distros, see the official docs at [docs.docker.com/engine/install](https://docs.docker.com/engine/install/).

</details>

---

### Option B: Build Docker Image from Source

Clone the repo and build the image for your platform.

**Single-platform build** (auto-detects your architecture):

```bash
cd citation-constellation

docker build -t citation-constellation:v0.3 .
docker run --rm -it -p 7860:7860 citation-constellation:v0.3
```

**Explicit platform builds:**

```bash
# Intel / AMD (most Windows PCs, older Macs, Linux servers)
docker build --platform linux/amd64 -t citation-constellation:v0.3-amd64 .

# Apple Silicon (M1/M2/M3/M4 Macs) or ARM servers (AWS Graviton, Raspberry Pi)
docker build --platform linux/arm64 -t citation-constellation:v0.3-arm64 .
```

**Multi-platform build** (build once, run anywhere — requires `docker buildx`):

```bash
# Create a multi-platform builder (one-time setup)
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap

# Build and push for both architectures
docker buildx build \\
    --platform linux/amd64,linux/arm64 \\
    -t citation-constellation:v0.3 \\
    --push .

# Or load locally (single platform at a time)
docker buildx build \\
    --platform linux/amd64 \\
    -t citation-constellation:v0.3 \\
    --load .
```

**Run the container:**

```bash
docker run --rm -it -p 7860:7860 citation-constellation:v0.3
```

Open your browser to `http://localhost:7860`.

> 💡 **Which platform am I?**
> *   **Windows (most PCs):** `linux/amd64`
> *   **Mac with Intel chip:** `linux/amd64`
> *   **Mac with Apple Silicon (M1/M2/M3/M4):** `linux/arm64`
> *   **Linux x86_64 server:** `linux/amd64`
> *   **Linux ARM server (AWS Graviton, Raspberry Pi 4+):** `linux/arm64`

---

### Option C: Use the Prebuilt Image

Pull and run the prebuilt image from Docker Hub:

```bash
# Pull the image (Docker auto-selects the correct architecture)
docker pull mahbub1969/citation-constellation:v1

# Run the container
docker run --rm -it -p 7860:7860 mahbub1969/citation-constellation:v1
```

Open your browser to `http://localhost:7860`.

> 💡 If the prebuilt image doesn't support your architecture, use **Option B** to build from source instead.

---

### Docker Troubleshooting

| Problem | Solution |
|---------|----------|
| `docker: command not found` | Docker is not installed or not in PATH. Follow the installation steps above. |
| `permission denied` on Linux | Run `sudo usermod -aG docker $USER` then log out and back in, or prefix commands with `sudo`. |
| Port 7860 already in use | Change the host port: `docker run --rm -it -p 8080:7860 citation-constellation:v0.3` then open `http://localhost:8080`. |
| Slow on Apple Silicon | Make sure you're building/pulling the `linux/arm64` image, not `linux/amd64` (which runs under Rosetta emulation). |
| `WSL 2` errors on Windows | Run `wsl --update` in an elevated PowerShell, restart Docker Desktop. |
| Build fails with `buildx` | Ensure the buildx plugin is installed: `docker buildx version`. If missing, update Docker Desktop to the latest version. |

---

## 4. Tips & Best Practices

### When to Use the CLI vs. the Web App

| Scenario | Recommended |
|----------|-------------|
| Quick one-off analysis (< 2,000 citations) | Web app |
| Large profiles (4,000+ citations or 200+ publications) | CLI |
| Batch analysis of multiple researchers | CLI |
| Interactive review of flagged works | Either (web: checkbox UI; CLI: `--confirm`) |
| Comparing multiple researchers | Web app (upload multiple JSONs) |
| Sharing results with colleagues | Either (share the audit JSON) |

> 💡 **Why CLI for large profiles?** The web app has internal timeouts to keep the server responsive. The CLI has **no timeout limits** and provides real-time progress bars, so it can handle arbitrarily large profiles. Analysis time scales with both **citation count** (more API calls to fetch citing works) and **publication count** (larger co-author network to traverse). A researcher with 4,000+ citations and 200+ publications can take 15–30 minutes.

### The `--trajectory` Flag

Always use `--trajectory` (or `-t`) when generating audit files via the CLI if you plan to visualize them in the web app. Without this flag, the career trajectory chart will not be available (all other visualizations still work).

```bash
# Always include -t for web visualization
python phase3.py --orcid 0000-0000-0000-0000 -t
```

### Choosing the Right Graph Depth

*   **Depth 1** — Strictest in-group definition. Good for researchers in large, loosely connected fields (e.g., clinical medicine, epidemiology).
*   **Depth 2** — Recommended default. Captures the immediate collaborative circle without over-expanding.
*   **Depth 3** — Widest net. Use for small, tightly-knit fields (e.g., specialized subfields with frequent co-authorship chains).

> 💡 Higher depth = larger in-group = lower BARON score. The gap between BARON and HEROCON reveals how much measured impact depends on the researcher's inner circle.

### Handling Name Collisions

OpenAlex uses algorithmic author disambiguation, which occasionally merges works from different researchers with similar names. Signs of a name collision:

*   The tool prints a **publication span warning** (> 25 years)
*   Works appear from institutions the researcher has never been affiliated with
*   The publication count is significantly higher than expected

**Solutions:**
1.  Use `--since YEAR` to exclude pre-career publications.
2.  Use `--confirm` to interactively review and exclude misattributed works.
3.  Ensure the researcher's ORCID profile is up to date — high ORCID coverage (≥70%) enables hard filtering.

### Understanding Data Quality

The audit report includes a **data quality percentage** and **reliability rating**:

| Quality | Rating | Interpretation |
|---------|--------|----------------|
| ≥ 85% | HIGH | Scores are trustworthy |
| ≥ 70% | MODERATE | Reasonable, but treat with care |
| ≥ 50% | LOW | Significant data gaps |
| < 50% | VERY LOW | Too much missing data for reliable scoring |

Citations classified as `UNKNOWN` (insufficient metadata) are excluded from both the BARON and HEROCON denominators, so missing data does not artificially inflate or deflate scores. The data quality percentage tells you what fraction of citations had enough metadata for classification.

### Reading the BARON-HEROCON Gap

*   **Small gap** (< 3%) → The researcher's impact is overwhelmingly external. In-group citations mostly come from self-citations, which get zero weight in both scores.
*   **Moderate gap** (3–10%) → There is a meaningful inner-circle contribution, but external impact is still dominant.
*   **Large gap** (> 10%) → A significant portion of measured impact comes from the researcher's collaborative network. This is neither good nor bad — it simply characterizes the citation structure.

> ⚠️ BARON and HEROCON measure **citation network structure**, not research quality, impact, or integrity. They should **not** be used for hiring, promotion, or funding decisions.

---

## 5. Demo: What the Output Looks Like

Below are screenshots from a real analysis to help you understand each part of the output before you run your own.

### Ethical Notice

Every analysis output begins with a prominent ethical disclaimer, reinforcing that BARON and HEROCON measure citation network structure — not research quality, impact, or integrity.

<img src="/gradio_api/file=app/assets/ethical-note.png" alt="Ethical notice displayed at the top of every analysis output" style="max-width: 100%; height: auto; display: block;">

---

### Score Panel

The score panel presents BARON and HEROCON scores alongside key summary statistics: total citations, classifiable citations, the BARON–HEROCON gap, and a data quality reliability rating.

**Web Interface**

<img src="/gradio_api/file=app/assets/score-panel-tool.png" alt="Score panel — Web Interface" style="max-width: 100%; height: auto; display: block;">

**Command Line Interface**

<img src="/gradio_api/file=app/assets/score-panel-tool-cli.png" alt="Score panel — Command Line Interface" style="max-width: 100%; height: auto; display: block;">

---

### Classification Breakdown Donut Chart

A proportional breakdown of citation origins across all classification categories, with BARON and HEROCON scores displayed in the center.

<img src="/gradio_api/file=app/assets/classification-breakdown.png" alt="Classification breakdown donut chart" style="max-width: 100%; height: auto; display: block;">

---

### Co-Author Network Graph

The interactive co-author network graph renders the target researcher as a gold node, direct co-authors in crimson (sized by shared publications), and transitive co-authors in blue. Hover over any node for details. Networks exceeding 150 nodes are automatically pruned.

<img src="/gradio_api/file=app/assets/co-author-network.png" alt="Co-author network graph (overview)" style="max-width: 100%; height: auto; display: block;">

<img src="/gradio_api/file=app/assets/co-author-network2.png" alt="Co-author network graph (detail)" style="max-width: 100%; height: auto; display: block;">

---

### Classification Summary Table

Each citation category with its count, percentage of classifiable citations, and the HEROCON weight applied.

**Web Interface**

<img src="/gradio_api/file=app/assets/classification-summary.png" alt="Classification summary — Web Interface" style="max-width: 100%; height: auto; display: block;">

**Command Line Interface**

<img src="/gradio_api/file=app/assets/classification-summary-cli.png" alt="Classification summary — Command Line Interface" style="max-width: 100%; height: auto; display: block;">

---

### Career Trajectory Chart

Cumulative BARON and HEROCON scores over time as dual lines, with a shaded gap region between them. Stacked bars beneath show annual citation volume.

**Web Interface**

<img src="/gradio_api/file=app/assets/career-trajectory.png" alt="Career trajectory chart — Web Interface" style="max-width: 100%; height: auto; display: block;">

**Command Line Interface**

<img src="/gradio_api/file=app/assets/career-trajectory-cli.png" alt="Career trajectory chart — Command Line Interface" style="max-width: 100%; height: auto; display: block;">

---

### Full Citation Table (Audit Trail)

Every individual citation with its classification, confidence level, detection phase, and a human-readable rationale. Any classification can be inspected, questioned, and contested.

<img src="/gradio_api/file=app/assets/citation-table.png" alt="Full citation table from the audit trail" style="max-width: 100%; height: auto; display: block;">

---

### Comparison View

Upload multiple audit JSON files to the **View Existing Audits** tab for side-by-side structural analysis. (Researcher names shown below have been anonymized.)

**Comparison Table**

<img src="/gradio_api/file=app/assets/comparison-table.png" alt="Comparison table" style="max-width: 100%; height: auto; display: block;">

**BARON Trajectory Comparison**

<img src="/gradio_api/file=app/assets/baron-trajectory-comparison.png" alt="BARON trajectory comparison" style="max-width: 100%; height: auto; display: block;">

**HEROCON Trajectory Comparison**

<img src="/gradio_api/file=app/assets/herocon-trajectory-comparison.png" alt="HEROCON trajectory comparison" style="max-width: 100%; height: auto; display: block;">

**Individual Reports within Comparison View**

<img src="/gradio_api/file=app/assets/individual-reports.png" alt="Individual reports within the comparison view" style="max-width: 100%; height: auto; display: block;">

---

### Phased Architecture

The detection pipeline progressively deepens from self-citation through co-authorship, affiliation matching, and venue governance.

<img src="/gradio_api/file=app/assets/phased-architecture.png" alt="Phased implementation architecture" style="max-width: 100%; height: auto; display: block;">

---

### Development Roadmap

<img src="/gradio_api/file=app/assets/project-plan.png" alt="Development roadmap" style="max-width: 100%; height: auto; display: block;">
"""
