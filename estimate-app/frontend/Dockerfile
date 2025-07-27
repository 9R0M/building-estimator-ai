# frontend/Dockerfile
# --- ビルドステージ ---
    FROM node:20-alpine AS builder
    WORKDIR /app
    # package.jsonとlockファイルだけ先にコピーして依存解決を高速化
    COPY package*.json ./
    RUN npm install
    # 全ファイルコピーしてビルド
    COPY . .
    RUN npm run build
    # --- 実行ステージ ---
    FROM nginx:alpine
    # ビルド成果物をNginx公開ディレクトリに配置
    COPY --from=builder /app/dist /usr/share/nginx/html
    # Nginxのデフォルト設定を最適化（省略可）
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]