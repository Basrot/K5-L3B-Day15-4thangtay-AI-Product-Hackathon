# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS model
ARG ZIPFORMER_MODEL_URL=https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-vi-30M-int8-2026-02-09.tar.bz2
RUN python - <<'PY'
import os
import tarfile
import urllib.request
from pathlib import Path

url = os.environ.get("ZIPFORMER_MODEL_URL")
archive = Path("/tmp/model.tar.bz2")
urllib.request.urlretrieve(url, archive)
destination = Path("/opt/models/zipformer")
destination.mkdir(parents=True)
with tarfile.open(archive, "r:bz2") as model:
    model.extractall("/tmp/model", filter="data")
for name in ("encoder.int8.onnx", "decoder.onnx", "joiner.int8.onnx", "tokens.txt"):
    matches = list(Path("/tmp/model").rglob(name))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {name}, found {len(matches)}")
    matches[0].rename(destination / name)
PY

FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 \
    HOME=/app/runtime \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    ZIPFORMER_MODEL_DIR=/opt/models/zipformer \
    ZIPFORMER_BACKEND=onnx \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    CBC_DB_PATH=/app/runtime/cbc.sqlite3 \
    VIENEU_TTS_BACKEND=api \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 libstdc++6 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 --no-create-home app
WORKDIR /app
COPY requirements-server.txt ./
RUN python -m pip install -r requirements-server.txt
COPY --from=model /opt/models/zipformer /opt/models/zipformer
COPY codebase/ ./codebase/
COPY voice_demo.py ./
COPY data/full-panel-demo.json ./data/full-panel-demo.json
RUN mkdir -p /app/runtime && chown 10001:10001 /app/runtime
USER 10001:10001
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=4)"
CMD ["python", "-m", "streamlit", "run", "voice_demo.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.maxUploadSize=10", "--browser.gatherUsageStats=false", "--server.headless=true"]
