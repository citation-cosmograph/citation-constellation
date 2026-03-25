# citation-constellation Dockerfile
# SciLifeLab Serve compliant: non-root user (uid 1000), port 7860
# Build:
# docker buildx build --platform linux/amd64,linux/arm64 -t mahbub1969/citation-constellation:v1 --push .
# Pull:
# docker pull mahbub1969/citation-constellation:v1
# Run:
# docker run --rm -it -p 7860:7860 mahbub1969/citation-constellation:v1


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

# ── Gradio temp directory for uploads ──
ENV GRADIO_TEMP_DIR="/home/appuser/app/temp/"
ENV GRADIO_SERVER_NAME="0.0.0.0"
RUN mkdir -p $HOME/app/temp $HOME/app/audits

# ── Permissions ──
RUN chown -R $USER:$USER $HOME

# ── Run as non-root ──
USER $USER

EXPOSE 7860

ENTRYPOINT ["./start-script.sh"]
