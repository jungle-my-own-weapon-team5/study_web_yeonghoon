#!/bin/bash

set -e

export POSTGRES_USER=${POSTGRES_USER:-app}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-1q2w3e4r!}
export POSTGRES_DB=${POSTGRES_DB:-ai_app}
export BACKEND_PORT=${BACKEND_PORT:-8000}
export FRONTEND_PORT=${FRONTEND_PORT:-5173}
export PID_DIR=${PID_DIR:-/app}

START_PID_FILE="${PID_DIR}/start.pid"
BACKEND_PID_FILE="${PID_DIR}/backend.pid"
FRONTEND_PID_FILE="${PID_DIR}/frontend.pid"

cleanup() {
  trap - EXIT INT TERM

  echo "Stopping backend/frontend processes..."

  if [ -f "${FRONTEND_PID_FILE}" ]; then
    FRONTEND_PID="$(cat "${FRONTEND_PID_FILE}")"
    if [ -n "${FRONTEND_PID}" ] && kill -0 "${FRONTEND_PID}" > /dev/null 2>&1; then
      kill "${FRONTEND_PID}" || true
    fi
  fi

  if [ -f "${BACKEND_PID_FILE}" ]; then
    BACKEND_PID="$(cat "${BACKEND_PID_FILE}")"
    if [ -n "${BACKEND_PID}" ] && kill -0 "${BACKEND_PID}" > /dev/null 2>&1; then
      kill "${BACKEND_PID}" || true
    fi
  fi

  pkill -f "uvicorn app.main:app" || true
  pkill -f "vite" || true
  pkill -f "npm run dev" || true

  rm -f "${START_PID_FILE}" "${BACKEND_PID_FILE}" "${FRONTEND_PID_FILE}"
}

trap cleanup EXIT INT TERM

echo "$$" > "${START_PID_FILE}"

echo "Checking PostgreSQL..."

if pg_isready -U postgres > /dev/null 2>&1; then
  echo "PostgreSQL is already running."
else
  echo "Starting PostgreSQL..."
  pg_ctlcluster 16 main start
fi

echo "Waiting for PostgreSQL..."
until pg_isready -U postgres > /dev/null 2>&1; do
  sleep 1
done

echo "Creating PostgreSQL role if not exists..."
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname = '${POSTGRES_USER}'\" | grep -q 1 || psql -c \"CREATE ROLE ${POSTGRES_USER} WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}' SUPERUSER CREATEDB CREATEROLE;\""

echo "Creating PostgreSQL database if not exists..."
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'\" | grep -q 1 || createdb -O ${POSTGRES_USER} ${POSTGRES_DB}"

echo "Initializing database..."
PGPASSWORD="${POSTGRES_PASSWORD}" psql \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  -h localhost \
  -f /app/db/init.sql || true

echo "Stopping existing backend/frontend processes if any..."

pkill -f "uvicorn app.main:app" || true
pkill -f "vite" || true
pkill -f "npm run dev" || true

echo "Starting FastAPI backend..."
cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" --reload &
BACKEND_PID=$!
echo "${BACKEND_PID}" > "${BACKEND_PID_FILE}"

echo "Starting React frontend..."
cd /app/frontend

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies inside Linux container..."
  npm install
fi

npm run dev -- --host 0.0.0.0 --port "${FRONTEND_PORT}" &
FRONTEND_PID=$!
echo "${FRONTEND_PID}" > "${FRONTEND_PID_FILE}"

wait -n "${BACKEND_PID}" "${FRONTEND_PID}"
