"""
citation-constellation/app/tabs/BARON_and_HEROCON.py
=======================================
Information about how BARON and HEROCON work
"""

BARON_and_HEROCON = """


<div style="background:linear-gradient(160deg,#0a0a1a 0%,#0f1a2e 40%,#0d0d20 100%);font-family:Inter,sans-serif;color:#e0e0e0;padding:28px 24px;max-width:1100px;margin:0 auto;border-radius:12px;">
<div style="text-align:center;margin-bottom:18px;">
<div style="font-size:1.6rem;font-weight:800;letter-spacing:2px;background:linear-gradient(135deg,#f4e4c1,#d4af37 40%,#9370db);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;">Citation-Constellation</div>
<div style="font-size:.8rem;color:rgba(255,255,255,.55);margin-top:3px;">Phased Implementation Architecture</div>
</div>
<div style="display:flex;justify-content:center;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
<div style="background:linear-gradient(135deg,rgba(212,175,55,.12),rgba(147,112,219,.12));border:1px solid rgba(255,255,255,.2);border-radius:8px;padding:8px 14px;text-align:center;">
<div style="font-size:1rem;">🔑</div>
<div style="font-size:.7rem;font-weight:700;color:#f4e4c1;">ORCID / OpenAlex ID</div>
</div>
<div style="color:rgba(255,255,255,.3);">→</div>
<div style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:8px 14px;text-align:center;">
<div style="font-size:1rem;">🛡️</div>
<div style="font-size:.7rem;font-weight:700;color:#a8d5a2;">ORCID Validation</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.5);margin-top:1px;">Smart two-mode system</div>
</div>
<div style="color:rgba(255,255,255,.3);">→</div>
<div style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:8px 14px;text-align:center;">
<div style="font-size:1rem;">⚡</div>
<div style="font-size:.7rem;font-weight:700;color:#a8d5a2;">OpenAlex + ROR</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.5);margin-top:1px;">Async · rate-limited · retry</div>
</div>
</div>
<div style="display:flex;justify-content:center;height:20px;margin-bottom:12px;">
<div style="width:2px;height:100%;background:linear-gradient(180deg,rgba(212,175,55,.4),rgba(147,112,219,.4));"></div>
</div>
<div style="text-align:center;font-size:.65rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,255,255,.45);margin:12px 0 8px;">Detection Phases — Each Adds a Layer</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:12px;">
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(76,175,80,.08);border:1.5px solid rgba(76,175,80,.3);">
<div style="font-size:.55rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#4caf50;background:rgba(76,175,80,.15);">Phase 1</div>
<div style="font-size:1.3rem;margin:3px 0;">👤</div>
<div style="font-size:.8rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Self-Citation</div>
<div style="font-size:.62rem;color:rgba(255,255,255,.6);line-height:1.4;flex-grow:1;">Author ID match. Binary SELF / NON_SELF.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.58rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#a5d6a7;background:rgba(76,175,80,.1);">2 classes</div>
<br><span style="font-size:.5rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#1b5e20;background:#4caf50;">✓ Done</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(76,175,80,.08);border:1.5px solid rgba(76,175,80,.3);">
<div style="font-size:.55rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#4caf50;background:rgba(76,175,80,.15);">Phase 2</div>
<div style="font-size:1.3rem;margin:3px 0;">🔗</div>
<div style="font-size:.8rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Co-Author Network</div>
<div style="font-size:.62rem;color:rgba(255,255,255,.6);line-height:1.4;flex-grow:1;">BFS graph · temporal decay · depth 1–3. Introduces HEROCON.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.58rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#a5d6a7;background:rgba(76,175,80,.1);">4 classes</div>
<br><span style="font-size:.5rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#1b5e20;background:#4caf50;">✓ Done</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(76,175,80,.08);border:1.5px solid rgba(76,175,80,.3);">
<div style="font-size:.55rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#4caf50;background:rgba(76,175,80,.15);">Phase 3</div>
<div style="font-size:1.3rem;margin:3px 0;">🏛️</div>
<div style="font-size:.8rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Affiliation</div>
<div style="font-size:.62rem;color:rgba(255,255,255,.6);line-height:1.4;flex-grow:1;">Temporal ROR hierarchy. Dept / institution / parent org. UNKNOWN class.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.58rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#a5d6a7;background:rgba(76,175,80,.1);">7 classes</div>
<br><span style="font-size:.5rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#1b5e20;background:#4caf50;">✓ Done</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(255,183,77,.08);border:1.5px solid rgba(255,183,77,.3);">
<div style="font-size:.55rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#ffb74d;background:rgba(255,183,77,.15);">Phase 4</div>
<div style="font-size:1.3rem;margin:3px 0;">🤖</div>
<div style="font-size:.8rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Venue Governance</div>
<div style="font-size:.62rem;color:rgba(255,255,255,.6);line-height:1.4;flex-grow:1;">Local LLM extraction. Editorial boards & committees. Persistent DB.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.58rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#ffe0b2;background:rgba(255,183,77,.1);">11 classes</div>
<br><span style="font-size:.5rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#4e342e;background:#ffb74d;">🔧 Building</span>
</div>
</div>
<div style="border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;align-items:center;min-height:150px;background:rgba(144,202,249,.06);border:1.5px dashed rgba(144,202,249,.25);">
<div style="font-size:.55rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;padding:2px 7px;border-radius:4px;margin-bottom:4px;color:#90caf9;background:rgba(144,202,249,.15);">Phase 5</div>
<div style="font-size:1.3rem;margin:3px 0;">📊</div>
<div style="font-size:.8rem;font-weight:700;color:#fff;line-height:1.2;margin-bottom:3px;">Normalization</div>
<div style="font-size:.62rem;color:rgba(255,255,255,.6);line-height:1.4;flex-grow:1;">Percentile ranks. Peer cohorts. Confidence intervals.</div>
<div style="margin-top:auto;padding-top:5px;">
<div style="font-size:.58rem;font-weight:600;padding:2px 6px;border-radius:4px;color:#bbdefb;background:rgba(144,202,249,.1);">Percentiles</div>
<br><span style="font-size:.5rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-top:4px;padding:2px 5px;border-radius:3px;display:inline-block;color:#0d47a1;background:#90caf9;">📋 Planned</span>
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
<div style="font-size:.6rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-top:2px;color:rgba(255,255,255,.5);">Strict · Binary</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.4);font-family:monospace;margin-top:4px;">external ÷ classifiable × 100</div>
</div>
<div style="border-radius:10px;padding:12px 24px;text-align:center;min-width:170px;background:linear-gradient(135deg,rgba(212,175,55,.06),rgba(147,112,219,.06));border:1px solid rgba(255,255,255,.15);">
<div style="font-size:1.15rem;font-weight:900;letter-spacing:2px;background:linear-gradient(90deg,#d4af37,#9370db);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:.9rem;">THE GAP</div>
<div style="font-size:.6rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-top:2px;color:rgba(255,255,255,.5);">Inner-circle diagnostic</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.4);font-family:monospace;margin-top:4px;">HEROCON − BARON</div>
</div>
<div style="border-radius:10px;padding:12px 24px;text-align:center;min-width:170px;background:rgba(147,112,219,.1);border:1.5px solid rgba(147,112,219,.35);">
<div style="font-size:1.15rem;font-weight:900;letter-spacing:2px;color:#9370db;">HEROCON</div>
<div style="font-size:.6rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-top:2px;color:rgba(255,255,255,.5);">Graduated · Weighted</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.4);font-family:monospace;margin-top:4px;">Σ weights ÷ classifiable × 100</div>
</div>
</div>
<div style="display:flex;justify-content:center;height:20px;margin-bottom:12px;">
<div style="width:2px;height:100%;background:linear-gradient(180deg,rgba(212,175,55,.4),rgba(147,112,219,.4));"></div>
</div>
<div style="text-align:center;font-size:.65rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,255,255,.45);margin:12px 0 8px;">Outputs — All with Audit Trail & Disclaimer</div>
<div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-bottom:16px;">
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">💻</div>
<div style="font-size:.7rem;font-weight:700;color:#fff;">CLI</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.5);">Rich terminal · progressive</div>
</div>
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">📄</div>
<div style="font-size:.7rem;font-weight:700;color:#fff;">JSON Audit</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.5);">Every decision documented</div>
</div>
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">🌐</div>
<div style="font-size:.7rem;font-weight:700;color:#fff;">Web UI</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.5);">No-code · interactive</div>
</div>
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;">
<div style="font-size:1rem;">📥</div>
<div style="font-size:.7rem;font-weight:700;color:#fff;">Export</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.5);">Portable · reusable</div>
</div>
</div>
<div style="margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,.08);">
<div style="text-align:center;font-size:.65rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,183,77,.6);margin:12px 0 8px;">Phase 4 Ecosystem</div>
<div style="display:flex;justify-content:center;align-items:center;gap:0;">
<div style="border-radius:10px;padding:12px 16px;text-align:center;min-width:160px;background:rgba(147,112,219,.08);border:1px solid rgba(147,112,219,.25);">
<div style="font-size:1.3rem;">🌟</div>
<div style="font-size:.85rem;font-weight:800;letter-spacing:1px;color:#b39ddb;">Pulsar</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.55);">The Signal</div>
<div style="font-size:.52rem;color:rgba(255,255,255,.4);font-family:monospace;line-height:1.4;margin-top:3px;">Qwen 3.5 8B · llama.cpp · k8s</div>
</div>
<div style="font-size:1.3rem;color:rgba(255,255,255,.25);padding:0 8px;">→</div>
<div style="border-radius:10px;padding:12px 16px;text-align:center;min-width:160px;background:rgba(100,181,246,.08);border:1px solid rgba(100,181,246,.25);">
<div style="font-size:1.3rem;">🔭</div>
<div style="font-size:.85rem;font-weight:800;letter-spacing:1px;color:#90caf9;">Astrolabe</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.55);">The Instrument</div>
<div style="font-size:.52rem;color:rgba(255,255,255,.4);font-family:monospace;line-height:1.4;margin-top:3px;">Scrape · extract · resolve</div>
</div>
<div style="font-size:1.3rem;color:rgba(255,255,255,.25);padding:0 8px;">→</div>
<div style="border-radius:10px;padding:12px 16px;text-align:center;min-width:160px;background:rgba(212,175,55,.08);border:1px solid rgba(212,175,55,.25);">
<div style="font-size:1.3rem;">✨</div>
<div style="font-size:.85rem;font-weight:800;letter-spacing:1px;color:#f4e4c1;">Constellation</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.55);">The Map</div>
<div style="font-size:.52rem;color:rgba(255,255,255,.4);font-family:monospace;line-height:1.4;margin-top:3px;">VENUE_* · BARON · HEROCON</div>
</div>
</div>
</div>
<div style="display:flex;justify-content:center;gap:14px;margin-top:14px;flex-wrap:wrap;">
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">OpenAlex</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">ORCID</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">ROR</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">Cloudflare Crawl</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;text-transform:uppercase;">Free</div>
</div>
</div>
<div style="text-align:center;margin-top:16px;font-size:.65rem;color:rgba(255,255,255,.45);font-style:italic;max-width:700px;margin-left:auto;margin-right:auto;line-height:1.5;">
<strong style="color:rgba(255,255,255,.6);font-style:normal;">Figure:</strong> Phased implementation architecture. Phases 1–3 are complete and available via CLI and web interface. Phase 4 (venue governance via local LLM) is under development. Phase 5 (field normalization) is planned.
</div>
</div>


# How BARON and HEROCON Work

BARON and HEROCON are two complementary scores that measure the same thing — how much of a researcher's citation profile comes from outside their immediate professional circle — but they compute it differently.

---

## The Core Idea

Every citation a researcher receives is checked against their professional network. The system looks for connections between the researcher and each citing author across three layers:

1. **Self** — The researcher cited their own work
2. **Co-authors** — Someone they have published with (or a collaborator's collaborator)
3. **Institution** — Colleagues at their university, department, or parent organization

If none of these connections are found, the citation is classified as **External**. If the system lacks sufficient metadata to determine any relationship, the citation is classified as **Unknown** and excluded from scoring entirely.

---

## Classification Hierarchy

Citations are classified using a strict priority order. The first matching rule wins:

| Priority | Classification | Phase | Description | Graph Distance |
|----------|---------------|-------|-------------|----------------|
| 1 | **SELF** | 1 | Target researcher is an author on the citing work | 0 |
| 2 | **DIRECT_COAUTHOR** | 2 | Citing author shared ≥1 publication with target | 1 |
| 3 | **TRANSITIVE_COAUTHOR** | 2 | Citing author is a co-author of a co-author | 2 (or 3) |
| 4 | **SAME_DEPT** | 3 | Same department, no co-authorship detected | — |
| 5 | **SAME_INSTITUTION** | 3 | Same university, different department | — |
| 6 | **SAME_PARENT_ORG** | 3 | Different institutions sharing a parent in ROR hierarchy | — |
| 7 | **UNKNOWN** | 3 | Insufficient metadata for classification | — |
| 8 | **EXTERNAL** | 3 | No co-authorship or institutional connection found | — |

Co-author graph matches always take priority over affiliation matches. A citing author who is both a direct co-author *and* at the same institution is classified as DIRECT_COAUTHOR, not SAME_INSTITUTION.

---

## BARON (Binary)

BARON treats every citation as either inside the researcher's network or outside it. There is no partial credit.

- **In-group** (SELF, DIRECT_COAUTHOR, TRANSITIVE_COAUTHOR, SAME_DEPT, SAME_INSTITUTION, SAME_PARENT_ORG) = **0 points**
- **External** = **1 point**
- **Unknown** = **excluded from both numerator and denominator**

**Formula:**

```
BARON = (External citations ÷ Classifiable citations) × 100
```

where *classifiable = total − unknown*.

A BARON score of 65% means 65% of the researcher's classifiable citations came from people with no detected connection to them.

---

## HEROCON (Graduated)

HEROCON gives partial credit for in-group citations based on how close the connection is. Instead of binary 0 or 1, each classification category has a weight between 0.0 and 1.0.

**Formula:**

```
HEROCON = (Σ weight(citation_i) ÷ Classifiable citations) × 100
```

### Default HEROCON Weights

| Classification | Weight | Rationale |
|----------------|--------|-----------|
| **SELF** | 0.0 | No credit — citing your own work is the strongest in-group signal |
| **SAME_DEPT** | 0.1 | Very low credit — forced proximity with no collaboration |
| **DIRECT_COAUTHOR** | 0.2 | Low credit — active chosen collaboration |
| **SAME_INSTITUTION** | 0.4 | Moderate credit — same university, different department |
| **TRANSITIVE_COAUTHOR** | 0.5 | Moderate credit — friend-of-friend, weaker signal |
| **SAME_PARENT_ORG** | 0.7 | High credit — shared umbrella org (e.g., University of California system) |
| **EXTERNAL** | 1.0 | Full credit — no detected relationship |
| **UNKNOWN** | *excluded* | Not counted in numerator or denominator |

> ⚠️ These defaults are **experimental heuristics**, not empirically calibrated values. You can provide custom weights via `--herocon-weights` (CLI) or the weights upload in the web app. Any classification not specified in your custom file falls back to the default weight.

### Planned Phase 4 Weights

| Classification | Default Weight | Description |
|----------------|---------------|-------------|
| **VENUE_SELF_GOVERNANCE** | 0.05 | Researcher sits on the editorial board of the citing venue |
| **VENUE_EDITOR_COAUTHOR** | 0.15 | A venue editor is a co-author of the target |
| **VENUE_EDITOR_AFFIL** | 0.3 | A venue editor is at the same institution |
| **VENUE_COMMITTEE** | 0.4 | A programme committee member is in the researcher's network |

---

## The Gap: HEROCON − BARON

Since HEROCON gives partial credit where BARON gives zero, HEROCON is always ≥ BARON. The difference between them — **the gap** — reveals how much of a researcher's measured impact flows through their inner circle.

| Gap Size | Interpretation |
|----------|---------------|
| **< 3%** | Most citations are fully external. The inner circle provides minimal boost. |
| **3–10%** | Meaningful inner-circle contribution, but external impact is dominant. |
| **> 10%** | A significant portion of measured impact comes from the collaborative network. |

The gap is neither good nor bad. It characterizes the *structure* of a citation profile, not its quality.

---

## The Detection Phases in Detail

### Phase 1: Self-Citation Detection

The simplest phase. For each incoming citation, the system checks whether the target researcher's OpenAlex author ID appears in the citing work's author list.

- Match → **SELF**
- No match → **NON_SELF** (refined in later phases)

**Output:** BARON v0.1 (self-citation baseline). This is the upper bound — it only decreases as more in-group types are detected.

### Phase 2: Co-Author Network Detection

Builds an undirected co-authorship graph from the target researcher's own publications. Every pair of co-authors on every paper creates (or strengthens) an edge.

**Graph construction:**
- Nodes = all authors who appear on any of the target's publications
- Edges = co-authorship, weighted by number of shared papers and recency

**Co-authorship strength** uses exponential recency decay:
```
strength = shared_papers × exp(-0.1 × years_since_last_collab)
```
This gives a half-life of approximately 7 years. A prolific recent collaborator scores much higher than a one-time co-author from a decade ago. The strength value is logged in the audit trail but does not directly affect the BARON/HEROCON classification — classification is purely distance-based.

**Classification** uses BFS (breadth-first search) from the target researcher:
- Distance 0 → SELF
- Distance 1 → DIRECT_COAUTHOR
- Distance 2 → TRANSITIVE_COAUTHOR (configurable up to depth 3)
- No path → EXTERNAL

**Output:** BARON v0.2 + HEROCON v0.2, shown with the delta from Phase 1.

> 💡 **Important limitation:** The co-author graph is built only from the target researcher's own publications. Co-author A's other collaborators are invisible unless they also appear on the target's papers. This makes the graph a conservative undercount of the true transitive network.

### Phase 3: Affiliation Matching

Adds temporal institutional affiliation matching. A citation from 2022 is matched against where both researchers were affiliated *in 2022*, not where they are today.

**Affiliation timeline** is built from work-level affiliations in OpenAlex: each publication records the author's institution at the time of that publication. Collecting these across all works (target and citing) gives a temporal trace without relying on ORCID employment history (which is often incomplete).

**Institution hierarchy** is resolved using [ROR (Research Organization Registry)](https://ror.org), which provides parent-child relationships between organizations. Two researchers at different universities under the same consortium → SAME_PARENT_ORG.

**Classification priority** (Phase 3 applies after Phase 2):
1. Co-author graph match first (SELF / DIRECT / TRANSITIVE)
2. Affiliation match (SAME_DEPT / SAME_INSTITUTION / SAME_PARENT_ORG)
3. UNKNOWN — insufficient metadata on either side
4. EXTERNAL — data available but no relationship found

**Output:** BARON v0.3 + HEROCON v0.3, shown with progressive deltas from Phase 1 → 2 → 3.

---

## ORCID Cross-Validation

OpenAlex uses algorithmic author disambiguation, which can occasionally merge works from different researchers with similar names. Before scoring, the system cross-references OpenAlex's work list against the researcher's ORCID record.

**Two operating modes** (selected automatically based on ORCID coverage):

| Coverage | Mode | Behavior |
|----------|------|----------|
| **≥ 70%** | Filter | Only works found in *both* ORCID and OpenAlex enter the pipeline |
| **< 70%** | Warning | All OpenAlex works are kept, but affiliation anomaly detection flags suspicious ones |

**Matching strategies** (applied per work):
1. **DOI exact match** — most reliable
2. **Title fuzzy match** (≥ 85% similarity) — fallback for works without DOI

**Affiliation anomaly detection** (in warning mode): flags unverified works whose institutional affiliations never appear anywhere in the researcher's known works. These are likely misattributions from name collisions.

**Publication span warning:** If the span between earliest and latest publication exceeds 25 years, the system warns about possible name collision and suggests `--since YEAR`.

---

## Data Quality & Reliability

Not all citations have enough metadata for classification. When the system cannot determine an affiliation or relationship, it classifies the citation as **UNKNOWN**.

**UNKNOWN citations are excluded** from both BARON and HEROCON denominators. This prevents missing data from artificially inflating or deflating scores.

The **data quality percentage** shows what fraction of citations had sufficient metadata:

| Quality | Rating | Interpretation |
|---------|--------|----------------|
| ≥ 85% | **HIGH** | Scores are trustworthy |
| ≥ 70% | **MODERATE** | Reasonable, but treat with care |
| ≥ 50% | **LOW** | Significant data gaps — interpret cautiously |
| < 50% | **VERY LOW** | Too much missing data for reliable scoring |

---

## The Audit Trail

Every run produces a comprehensive JSON audit file that documents every citation, every classification, and every decision the system made. This is **non-optional by design**. The audit file includes:

- **Researcher profile** — name, ORCID, OpenAlex ID, work count, citation count
- **Every work** — title, year, venue, authors, references (target and citing)
- **Every citation link** — citing work → cited work, with year
- **Every classification** — label, confidence, phase detected, and a human-readable rationale explaining *why* that specific citation was classified the way it was
- **Co-author graph** — full node and edge lists with distances, shared paper counts, and collaboration strength
- **Affiliation timeline** — where the target researcher was affiliated at each point in time
- **Institution hierarchy** — ROR parent-child relationships used for SAME_PARENT_ORG detection
- **ORCID validation results** — which works were verified, which were flagged, which were excluded
- **Score breakdown** — full counts and percentages for every classification category
- **Career trajectory** — cumulative BARON and HEROCON scores by year (when `--trajectory` is used)

The audit file is the single source of truth. Any researcher can open it and verify exactly how their score was computed, down to individual citations.

---

## What BARON and HEROCON Are Not

> ⚠️ **BARON and HEROCON measure citation network structure, not research quality, impact, or integrity.**

They describe *where in the social graph* citations originate. A low score does not mean the research is bad. A high score does not mean the research is good. They should **not** be used for hiring, promotion, or funding decisions.

Every run includes this disclaimer in the console output, the JSON export, and the audit trail.
"""
