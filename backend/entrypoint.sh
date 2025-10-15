#!/bin/bash
set -e

echo "Waiting for database..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  sleep 1
done
echo "Database is ready"

echo "Initializing database tables..."
python init_db.py

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
