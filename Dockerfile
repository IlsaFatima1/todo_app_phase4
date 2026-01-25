# ---------- FRONTEND BUILD ----------
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

# ---------- BACKEND ----------
FROM python:3.10-slim

WORKDIR /app

# Backend deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend code
COPY backend .

# Frontend build output
COPY --from=frontend-builder /frontend/.next /app/.next
COPY --from=frontend-builder /frontend/public /app/public
COPY --from=frontend-builder /frontend/package.json /app/package.json
COPY --from=frontend-builder /frontend/node_modules /app/node_modules

EXPOSE 7860

# Start FastAPI (serving both)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
