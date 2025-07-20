FROM python:3.11-slim
# Prometheus マルチプロセス メトリクス用ディレクトリ
ENV PROMETHEUS_MULTIPROC_DIR=/app/metrics
WORKDIR /app
RUN mkdir -p /app/metrics
VOLUME /app/metrics
# 依存先を先にコピー → キャッシュ活用
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
&& pip install gunicorn "uvicorn[standard]" \
&& rm -rf /root/.cache/pip
# アプリコードを後でコピー、再ビルド回避
COPY . .
# 非 root ユーザーで起動（セキュリティ強化）
RUN addgroup --system app && adduser --system --ingroup app app
USER app
# 実行コマンド：Gunicorn + UvicornWorker × 4 workers
CMD ["gunicorn", "main:app","-k", "uvicorn.workers.UvicornWorker","--workers", "4","--bind", "0.0.0.0:8000"]
#.dockerignore に以下追加で無駄ファイルの除外を徹底
#__pycache__/
#*.pyc
#.git
#.env
#metrics/
#HEALTHCHECK を設定することで、Docker／Kubernetesレベルで健全性管理が可能
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1