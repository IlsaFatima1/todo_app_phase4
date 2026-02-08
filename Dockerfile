FROM node:18-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
ENV PIP_DEFAULT_TIMEOUT=1000
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt


COPY backend .

COPY --from=frontend-builder /frontend/.next /app/.next
COPY --from=frontend-builder /frontend/public /app/public
COPY --from=frontend-builder /frontend/package.json /app/package.json
COPY --from=frontend-builder /frontend/node_modules /app/node_modules

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
