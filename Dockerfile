# Dockerfile
# Builds the container image for the Agentic Ops Orchestrator API.
# This project only needs FastAPI/uvicorn for now (no torch, no ML
# libraries), so the image stays small and simple.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]