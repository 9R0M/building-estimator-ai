FROM python:3.11-slim
# --- 環境変数 ---
ENV PYTHONPATH=/app
ENV PROMETHEUS_MULTIPROC_DIR=/app/metrics
# --- 作業ディレクトリ & ボリューム ---
WORKDIR /app
RUN mkdir -p /app/metrics
VOLUME /app/metrics
# --- OSライブラリのインストール（GDAL, Tesseract, ビルドツール等）---
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
       software-properties-common \
       git \
       g++ \
       curl \
       build-essential \
       gdal-bin \
       libgdal-dev \
       libproj-dev \
       libgeos-dev \
       libxml2 \
       libxslt1-dev \
       libjpeg-dev \
       libpng-dev \
       libtiff-dev \
       libfreetype6-dev \
       libharfbuzz-dev \
       libfribidi-dev \
       libhdf5-dev \
       libudunits2-dev \
       libnetcdf-dev \
       libglib2.0-0 \
       libsm6 \
       libxext6 \
       libxrender-dev \
       libffi-dev \
       libpq-dev \
       tesseract-ocr \
&& rm -rf /var/lib/apt/lists/*
# --- Pythonパッケージのインストール ---
COPY requirements.txt .
RUN pip install --upgrade pip && \
   pip install --no-cache-dir -r requirements.txt && \
   pip install gunicorn && \
   pip install "uvicorn[standard]"
# --- アプリケーションコードをコピー ---
COPY ./app ./app
# --- 非rootユーザーで起動（セキュリティ強化）---
RUN addgroup --system app && adduser --system --ingroup app app
USER app
# --- Gunicorn + UvicornWorker 起動コマンド ---
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000"]
# --- 健康チェック（FastAPI側で /health を定義すること） ---
HEALTHCHECK --interval=30s --timeout=5s \
 CMD curl -f http://localhost:8000/api/health || exit 1
