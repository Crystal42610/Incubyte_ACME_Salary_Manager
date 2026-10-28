#!/bin/sh
set -eu
: "${ACME_ADMIN_USER:?Set ACME_ADMIN_USER before starting}"
: "${ACME_ADMIN_PASSWORD:?Set ACME_ADMIN_PASSWORD before starting}"
python -m backend.seed
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
