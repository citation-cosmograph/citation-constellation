"""
citation-constellation/app/tabs/FUTURE_FEATURES.py
=======================================
Roadmap for future phases and features
"""

FUTURE_FEATURES = """


<div style="background:linear-gradient(160deg,#0a0a1a 0%,#0f1a2e 40%,#0d0d20 100%);font-family:Inter,sans-serif;color:#e0e0e0;padding:28px 24px;max-width:1100px;margin:0 auto;border-radius:12px;">

<!-- ═══════════ Title ═══════════ -->
<div style="text-align:center;margin-bottom:20px;">
<div style="font-size:1.6rem;font-weight:800;letter-spacing:2px;background:linear-gradient(135deg,#ffb74d,#ff8a65 40%,#90caf9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;">Future Roadmap</div>
<div style="font-size:.8rem;color:rgba(255,255,255,.55);margin-top:3px;">Planned phases, features, and infrastructure</div>
</div>

<!-- ═══════════ Current State Banner ═══════════ -->
<div style="display:flex;justify-content:center;margin-bottom:16px;">
<div style="background:rgba(76,175,80,.08);border:1.5px solid rgba(76,175,80,.3);border-radius:10px;padding:10px 24px;text-align:center;max-width:500px;">
<div style="font-size:.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#66bb6a;margin-bottom:4px;">Currently Available — Phases 1–3</div>
<div style="font-size:.7rem;color:rgba(255,255,255,.6);line-height:1.5;">Self-citation detection · Co-author network (BFS, depth 1–3) · Temporal affiliation matching (ROR hierarchy) · ORCID cross-validation · Full audit trail</div>
</div>
</div>

<div style="display:flex;justify-content:center;height:24px;margin-bottom:4px;">
<div style="width:2px;height:100%;background:linear-gradient(180deg,rgba(76,175,80,.4),rgba(255,183,77,.4));"></div>
</div>

<!-- ═══════════ Phase 4 ═══════════ -->
<div style="text-align:center;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,183,77,.6);margin:8px 0;">Phase 4 — Venue Governance Detection</div>

<div style="background:rgba(255,183,77,.06);border:1.5px solid rgba(255,183,77,.25);border-radius:12px;padding:18px 16px;margin-bottom:12px;">

<!-- Phase 4: Status + Summary -->
<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
<span style="font-size:1.6rem;">🤖</span>
<div>
<div style="font-size:.9rem;font-weight:800;color:#ffe0b2;">Venue Governance via Local LLM</div>
<div style="font-size:.65rem;color:rgba(255,255,255,.55);margin-top:2px;">Detect citations from venues where the researcher or their network holds editorial or committee roles</div>
</div>
<span style="font-size:.55rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;padding:3px 8px;border-radius:4px;color:#4e342e;background:#ffb74d;white-space:nowrap;margin-left:auto;">🔧 Building</span>
</div>

<!-- Phase 4: New classifications -->
<div style="font-size:.6rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,183,77,.7);margin-bottom:8px;">New Classification Types</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:14px;">
<div style="background:rgba(255,183,77,.08);border:1px solid rgba(255,183,77,.2);border-radius:8px;padding:8px;text-align:center;">
<div style="font-size:.72rem;font-weight:700;color:#ffe0b2;">VENUE_SELF_GOV</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.55);margin-top:2px;">Researcher on editorial board</div>
<div style="font-size:.52rem;font-weight:600;color:#ffcc80;margin-top:4px;">Weight: 0.05</div>
</div>
<div style="background:rgba(255,183,77,.08);border:1px solid rgba(255,183,77,.2);border-radius:8px;padding:8px;text-align:center;">
<div style="font-size:.72rem;font-weight:700;color:#ffe0b2;">VENUE_ED_COAUTH</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.55);margin-top:2px;">Venue editor is a co-author</div>
<div style="font-size:.52rem;font-weight:600;color:#ffcc80;margin-top:4px;">Weight: 0.15</div>
</div>
<div style="background:rgba(255,183,77,.08);border:1px solid rgba(255,183,77,.2);border-radius:8px;padding:8px;text-align:center;">
<div style="font-size:.72rem;font-weight:700;color:#ffe0b2;">VENUE_ED_AFFIL</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.55);margin-top:2px;">Venue editor at same institution</div>
<div style="font-size:.52rem;font-weight:600;color:#ffcc80;margin-top:4px;">Weight: 0.3</div>
</div>
<div style="background:rgba(255,183,77,.08);border:1px solid rgba(255,183,77,.2);border-radius:8px;padding:8px;text-align:center;">
<div style="font-size:.72rem;font-weight:700;color:#ffe0b2;">VENUE_COMMITTEE</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.55);margin-top:2px;">Committee member in network</div>
<div style="font-size:.52rem;font-weight:600;color:#ffcc80;margin-top:4px;">Weight: 0.4</div>
</div>
</div>

<!-- Phase 4: Three-tool ecosystem -->
<div style="font-size:.6rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,183,77,.7);margin-bottom:8px;">Three-Tool Ecosystem</div>
<div style="display:flex;justify-content:center;align-items:stretch;gap:0;margin-bottom:10px;">
<div style="border-radius:10px 0 0 10px;padding:14px 16px;text-align:center;flex:1;background:rgba(147,112,219,.08);border:1px solid rgba(147,112,219,.25);border-right:none;">
<div style="font-size:1.2rem;">🌟</div>
<div style="font-size:.85rem;font-weight:800;letter-spacing:1px;color:#b39ddb;">Pulsar</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.55);margin-top:2px;">The Signal</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.45);font-family:monospace;line-height:1.5;margin-top:6px;">Qwen 3.5 8B<br>llama.cpp · Kubernetes<br>OpenAI-compatible API</div>
</div>
<div style="display:flex;align-items:center;padding:0 4px;color:rgba(255,255,255,.25);font-size:1.2rem;background:rgba(255,255,255,.02);">→</div>
<div style="padding:14px 16px;text-align:center;flex:1;background:rgba(100,181,246,.08);border:1px solid rgba(100,181,246,.25);border-left:none;border-right:none;">
<div style="font-size:1.2rem;">🔭</div>
<div style="font-size:.85rem;font-weight:800;letter-spacing:1px;color:#90caf9;">Astrolabe</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.55);margin-top:2px;">The Instrument</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.45);font-family:monospace;line-height:1.5;margin-top:6px;">httpx + Cloudflare Crawl<br>HTML → LLM extraction<br>Entity resolution</div>
</div>
<div style="display:flex;align-items:center;padding:0 4px;color:rgba(255,255,255,.25);font-size:1.2rem;background:rgba(255,255,255,.02);">→</div>
<div style="border-radius:0 10px 10px 0;padding:14px 16px;text-align:center;flex:1;background:rgba(212,175,55,.08);border:1px solid rgba(212,175,55,.25);border-left:none;">
<div style="font-size:1.2rem;">✨</div>
<div style="font-size:.85rem;font-weight:800;letter-spacing:1px;color:#f4e4c1;">Constellation</div>
<div style="font-size:.6rem;color:rgba(255,255,255,.55);margin-top:2px;">The Map</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.45);font-family:monospace;line-height:1.5;margin-top:6px;">VENUE_* classifications<br>BARON v0.4 · HEROCON v0.4<br>11 total classes</div>
</div>
</div>

<!-- Phase 4: Infrastructure blocks -->
<div style="font-size:.6rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,183,77,.7);margin-bottom:8px;">Infrastructure</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;">
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 10px;text-align:center;">
<div style="font-size:.75rem;">🗄️</div>
<div style="font-size:.68rem;font-weight:700;color:rgba(255,255,255,.85);">PostgreSQL DB</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:2px;">Timestamped governance records with confidence scores</div>
</div>
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 10px;text-align:center;">
<div style="font-size:.75rem;">⏰</div>
<div style="font-size:.68rem;font-weight:700;color:rgba(255,255,255,.85);">K8s CronJobs</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:2px;">Nightly refresh for records older than 12 months</div>
</div>
<div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 10px;text-align:center;">
<div style="font-size:.75rem;">🔍</div>
<div style="font-size:.68rem;font-weight:700;color:rgba(255,255,255,.85);">Entity Resolution</div>
<div style="font-size:.55rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:2px;">ORCID + affiliation matching against OpenAlex profiles</div>
</div>
</div>
</div>

<div style="display:flex;justify-content:center;height:24px;margin:4px 0;">
<div style="width:2px;height:100%;background:linear-gradient(180deg,rgba(255,183,77,.4),rgba(144,202,249,.3));"></div>
</div>

<!-- ═══════════ Phase 5 ═══════════ -->
<div style="text-align:center;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(144,202,249,.6);margin:8px 0;">Phase 5 — Field Normalization & Comparative Analytics</div>

<div style="background:rgba(144,202,249,.05);border:1.5px dashed rgba(144,202,249,.25);border-radius:12px;padding:18px 16px;margin-bottom:12px;">

<!-- Phase 5: Status + Summary -->
<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
<span style="font-size:1.6rem;">📊</span>
<div>
<div style="font-size:.9rem;font-weight:800;color:#bbdefb;">Percentile Ranks & Peer Cohorts</div>
<div style="font-size:.65rem;color:rgba(255,255,255,.55);margin-top:2px;">Compare scores against field-specific peer distributions with confidence intervals</div>
</div>
<span style="font-size:.55rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;padding:3px 8px;border-radius:4px;color:#0d47a1;background:#90caf9;white-space:nowrap;margin-left:auto;">📋 Planned</span>
</div>

<!-- Phase 5: Feature grid -->
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;">
<div style="background:rgba(144,202,249,.06);border:1px solid rgba(144,202,249,.18);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">🏷️</div>
<div style="font-size:.7rem;font-weight:700;color:#bbdefb;margin-top:2px;">Field Classification</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">OpenAlex concept tags and hierarchical topic classifications to assign researchers to fields</div>
</div>
<div style="background:rgba(144,202,249,.06);border:1px solid rgba(144,202,249,.18);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">👥</div>
<div style="font-size:.7rem;font-weight:700;color:#bbdefb;margin-top:2px;">Peer Cohort Sampling</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Auto-sampled by field, career length, and publication volume for meaningful comparison</div>
</div>
<div style="background:rgba(144,202,249,.06);border:1px solid rgba(144,202,249,.18);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">📐</div>
<div style="font-size:.7rem;font-weight:700;color:#bbdefb;margin-top:2px;">Confidence Intervals</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Bootstrap resampling to quantify statistical uncertainty in BARON and HEROCON scores</div>
</div>
<div style="background:rgba(144,202,249,.06);border:1px solid rgba(144,202,249,.18);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">📈</div>
<div style="font-size:.7rem;font-weight:700;color:#bbdefb;margin-top:2px;">Percentile Ranks</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Individual scores ranked against peer cohort distributions, normalized by field norms</div>
</div>
<div style="background:rgba(144,202,249,.06);border:1px solid rgba(144,202,249,.18);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">🌐</div>
<div style="font-size:.7rem;font-weight:700;color:#bbdefb;margin-top:2px;">REST API</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Programmatic endpoint for score computation, audit data, and integration with external tools</div>
</div>
<div style="background:rgba(144,202,249,.06);border:1px solid rgba(144,202,249,.18);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">📊</div>
<div style="font-size:.7rem;font-weight:700;color:#bbdefb;margin-top:2px;">Advanced Dashboard</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Interactive ego graphs, network structure visualization, and temporal career trajectories</div>
</div>
</div>
</div>

<div style="display:flex;justify-content:center;height:24px;margin:4px 0;">
<div style="width:2px;height:100%;background:linear-gradient(180deg,rgba(144,202,249,.3),rgba(206,147,216,.3));"></div>
</div>

<!-- ═══════════ Phase 6 ═══════════ -->
<div style="text-align:center;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(206,147,216,.6);margin:8px 0;">Phase 6 — Validation & Advanced Diagnostics</div>

<div style="background:rgba(206,147,216,.05);border:1.5px dashed rgba(206,147,216,.2);border-radius:12px;padding:18px 16px;margin-bottom:12px;">

<!-- Phase 6: Status + Summary -->
<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
<span style="font-size:1.6rem;">🔬</span>
<div>
<div style="font-size:.9rem;font-weight:800;color:#e1bee7;">Empirical Calibration & Multi-Source Fusion</div>
<div style="font-size:.65rem;color:rgba(255,255,255,.55);margin-top:2px;">Ground HEROCON weights in observed data, validate against surveys, integrate additional bibliometric sources</div>
</div>
<span style="font-size:.55rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;padding:3px 8px;border-radius:4px;color:#4a148c;background:#ce93d8;white-space:nowrap;margin-left:auto;">🔮 Future</span>
</div>

<!-- Phase 6: Feature grid -->
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;">
<div style="background:rgba(206,147,216,.06);border:1px solid rgba(206,147,216,.15);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">⚖️</div>
<div style="font-size:.7rem;font-weight:700;color:#e1bee7;margin-top:2px;">Sensitivity Analysis</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Test score stability under perturbations of HEROCON weights and decay constants</div>
</div>
<div style="background:rgba(206,147,216,.06);border:1px solid rgba(206,147,216,.15);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">🔄</div>
<div style="font-size:.7rem;font-weight:700;color:#e1bee7;margin-top:2px;">UNKNOWN Imputation</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Evaluate alternative strategies for unclassifiable citations to assess selection bias</div>
</div>
<div style="background:rgba(206,147,216,.06);border:1px solid rgba(206,147,216,.15);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">✅</div>
<div style="font-size:.7rem;font-weight:700;color:#e1bee7;margin-top:2px;">Ground-Truth Validation</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Cross-validation against citation motivation surveys for empirical accuracy</div>
</div>
<div style="background:rgba(206,147,216,.06);border:1px solid rgba(206,147,216,.15);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">📉</div>
<div style="font-size:.7rem;font-weight:700;color:#e1bee7;margin-top:2px;">Rolling Trajectories</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Windowed BARON/HEROCON scores across career years to identify trend patterns</div>
</div>
<div style="background:rgba(206,147,216,.06);border:1px solid rgba(206,147,216,.15);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">🔗</div>
<div style="font-size:.7rem;font-weight:700;color:#e1bee7;margin-top:2px;">Multi-Source Fusion</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Integrate Semantic Scholar, CrossRef, and DBLP to reduce single-source dependency</div>
</div>
<div style="background:rgba(206,147,216,.06);border:1px solid rgba(206,147,216,.15);border-radius:8px;padding:10px;text-align:center;">
<div style="font-size:.85rem;">🎯</div>
<div style="font-size:.7rem;font-weight:700;color:#e1bee7;margin-top:2px;">Empirical Calibration</div>
<div style="font-size:.58rem;color:rgba(255,255,255,.5);line-height:1.4;margin-top:4px;">Ground HEROCON weights in observed citation behavior rather than theoretical defaults</div>
</div>
</div>
</div>

<!-- ═══════════ Timeline ═══════════ -->
<div style="margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,.08);">
<div style="text-align:center;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:rgba(255,255,255,.4);margin-bottom:10px;">Development Timeline</div>
<div style="display:flex;justify-content:center;align-items:center;gap:0;max-width:800px;margin:0 auto;">
<div style="flex:1;text-align:center;padding:8px 4px;border-right:1px solid rgba(255,255,255,.08);">
<div style="font-size:.55rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#66bb6a;">Phases 1–3</div>
<div style="font-size:.52rem;color:rgba(255,255,255,.45);margin-top:2px;">Available now</div>
<div style="width:100%;height:4px;background:#4caf50;border-radius:2px;margin-top:6px;"></div>
</div>
<div style="flex:1;text-align:center;padding:8px 4px;border-right:1px solid rgba(255,255,255,.08);">
<div style="font-size:.55rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#ffb74d;">Phase 4</div>
<div style="font-size:.52rem;color:rgba(255,255,255,.45);margin-top:2px;">In development</div>
<div style="width:100%;height:4px;background:linear-gradient(90deg,#ffb74d 40%,rgba(255,183,77,.2) 40%);border-radius:2px;margin-top:6px;"></div>
</div>
<div style="flex:1;text-align:center;padding:8px 4px;border-right:1px solid rgba(255,255,255,.08);">
<div style="font-size:.55rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#90caf9;">Phase 5</div>
<div style="font-size:.52rem;color:rgba(255,255,255,.45);margin-top:2px;">Planned</div>
<div style="width:100%;height:4px;background:rgba(144,202,249,.2);border-radius:2px;margin-top:6px;"></div>
</div>
<div style="flex:1;text-align:center;padding:8px 4px;">
<div style="font-size:.55rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#ce93d8;">Phase 6</div>
<div style="font-size:.52rem;color:rgba(255,255,255,.45);margin-top:2px;">Future research</div>
<div style="width:100%;height:4px;background:rgba(206,147,216,.15);border-radius:2px;margin-top:6px;"></div>
</div>
</div>
</div>

<!-- ═══════════ Data sources footer ═══════════ -->
<div style="display:flex;justify-content:center;gap:10px;margin-top:14px;flex-wrap:wrap;">
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">OpenAlex</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;">FREE</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">ORCID</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;">FREE</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">ROR</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;">FREE</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">Cloudflare Crawl</div>
<div style="font-size:.5rem;font-weight:700;color:#66bb6a;letter-spacing:.8px;">FREE</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">Semantic Scholar</div>
<div style="font-size:.5rem;font-weight:700;color:#90caf9;letter-spacing:.8px;">Phase 6</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">CrossRef</div>
<div style="font-size:.5rem;font-weight:700;color:#90caf9;letter-spacing:.8px;">Phase 6</div>
</div>
<div style="padding:4px 10px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:5px;">
<div style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,.65);">DBLP</div>
<div style="font-size:.5rem;font-weight:700;color:#90caf9;letter-spacing:.8px;">Phase 6</div>
</div>
</div>

<div style="text-align:center;margin-top:16px;font-size:.65rem;color:rgba(255,255,255,.45);font-style:italic;max-width:700px;margin-left:auto;margin-right:auto;line-height:1.5;">
<strong style="color:rgba(255,255,255,.6);font-style:normal;">Figure:</strong> Development roadmap. Phase 4 introduces venue governance detection via a three-tool ecosystem (Pulsar, Astrolabe, Constellation). Phase 5 adds field normalization and comparative analytics. Phase 6 focuses on empirical validation and multi-source data fusion.
</div>
</div>


---

# Future Features — Detailed Description

## Phase 4: Venue Governance Detection via Local LLM and AI Agent

This phase will introduce detection of citations from academic venues where a researcher or their professional network holds governance roles. The system will identify connections through editorial boards, programme committees, and organising committees of journals and conferences, revealing structural pathways where venue governance relationships might influence citation patterns.

### Technical Implementation

**LLM Infrastructure (Pulsar)**
- A quantized Qwen 3.5 8B language model will be deployed via llama.cpp on Kubernetes to serve as a local extraction engine
- CPU-only inference, no GPU dependency — deployable on standard Kubernetes clusters
- Exposed as an OpenAI-compatible API endpoint for seamless integration with downstream tools
- Hosted on SciLifeLab Serve alongside the main Citation-Constellation application

**Web Scraping & Extraction (Astrolabe)**
- An AI agent pipeline will scrape venue editorial board pages using httpx and Cloudflare Crawl API for JavaScript-rendered sites
- Raw HTML will be fed to the local LLM to extract structured member names, roles, institutions, and ORCID identifiers
- Entity resolution algorithms will match extracted governance members against OpenAlex author profiles using ORCID and affiliation data
- High-confidence matches will be stored in a persistent PostgreSQL database with timestamped entries and confidence scores

**Classification Integration (Constellation)**
- The classification layer will cross-reference each citing venue against the governance database
- Four new classification types will be introduced (see table in diagram above)
- The HEROCON weights for venue classifications are graduated: self-governance gets nearly zero credit (0.05), while committee membership gets moderate credit (0.4)

**Data Freshness**
- Nightly Kubernetes CronJobs will refresh governance data older than 12 months
- New venues encountered during analysis runs will be queued for incremental database expansion
- All governance data will be timestamped and versioned for audit trail integrity

### New Classification Types (Phase 4)

| Classification | HEROCON Weight | Detection Method |
|----------------|---------------|-----------------|
| **VENUE_SELF_GOVERNANCE** | 0.05 | Researcher found on the editorial board / organising committee of the citing venue |
| **VENUE_EDITOR_COAUTHOR** | 0.15 | A venue editor is a co-author of the target researcher |
| **VENUE_EDITOR_AFFIL** | 0.3 | A venue editor is at the same institution as the target researcher |
| **VENUE_COMMITTEE** | 0.4 | A programme committee member is within the target's co-author network |

---

## Phase 5: Field Normalization and Comparative Analytics

Raw BARON and HEROCON scores are meaningful for self-reflection but difficult to interpret in isolation: what counts as "typical" varies enormously by field, career stage, and research culture. Phase 5 will provide the context needed for meaningful comparison.

### Planned Features

**Field Classification**
- The system will classify researchers into fields using OpenAlex concept tags and hierarchical topic classifications
- Multi-label assignment will handle interdisciplinary researchers who span multiple fields

**Peer Cohort Sampling**
- Peer cohorts will be automatically sampled by matching field, career length, and publication volume parameters
- Cohort size will be configurable (default: 100–500 peers per field-career-stage combination)

**Confidence Intervals**
- Bootstrap resampling methods will calculate confidence intervals for BARON and HEROCON scores to reflect statistical uncertainty
- This will make explicit the difference between "this researcher's score is 72%" and "this researcher's score is 72% ± 4%"

**Field-Normalized Percentile Ranks**
- Individual scores will be compared against peer cohort distributions to produce percentile ranks
- A researcher at the 75th percentile in their field has a higher external citation proportion than 75% of comparable researchers

**REST API**
- A programmatic endpoint will expose score computation and audit data for integration with institutional dashboards, research information systems, and third-party analytics tools
- JSON-based request/response with API key authentication

**Advanced Dashboard**
- Interactive visualizations of network structure, ego graphs, and temporal career trajectories
- Comparative overlays showing a researcher's trajectory against field medians and quartiles

---

## Phase 6: Validation and Advanced Diagnostics

The final planned phase focuses on empirical validation and methodological rigour — ensuring that BARON and HEROCON scores are not just structurally sound but empirically meaningful.

### Planned Research

**Sensitivity Analysis**
- Systematic perturbation of HEROCON weights and decay constants to test score stability
- If small weight changes cause large score swings, the metric is fragile and needs redesign
- Results will inform which weight ranges produce stable, interpretable scores

**UNKNOWN Imputation**
- Alternative strategies for handling unclassifiable citations (currently excluded from denominators)
- Worst-case (all UNKNOWN = in-group) and best-case (all UNKNOWN = external) bounds will bracket the true score
- Probabilistic imputation based on field-level base rates may provide tighter bounds

**Ground-Truth Cross-Validation**
- Citation motivation surveys ask researchers *why* they cited each paper — these provide ground truth for whether a citation is relationship-driven or content-driven
- Network classifications will be correlated against available survey data to measure accuracy
- This is the gold standard for validating any citation classification system

**Rolling Temporal Trajectories**
- Windowed (e.g., 5-year rolling) BARON/HEROCON scores to complement the current cumulative trajectory
- Rolling scores reveal trend changes (e.g., a researcher's network diversifying after a career move) that cumulative scores smooth over

**Multi-Source Data Fusion**
- Integration of Semantic Scholar, CrossRef, and DBLP alongside OpenAlex
- Cross-source validation: if two sources agree on a citation link, confidence increases
- Reduces single-source dependency and improves coverage for fields underrepresented in OpenAlex

**Empirical Weight Calibration**
- Frameworks to derive HEROCON weights from observed citation behavior rather than theoretical assumptions
- For example: if direct co-author citations have a 3× higher base rate than external citations in a field, the weight should reflect that inflation factor
- This will replace the current experimental heuristic defaults with data-driven values
"""
