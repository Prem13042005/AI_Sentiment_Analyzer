FROM python:3.10-slim

WORKDIR /app

# Install standard Linux binaries and database connectors
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy workspace code
COPY . .

# Expose FastAPI and Streamlit standard ports
EXPOSE 8000
EXPOSE 8501

# Default runtime command serves the FastAPI API
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
