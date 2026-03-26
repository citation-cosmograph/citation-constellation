# citation-constellation Dockerfile
# SciLifeLab Serve compliant: non-root user (uid 1000), port 7860
# Build:
# docker buildx build --platform linux/amd64,linux/arm64 --no-cache -t mahbub1969/citation-constellation:v1 --push .
# Pull:
# docker pull mahbub1969/citation-constellation:v1
# Run:
# docker run --rm -it -p 7860:7860 mahbub1969/citation-constellation:v1

# Use defaults (8 workers for 16 GB RAM)
# docker run --rm -it -p 7860:7860 mahbub1969/citation-constellation:v1

# Override for a smaller machine (4 GB)
#docker run --rm -it -p 7860:7860 \
#    -e CC_MAX_WORKERS=2 \
#    mahbub1969/citation-constellation:v1

# Override multiple settings
#docker run --rm -it -p 7860:7860 \
#    -e CC_MAX_WORKERS=4 \
#    -e CC_PIPELINE_TIMEOUT_MAX=1800 \
#    -e RATE_LIMIT_MAX=20 \
#    mahbub1969/citation-constellation:v1


FROM python:3.11-slim

# ── Non-root user (uid 1000 required by SciLifeLab Serve) ──
ENV USER=appuser
ENV HOME=/home/$USER

RUN useradd -m -u 1000 $USER

# ── Working directory ──
WORKDIR $HOME/app

# ── System dependencies ──
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ──
COPY requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir \
    -r requirements.txt

# ── Copy application code ──
COPY models.py $HOME/app/models.py
COPY client.py $HOME/app/client.py
COPY audit.py $HOME/app/audit.py
COPY orcid_validate.py $HOME/app/orcid_validate.py
COPY phase1.py $HOME/app/phase1.py
COPY phase2.py $HOME/app/phase2.py
COPY phase3.py $HOME/app/phase3.py
COPY app/ $HOME/app/app/

# ── Start script ──
COPY start-script.sh $HOME/app/start-script.sh
RUN chmod +x $HOME/app/start-script.sh

# ── Gradio config ──
ENV GRADIO_TEMP_DIR="/home/appuser/app/temp/"
ENV GRADIO_SERVER_NAME="0.0.0.0"

# ── Citation-Constellation config ──
# CC_MAX_WORKERS: concurrent analysis pipelines (each uses ~1.5 GB peak)
#   RAM guide: 2 GB → 1 | 4 GB → 2 | 8 GB → 4 | 16 GB → 8
# CC_PIPELINE_TIMEOUT_MAX: absolute max seconds for a single pipeline run
# CC_VALIDATE_TIMEOUT_MAX: absolute max seconds for ORCID validation step
# CC_RATE_LIMIT_MAX: max analyses per hour per session (renamed from RATE_LIMIT_MAX)
ENV CC_MAX_WORKERS=8
ENV CC_PIPELINE_TIMEOUT_MAX=3600
ENV CC_VALIDATE_TIMEOUT_MAX=600
ENV RATE_LIMIT_MAX=10

RUN mkdir -p $HOME/app/temp $HOME/app/audits

# ── Permissions ──
RUN chown -R $USER:$USER $HOME

# ── Run as non-root ──
USER $USER

EXPOSE 7860

ENTRYPOINT ["./start-script.sh"]
