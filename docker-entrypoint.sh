#!/bin/sh
set -eu
: "${ACME_ADMIN_USER:?Set ACME_ADMIN_USER before starting}"
: "${ACME_ADMIN_PASSWORD:?Set ACME_ADMIN_PASSWORD before starting}"
# Fail closed instead of accepting the published sample password on an internet host.
if [ "${#ACME_ADMIN_PASSWORD}" -lt 16 ] || [ "$ACME_ADMIN_PASSWORD" = "change-me-before-deploy" ] || [ "$ACME_ADMIN_PASSWORD" = "set-a-strong-password" ] || [ "$ACME_ADMIN_PASSWORD" = "choose-a-unique-private-password" ]; then
  echo "ERROR: Choose a unique admin password before deploying" >&2
  exit 1
fi
# A mounted Render disk can be owned by root on first deployment. Assign it
# to the app user before dropping privileges, then run the web app as non-root.
if [ "$(id -u)" = "0" ]; then
  chown acme:acme /data
  exec gosu acme /bin/sh "$0" "$@"
fi
python -m backend.seed
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
