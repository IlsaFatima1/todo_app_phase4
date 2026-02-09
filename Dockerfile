FROM python:3.12-alpine

WORKDIR /app

RUN pip install -r requirements.txt

COPY backend .
COPY --from=frontend-builder /frontend/.next /app/.next
COPY --from=frontend-builder /frontend/public /app/public
COPY --from=frontend-builder /frontend/package.json /app/package.json
COPY --from=frontend-builder /frontend/node_modules /app/node_modules

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
