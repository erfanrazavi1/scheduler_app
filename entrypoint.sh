#!/usr/bin/env sh
set -e

# Wait for PostgreSQL to accept connections before touching the database.
if [ -n "${POSTGRES_HOST:-}" ]; then
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432} ..."
  until python -c "import os, socket, sys; \
host=os.environ.get('POSTGRES_HOST','db'); \
port=int(os.environ.get('POSTGRES_PORT','5432')); \
s=socket.socket(); \
s.settimeout(2); \
sys.exit(0 if s.connect_ex((host, port)) == 0 else 1)"; do
    echo "PostgreSQL is not ready yet, retrying in 2s ..."
    sleep 2
  done
  echo "PostgreSQL is ready."
fi

# Apply database migrations.
python manage.py migrate --noinput

# Collect static files for production (served by WhiteNoise).
if [ "${DJANGO_DEBUG:-1}" = "0" ] || [ "${DJANGO_DEBUG:-1}" = "false" ]; then
  echo "Collecting static files ..."
  python manage.py collectstatic --noinput
fi

exec "$@"
