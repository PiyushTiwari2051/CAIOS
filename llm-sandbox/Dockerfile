FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Hardened unprivileged container user
RUN groupadd -r sandboxgroup && useradd -r -g sandboxgroup -d /app sandboxuser

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY service/ ./service/

# Create sandbox directory inside container with appropriate ownership
RUN mkdir -p /app/sandbox && chown -R sandboxuser:sandboxgroup /app

USER sandboxuser

EXPOSE 8001

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8001"]
