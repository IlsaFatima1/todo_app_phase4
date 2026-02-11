# Base image
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install Node.js (for Next.js)
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Copy backend
COPY backend ./backend

# Copy frontend
COPY frontend ./frontend

# Install backend deps
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install frontend deps
WORKDIR /app/frontend
RUN npm install && npm run build

# Go back
WORKDIR /app

# Expose port
EXPOSE 7860

# Start both apps
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 7860"]
