FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# torch CPU-only: image jauh lebih kecil (tanpa CUDA)
RUN pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download model embedding saat build, bukan saat container start
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

COPY main.py .
COPY app/ app/
COPY data/ data/

# chroma_db dibuat ulang dari data/ saat start pertama (tiap image baru = data terbaru)
# Model sudah ada di image -> jangan hubungi HF Hub saat runtime
ENV HF_HUB_OFFLINE=1
# chown non-rekursif: cukup /app writable untuk chroma_db (chown -R menduplikasi layer model ~480MB)
RUN useradd -r -u 1000 appuser && chown appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
