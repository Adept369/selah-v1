# orchestrator/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 1) Copy only requirements, install (this helps cache layers)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy in your code
COPY app ./app
COPY agents ./app/agents

# 3) Launch with Uvicorn (no --reload here; this is your "prod" image)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
