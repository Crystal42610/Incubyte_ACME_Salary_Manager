FROM node:22-alpine AS frontend-build
WORKDIR /build
COPY package.json ./
COPY frontend/app.js ./frontend/app.js
RUN npm install --no-audit --no-fund
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 ACME_DB_PATH=/data/acme.db
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /usr/sbin/nologin acme
COPY backend ./backend
COPY frontend/index.html frontend/styles.css ./frontend/
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh && mkdir -p /data
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
