FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Document the port used by the application
EXPOSE 10000

# Render provides PORT at runtime
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT