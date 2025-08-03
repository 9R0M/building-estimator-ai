# frontend/Dockerfile
# --- ビルドステージ ---
    FROM node:18 AS builder
    WORKDIR /app
    COPY . .
    RUN npm ci && npm run build
# --- 実行ステージ（Nginx） ---
    FROM nginx:alpine
    
    # ビルド成果物を Nginx の公開ディレクトリに配置
    COPY --from=builder ./app/dist/ /usr/share/nginx/html
    
    # 必要に応じてカスタムNginx設定（SPA対応など）
    COPY nginx.conf /etc/nginx/nginx.conf
    
    # ポート開放（80番）
    EXPOSE 80
    
    # Nginx をフォアグラウンドで起動
    CMD ["nginx", "-g", "daemon off;"]