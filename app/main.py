"""
citation-constellation/app/main.py
=====================================
Gradio web interface for BARON & HEROCON citation network structure analysis.

Two tabs:
  1. Run New Analysis — Enter ORCID/OpenAlex ID, get interactive results
  2. Visualize Reports — Upload existing audit JSON files for visualization & comparison

Designed for deployment on SciLifeLab Serve (serve.scilifelab.se).
"""

import sys
import os

# Ensure the repo root is on the path so phase1/2/3 imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from branding import (
    APP_FULL_TITLE, HEADER_HTML, FOOTER_HTML,
    CUSTOM_CSS, FAVICON_PATH, LOGO_PATH, SCORE_INTRO_CARD, ETHICAL_NOTICE
)
from tabs import run_analysis, visualize
from tabs.BARON_and_HEROCON import BARON_and_HEROCON
from tabs.FUTURE_FEATURES import FUTURE_FEATURES
from tabs.HOW_TO_RUN import HOW_TO_RUN
from tabs.RESEARCH_PAPER import RESEARCH_PAPER


def create_app() -> gr.Blocks:
    """Build the full Gradio application."""

    with gr.Blocks(
        title=APP_FULL_TITLE,
    ) as app:
        
        # logo
        #gr.Image(LOGO_PATH, show_label=False, container=False, buttons=None)
        
        gr.HTML(SCORE_INTRO_CARD, container=False)
        
        #gr.HTML(ETHICAL_NOTICE)
        
                
        # ── Ethical disclaimer (non-dismissable) ──
        # gr.Markdown(ETHICAL_DISCLAIMER, elem_classes=["disclaimer-banner"], container=False)
        
         # ── Header ──
        # gr.HTML(HEADER_HTML)
        

        # ── Tabs ──
        with gr.Tabs():
            with gr.Tab("🔍 Run Analysis"):
                run_analysis.build_tab()

            with gr.Tab("📊 View Existing Audits"):
                visualize.build_tab()
                
            with gr.Tab("💻 How to Run Here & Install Locally"):
                gr.Markdown(HOW_TO_RUN)
                
                    
            with gr.Tab("🧠 How BARON & HEROCON Work"):
                gr.Markdown(BARON_and_HEROCON)
                
            with gr.Tab("🚀 Future Features"):
                gr.Markdown(FUTURE_FEATURES)
                
            with gr.Tab("📄 Full Research Paper"):
                gr.Markdown(RESEARCH_PAPER)
                
            
                

        # ── Footer ──
        gr.HTML(FOOTER_HTML)

    return app


# ============================================================
# Entry Point
# ============================================================

#from pathlib import Path

# 1. Get the absolute path of the directory where main.py sits
# This ensures it works regardless of where you run the 'gradio' command from
#current_file_path = Path(__file__).resolve()
#assets_dir = current_file_path.parent / "assets"

# 2. Register the absolute path as a static directory
#gr.set_static_paths(paths=[str(assets_dir)])
gr.set_static_paths("app/assets/")


if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        favicon_path=FAVICON_PATH if os.path.exists(FAVICON_PATH) else None,
        css=CUSTOM_CSS,
        #theme=gr.themes.Monochrome(),
        #theme=gr.themes.Base()
        #theme=gr.themes.Default()
        #theme=gr.themes.Glass()
        theme=gr.themes.Monochrome()
        #theme=gr.themes.Soft()
        
        #theme=gr.themes.Soft(
        #    primary_hue="amber",
        #    secondary_hue="green",
        #    neutral_hue="gray",
        #),
    )
