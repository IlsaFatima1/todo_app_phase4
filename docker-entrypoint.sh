#!/bin/bash
set -e

# Initialize PostgreSQL
echo "Initializing PostgreSQL..."
service postgresql start

# Wait for PostgreSQL to be ready
sleep 5

# Create database and user if they don't exist
sudo -u postgres psql -c "CREATE USER user WITH PASSWORD 'password';" 2>/dev/null || echo "User may already exist"
sudo -u postgres psql -c "CREATE DATABASE todo_db OWNER user;" 2>/dev/null || echo "Database may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE todo_db TO user;" 2>/dev/null

# Start backend service in background
echo "Starting backend service on port 7860..."
cd /opt/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 7860 --reload &

# Start frontend service in background
echo "Starting frontend service on port 3000..."
cd /opt/frontend
npx serve -s -l 3000 &

# Keep container running
wait