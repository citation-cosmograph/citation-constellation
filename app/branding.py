"""
citation-constellation/app/branding.py
=======================================
Branding constants, ethical disclaimers, and UI text for the Gradio app.
"""

# ============================================================
# App Identity
# ============================================================

APP_TITLE = "Where do your citations come from? Citation-Constellation: Decomposing citation profiles by network proximity with BARON and HEROCON scores"
APP_SUBTITLE = "An open-source, no-code tool for multi-phase citation network decomposition; fully auditable with downloadable data, ready to install locally"
APP_VERSION = "v0.3"
APP_FULL_TITLE = f"{APP_TITLE} — {APP_SUBTITLE}"

# ============================================================
# Ethical Disclaimer (non-dismissable, shown prominently)
# ============================================================

# <div style="font-size: 4rem; margin-bottom: 15px; letter-spacing: 8px;">✋ 🛑 🙏</div>

ETHICAL_NOTICE = """
<div style="background-color: #F0F7F4; border: 2px solid #5A8F7B; border-radius: 12px; padding: 30px; margin: 20px 0; text-align: center; max-width: 100%;">
  
  
  <div style="font-size: 4rem; margin-bottom: 15px; letter-spacing: 8px;">✋ 🛑 🙏</div>
  
  <h2 style="color: #2C5F4D; margin: 0 0 20px 0; font-size: 1.4rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px;">Important Ethical Notice</h2>
  
  <p style="color: #1B4332; margin: 12px 0; font-size: 1.05rem; line-height: 1.6; font-weight: 500;">
    BARON and HEROCON scores <strong style="color: #C44536; font-weight: 800;">DO NOT</strong> measure research quality, impact, or integrity.
  </p>
  
  <p style="color: #1B4332; margin: 12px 0; font-size: 1.05rem; line-height: 1.6; font-weight: 500;">
    BARON and HEROCON scores should <strong style="color: #C44536; font-weight: 800;">NOT</strong> be used for hiring, promotion, or funding decisions.
  </p>
  
  <p style="color: #1B4332; margin: 12px 0; font-size: 1.05rem; line-height: 1.6; font-weight: 500;">
    All classification decisions are fully documented in the downloadable audit report. Verify all results before drawing conclusions.
  </p>
</div>
"""

# ============================================================
# Asset Paths (relative to app/ directory)
# ============================================================

LOGO_PATH = "app/assets/logos.png"
FAVICON_PATH = "app/assets/logo.png"

SCORE_INTRO_CARD = f"""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 0; border-radius: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 100%; margin: 0; box-sizing: border-box; overflow: hidden; box-shadow: 0 25px 80px rgba(0,0,0,0.6);">
  
  <!-- Header -->
  <div style="background: linear-gradient(90deg, rgba(212, 175, 55, 0.25) 0%, rgba(147, 112, 219, 0.25) 100%); padding: 25px 20px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.15);">
    <h2 style="color: #f4e4c1; margin: 0; font-size: clamp(2rem, 5vw, 3.2rem); letter-spacing: 3px; font-weight: 800; text-shadow: 0 2px 10px rgba(0,0,0,0.3);">Citation-Constellation</h2>
    <div style="color: rgba(244, 228, 193, 0.9); font-size: clamp(0.9rem, 2vw, 1.1rem); margin-top: 8px; font-weight: 400; max-width: 800px; margin-left: auto; margin-right: auto;">A citation network analysis tool featuring two novel, complementary bibliometric scores</div>
  </div>
  
  <!-- Hero Section: BARON | Image | HEROCON -->
  <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 40px 20px; background: radial-gradient(ellipse at center, rgba(255,255,255,0.05) 0%, transparent 70%); box-sizing: border-box;">
    
    <!-- BARON Side -->
    <div style="flex: 1; text-align: center; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
      <div style="display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 1rem; font-weight: 800; letter-spacing: 2px; color: #d4af37; border: 2px solid rgba(212, 175, 55, 0.4); margin-bottom: 20px; background: rgba(212, 175, 55, 0.1); box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15);">Binary & Absolute</div>
      <div style="font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 900; color: #d4af37; text-shadow: 0 0 30px rgba(212, 175, 55, 0.5); letter-spacing: 3px; margin-bottom: 10px;">BARON</div>
      <div style="font-size: 1.2rem; font-weight: 600; letter-spacing: 1px; color: rgba(212, 175, 55, 0.8); line-height: 1.4; max-width: 200px;">Boundary-Anchored<br>Research Outreach<br>Network Score</div>
    </div>
    
    <!-- Center Image -->
    <div style="flex: 0 0 auto; padding: 0 30px; display: flex; align-items: center; justify-content: center;">
      <img src="/gradio_api/file={LOGO_PATH}" alt="Citation Constellation Logo" style="max-width: 100%; height: auto; border-radius: 12px; filter: drop-shadow(0 20px 40px rgba(0,0,0,0.5)); display: block;">
    </div>
    
    <!-- HEROCON Side -->
    <div style="flex: 1; text-align: center; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
      <div style="display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 1rem; font-weight: 800; letter-spacing: 2px; color: #9370db; border: 2px solid rgba(147, 112, 219, 0.4); margin-bottom: 20px; background: rgba(147, 112, 219, 0.1); box-shadow: 0 4px 15px rgba(147, 112, 219, 0.15);">Weighted & Holistic</div>
      <div style="font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 900; color: #9370db; text-shadow: 0 0 30px rgba(147, 112, 219, 0.5); letter-spacing: 3px; margin-bottom: 10px;">HEROCON</div>
      <div style="font-size: 1.2rem; font-weight: 600; letter-spacing: 1px; color: rgba(147, 112, 219, 0.8); line-height: 1.4; max-width: 200px;">Holistic Equilibrated<br>Research Outreach<br>CONstellation Score</div>
    </div>
    
  </div>
  
  <!-- Detailed Descriptions Below -->
  <div style="display: grid; grid-template-columns: repeat(2, 1fr); width: 100%; border-top: 1px solid rgba(255,255,255,0.1);">
    
    <div style="padding: 30px; background: linear-gradient(180deg, rgba(212, 175, 55, 0.08) 0%, transparent 100%); border-right: 1px solid rgba(255,255,255,0.1);">
      <div style="color: rgba(255,255,255,0.85); font-size: 1.05rem; line-height: 1.7; font-style: italic; text-align: justify;">The Boundary-Anchored Research Outreach Network (BARON) score is inspired by the historical Marcher Barons, who secured and governed a realm's outer borders. Acting as the frontier guard of a researcher's citation profile, it deliberately filters out the natural amplification of local networks, such as co-authors and institutional peers. Instead, it anchors the maximum reach of a scholar's metrics by measuring strictly boundary-spanning, external citations. By establishing this foundational threshold of strict external outreach, the BARON score provides the crucial external validation required to give the broader HEROCON score its constellation shape.</div>
    </div>
    
    <div style="padding: 30px; background: linear-gradient(180deg, rgba(147, 112, 219, 0.08) 0%, transparent 100%);">
      <div style="color: rgba(255,255,255,0.85); font-size: 1.05rem; line-height: 1.7; font-style: italic; text-align: justify;">Named for the CONstellation Hercules, honoring the legendary Greek HERO (HEROCON), this score maps a researcher's total scholarly influence as a constellation. In this metaphor, local collaborations form a dense, bright cluster, much like the constellation's brightest star system, Rasalgethi ("the kneeler's head"), which represents the humility to "kneel" and value one's immediate community. However, an enduring constellation must also stretch across the sky. It relies on the anchoring boundary stars of the BARON score to define its outer limits and give it its legendary shape. Ultimately, a high HEROCON score demonstrates that research scholarship unites a bright local foundation with the vast external outreach that illuminates the broader academic universe.</div>
    </div>
    
  </div>
  {ETHICAL_NOTICE}
</div>
"""

SCORE_INTRO_CARDz = f"""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 20px; border-radius: 16px; font-family: sans-serif; width: 100%; margin: 0 auto;">
  
            
  
  <div style="background: linear-gradient(90deg, rgba(212, 175, 55, 0.2) 0%, rgba(147, 112, 219, 0.2) 100%); padding: 20px; text-align: center; border-radius: 12px 12px 0 0; border: 1px solid rgba(255,255,255,0.1); border-bottom: none;">
    <h2 style="color: #f4e4c1; margin: 0; font-size: 3rem; letter-spacing: 2px;">Citation-Constellation</h2>
    <div style="color: rgba(244, 228, 193, 0.7); font-size: 1rem; margin-top: 4px;">A citation network analysis tool featuring two novel, complementary bibliometric scores</div>
  </div>
  
  <div style="display: flex; justify-content: center; width: 100%; padding-bottom: 20px;">
    <img src="/gradio_api/file={LOGO_PATH}" alt="Logo" style="display: block; margin: 0 auto; max-width: 100%; height: auto; width: 30%; border-radius: 8px;">
  </div>
  
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0; border: 1px solid rgba(255,255,255,0.1); border-radius: 0 0 12px 12px; overflow: hidden;">
    
    <div style="padding: 35px; background: linear-gradient(180deg, rgba(212, 175, 55, 0.05) 0%, transparent 100%); border-right: 1px solid rgba(255,255,255,0.05);">
      <div style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 1rem; font-weight: 600; letter-spacing: 1px; color: #d4af37; border: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 15px;">Binary & Absolute</div>
      <div style="font-size: 2.4rem; font-weight: 700; color: #d4af37; margin-bottom: 8px; text-shadow: 0 0 30px rgba(212, 175, 55, 0.3);">BARON</div>
      <div style="font-size: 1.5rem; font-weight: 600; letter-spacing: 1.5px; color: #d4af37; margin-bottom: 18px; line-height: 1.4;">Boundary-Anchored Research Outreach Network Score</div>
      <div style="color: rgba(255,255,255,0.75); font-size: 1.05rem; line-height: 1.6; font-style: italic; padding: 0 5px;">The Boundary-Anchored Research Outreach Network (BARON) score is inspired by the historical Marcher Barons, who secured and governed a realm's outer borders. Acting as the frontier guard of a researcher's citation profile, it deliberately filters out the natural amplification of local networks, such as co-authors and institutional peers. Instead, it anchors the maximum reach of a scholar's metrics by measuring strictly boundary-spanning, external citations. By establishing this foundational threshold of strict external outreach, the BARON score provides the crucial external validation required to give the broader HEROCON score its constellation shape.</div>
    </div>
    
    <div style="padding: 35px; background: linear-gradient(180deg, rgba(147, 112, 219, 0.05) 0%, transparent 100%);">
      <div style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 1rem; font-weight: 600; letter-spacing: 1px; color: #9370db; border: 1px solid rgba(147, 112, 219, 0.3); margin-bottom: 15px;">Weighted & Holistic</div>
      <div style="font-size: 2.4rem; font-weight: 700; color: #9370db; margin-bottom: 8px; text-shadow: 0 0 30px rgba(147, 112, 219, 0.3);">HEROCON</div>
      <div style="font-size: 1.5rem; font-weight: 600; letter-spacing: 1.5px; color: #9370db; margin-bottom: 18px; line-height: 1.4;">Holistic Equilibrated Research Outreach CONstellation Score</div>
      <div style="color: rgba(255,255,255,0.75); font-size: 1.05rem; line-height: 1.6; font-style: italic; padding: 0 5px;">Named for the CONstellation Hercules, honoring the legendary Greek HERO (HEROCON), this score maps a researcher's total scholarly influence as a constellation. In this metaphor, local collaborations form a dense, bright cluster, much like the constellation's brightest star system, Rasalgethi ("the kneeler's head"), which represents the humility to "kneel" and value one's immediate community. However, an enduring constellation must also stretch across the sky. It relies on the anchoring boundary stars of the BARON score to define its outer limits and give it its legendary shape. Ultimately, a high HEROCON score demonstrates that research scholarship unites a bright local foundation with the vast external outreach that illuminates the broader academic universe.</div>
    </div>
    
  </div>
  {ETHICAL_NOTICE}
</div>
"""




ETHICAL_DISCLAIMER = """

<div style="font-size: 4em; margin-bottom: -10px;"> ✋ 🛑 🙏</div>

## IMPORTANT ETHICAL NOTICE

### **BARON and HEROCON scores DO NOT measure research quality, impact, or integrity.**
### **BARON and HEROCON scores should NOT be used for hiring, promotion, or funding decisions.**
### **All classification decisions are fully documented in the downloadable audit report. Verify all results before drawing conclusions.**
"""

DISCLAIMER_SHORT = (
    "BARON and HEROCON measure citation network structure, not research quality, "
    "impact, or integrity. They should not be used for hiring, promotion, or funding decisions. "
    "Every classification decision is documented in the downloadable audit report. "
    "Verify any result before drawing conclusions."
)

# ============================================================
# Input Help Text
# ============================================================

IDENTIFIER_HELP = """
**Enter an ORCID or OpenAlex ID:**

* **ORCID:** A 16-digit identifier (e.g., `0000-0000-0000-0000`). Find yours at [orcid.org](https://orcid.org).
* **OpenAlex ID:** Starts with an 'A' followed by digits (e.g., `A0000000000`). Find yours at [openalex.org](https://openalex.org).

**Examples of valid inputs:**
*(Note: These examples are dummy values and not from real profiles. Make sure to use your actual, correct ID!)*
* `0000-0000-0000-0000`
* `https://orcid.org/0000-0000-0000-0000`
* `A0000000000` or `a0000000000`
* `https://openalex.org/authors/a0000000000`
* `https://openalex.org/a0000000000`
* `https://openalex.org/authors/A0000000000`
* `https://openalex.org/A0000000000`

💡 *You can paste the ID directly or use the full URL. Citation-Constellation will extract the ID automatically.*
"""

SINCE_HELP = """
OpenAlex occasionally merges profiles of researchers with similar names. Set a temporal boundary to resolve these name collisions and help cleaning up the data.

* **Eliminate Noise:** Automatically exclude any publications dated before the researcher's career started.
* **Easy Verification:** Quickly verify the correct starting year by checking the researcher's first entry on databases like Google Scholar or ORCID.

💡 *Citation-Constellation* already uses sophisticated algorithmic filtering; this is an optional manual override to improve accuracy even further.
"""

DEPTH_HELP = """
* **Depth 1** — Only direct co-authors are in-group. Strictest. Best for large, loosely collaborative fields.
* **Depth 2** — Co-authors + their co-authors. Recommended default for most researchers.
* **Depth 3** — Three hops. Largest in-group. Best for small, tightly-knit fields.
    
💡 The depth setting determines how far a researcher's network extends to define their in-group during BARON and HEROCON score calculations. Adjusting this parameter allows them to tightly control the dividing line between their immediate collaborative circle and the broader academic community.
"""

CONFIRM_HELP = """
When enabled, you can manually review potential misattributions (detected via ORCID validation) before they are removed from scoring. When disabled, flagged papers are automatically excluded.

💡 This step is highly recommended for maximum accuracy.
"""


WEIGHTS_HELP = """
Upload a `.json` file to apply your own weighting scheme to the HEROCON score calculation. You do not need to include every metric in your file; any classification left unspecified will automatically fall back to its default value. 

**Example Format:**
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

**Why Customize?**
Citation-Constellation's default weights are currently **experimental heuristics**. They are based on structural intuition regarding how different academic relationships might influence citation behavior, rather than empirically calibrated data. 

💡 Because empirical weight calibration is still an ongoing area of research for Citation-Constellation, it is strongly encouraged that you use this upload feature to test custom parameters if you have a strong argument to support it. Future updates will introduce empirically calibrated defaults and sensitivity analyses to examine score stability under weight perturbation.
"""


# ============================================================
# GitHub & Paper References
# ============================================================

GITHUB_ORG = "https://github.com/citation-cosmograph"
REPO_CONSTELLATION = f"{GITHUB_ORG}/citation-constellation"
REPO_PULSAR = f"{GITHUB_ORG}/citation-pulsar-helm"
REPO_ASTROLABE = f"{GITHUB_ORG}/citation-astrolabe"

PAPER_REFERENCE = (
    "Alam, M. U. (2026). Where do your citations come from? Citation-Constellation: Decomposing citation profiles by network proximity with BARON and HEROCON scores "
    " *[arXiv: placeholder]*."
)

# ============================================================
# Footer HTML
# ============================================================
FOOTER_HTML = f"""
<div style="background: linear-gradient(180deg, #0f1419 0%, #1a1a2e 100%); padding: 35px 20px; margin-top: 0; border-top: 1px solid rgba(255,255,255,0.1); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; color: rgba(255,255,255,0.6); font-size: 0.9rem; line-height: 1.6; border-radius: 16px;">
    
    <p style="margin: 0 0 12px 0; font-size: 1rem; color: rgba(255,255,255,0.9); font-weight: 600; letter-spacing: 0.5px;">
        Part of the <a href="{GITHUB_ORG}" target="_blank" style="color: #d4af37; text-decoration: none; font-weight: 800; border-bottom: 1px solid rgba(212, 175, 55, 0.3); transition: all 0.3s ease;">citation-cosmograph</a> project
    </p>
    
    <p style="margin: 0 0 15px 0; font-size: 0.95rem; letter-spacing: 0.5px;">
        <a href="{REPO_CONSTELLATION}" target="_blank" style="color: #d4af37; text-decoration: none; font-weight: 600; margin: 0 8px; padding: 4px 12px; border-radius: 6px; background: rgba(212, 175, 55, 0.1); border: 1px solid rgba(212, 175, 55, 0.2); transition: all 0.3s ease;">citation-constellation</a> <span style="color: #d4af37;">✨</span>
        <span style="color: rgba(255,255,255,0.3); margin: 0 5px;">·</span>
        <a href="{REPO_PULSAR}" target="_blank" style="color: #9370db; text-decoration: none; font-weight: 600; margin: 0 8px; padding: 4px 12px; border-radius: 6px; background: rgba(147, 112, 219, 0.1); border: 1px solid rgba(147, 112, 219, 0.2); transition: all 0.3s ease;">citation-pulsar-helm</a> <span style="color: #9370db;">🌟</span>
        <span style="color: rgba(255,255,255,0.3); margin: 0 5px;">·</span>
        <a href="{REPO_ASTROLABE}" target="_blank" style="color: #64b5f6; text-decoration: none; font-weight: 600; margin: 0 8px; padding: 4px 12px; border-radius: 6px; background: rgba(100, 181, 246, 0.1); border: 1px solid rgba(100, 181, 246, 0.2); transition: all 0.3s ease;">citation-astrolab</a>e <span style="color: #64b5f6;">🔭</span>
    </p>
    
    <p style="margin: 15px 0; font-style: italic; color: rgba(255,255,255,0.5); font-size: 0.85rem; max-width: 600px; margin-left: auto; margin-right: auto; padding: 0 20px; border-left: 2px solid rgba(212, 175, 55, 0.3); border-right: 2px solid rgba(147, 112, 219, 0.3);">
        {PAPER_REFERENCE}
    </p>
    
    <p style="margin: 12px 0 8px 0; font-size: 0.85rem; color: rgba(255,255,255,0.5);">
        Hosted on <a href="https://serve.scilifelab.se" target="_blank" style="color: #a8d5a2; text-decoration: none; font-weight: 600; border-bottom: 1px solid rgba(168, 213, 162, 0.3);">SciLifeLab Serve</a> 
        <span style="color: rgba(255,255,255,0.2); margin: 0 8px;">|</span> 
        Powered by 
        <a href="https://openalex.org" target="_blank" style="color: #f4a261; text-decoration: none; font-weight: 600; margin: 0 3px; border-bottom: 1px solid rgba(244, 162, 97, 0.3);">OpenAlex</a>, 
        <a href="https://orcid.org" target="_blank" style="color: #a5d6a7; text-decoration: none; font-weight: 600; margin: 0 3px; border-bottom: 1px solid rgba(165, 214, 167, 0.3);">ORCID</a>, 
        <a href="https://ror.org" target="_blank" style="color: #90caf9; text-decoration: none; font-weight: 600; margin: 0 3px; border-bottom: 1px solid rgba(144, 202, 249, 0.3);">ROR</a>
    </p>
    
    <p style="margin: 12px 0 0 0; font-size: 0.8rem; color: rgba(255,255,255,0.4); font-weight: 500; letter-spacing: 1px; text-transform: uppercase;">
        MIT License
    </p>
</div>
"""

FOOTER_HTMLz = f"""
<div style="text-align: center; padding: 20px 0; border-top: 1px solid #e5e7eb; margin-top: 20px; color: #6b7280; font-size: 0.85em;">
    <p style="margin: 4px 0;">
        Part of the <a href="{GITHUB_ORG}" target="_blank"><b>citation-cosmograph</b></a> project
    </p>
    <p style="margin: 4px 0;">
        <a href="{REPO_CONSTELLATION}" target="_blank">citation-constellation</a> ✨ ·
        <a href="{REPO_PULSAR}" target="_blank">pulsar-helm</a> 🌟 ·
        <a href="{REPO_ASTROLABE}" target="_blank">astrolabe</a> 🔭
    </p>
    <p style="margin: 8px 0; font-style: italic;">
        {PAPER_REFERENCE}
    </p>
    <p style="margin: 4px 0;">
        Hosted on <a href="https://serve.scilifelab.se" target="_blank">SciLifeLab Serve</a> ·
        Powered by <a href="https://openalex.org" target="_blank">OpenAlex</a>,
        <a href="https://orcid.org" target="_blank">ORCID</a>,
        <a href="https://ror.org" target="_blank">ROR</a>
    </p>
    <p style="margin: 4px 0;">MIT License</p>
</div>
"""

# ============================================================
# Header HTML
# ============================================================

HEADER_HTML = f"""
<div style="text-align: center; padding: 10px 0;">
    <h1 style="margin: 0; font-size: 1.8em;">{APP_TITLE}</h1>
    <p style="margin: 4px 0; color: #6b7280; font-size: 1.1em;">{APP_SUBTITLE}</p>
    <p style="margin: 2px 0; color: #9ca3af; font-size: 0.85em;">{APP_VERSION} · citation-constellation</p>
</div>
"""

# ============================================================
# Custom CSS
# ============================================================

CUSTOM_CSS = """
.disclaimer-banner {
    background-color: #FEF3C7;
    border: 2px solid #F59E0B;
    border-radius: 8px;
    padding: 16px;
    margin: 10px 0;
    font-size: 0.95em;
    text-align: center;
}
.disclaimer-banner h3 {
    margin-top: 5px;
    margin-bottom: 15px; /* 👈 SHRUNK: Brings the text closer to the heading */
}
.disclaimer-banner p {
    margin: 8px 0;
}
.score-highlight {
    font-size: 2em;
    font-weight: bold;
    text-align: center;
}
"""
