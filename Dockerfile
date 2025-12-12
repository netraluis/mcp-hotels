FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port for SSE/HTTP transport
EXPOSE 8000

# Set python path
ENV PYTHONPATH=/app/src
ENV TRANSPORT=sse
ENV HOST=0.0.0.0
ENV PORT=8000

# Default command
CMD ["fastmcp", "run", "src/server.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
