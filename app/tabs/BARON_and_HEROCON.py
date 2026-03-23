"""
citation-constellation/app/BARON_and_HEROCON.py
=======================================
Information about how BARON and HEROCON work
"""

BARON_and_HEROCON = """


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
<div style="font-size:.8rem;font-weight:800;letter-spacing:1px;color:#d4af37;">Constellation</div>
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


**How BARON and HEROCON Work**

BARON and HEROCON are two ways to measure the same thing: how much of a researcher's citation profile comes from outside their immediate professional circle. They use the same underlying data but compute differently.

---

### The Core Idea

Every citation a researcher receives gets checked against their professional network. The system looks for connections between the researcher and the citing author across three layers:

1. **Self** – The researcher cited themselves  
2. **Co-authors** – Someone they've published with (or their collaborators)  
3. **Institution** – Colleagues at their university or organization  

If none of these apply, the citation is **External**.

BARON and HEROCON classify citations into these layers differently. BARON is strict. HEROCON is flexible.

---

### BARON (Binary)

BARON treats every citation as either inside the researcher's network or outside it.

- **In-group** (self, co-author, institutional colleague, venue connection) = **0 points**
- **External** = **1 point**

**Calculation:**
```
BARON = (External citations ÷ Classifiable citations) × 100
```

A BARON score of 65% means 65% of the researcher's classifiable citations came from people with no detected connection to them.

*Classifiable citations exclude any citations where the system lacks data to determine the relationship (marked as UNKNOWN).*

---

### HEROCON (Graduated)

HEROCON gives partial credit for in-group citations based on how close the connection is. Instead of 0 or 1, each category has a weight between 0 and 1.

| Connection Type | Weight | Rationale |
|----------------|--------|-----------|
| Self-citation | 0.0 | No credit |
| Same department | 0.1 | Forced proximity, no collaboration |
| Direct co-author | 0.2 | Chosen collaboration |
| Transitive co-author | 0.5 | Friend-of-friend |
| Same institution (different dept) | 0.4 | Same university, different field |
| Same parent organization | 0.7 | Shared umbrella (e.g., UC system) |
| External | 1.0 | Full credit |

**Calculation:**
```
HEROCON = (Sum of all citation weights ÷ Classifiable citations) × 100
```

HEROCON will always be equal to or higher than BARON because it gives partial credit where BARON gives zero.

---

### The Gap

**Gap = HEROCON − BARON**

The gap measures how much of the researcher's impact depends on their inner circle.

- **Small gap (0–10%)**: Most citations come from independent sources; the researcher's network provides minimal boost
- **Large gap (20%+)**: Many citations flow through professional relationships; the collaborative network is a major channel

---

### The Detection Layers

The system builds the researcher's network in phases. Each phase adds a new detection layer:

**Phase 1: Identity**
Checks if the citing author is the researcher (self-citation).

**Phase 2: Co-authorship**  
Builds a graph of everyone the researcher has published with. By default, checks connections up to two degrees out (co-authors' co-authors).

**Phase 3: Affiliation**  
Checks if the citing author worked at the same institution as the researcher when the citation was made. Uses publication dates to match contemporaneous affiliations, not current ones.

---

### Data Quality Handling

When the system cannot determine an affiliation or relationship (missing metadata), it classifies the citation as **UNKNOWN**. These citations are excluded from both BARON and HEROCON calculations rather than assumed external.

This prevents artificially high scores for researchers with incomplete metadata, but it means the scores reflect only the *classifiable* portion of the researcher's citation profile (typically 70–90% of total citations, depending on data availability).
"""
