FROM python:3.11
WORKDIR /app

# 1. Dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 2. Application code
COPY app      ./app
COPY agents   ./app/agents

# 3. Launch
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
