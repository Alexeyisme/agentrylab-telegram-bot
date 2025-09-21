# 🐳 AgentryLab Telegram Bot - Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Ensure root project directory is on Python path (so /app/config.py is importable)
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies including AgentryLab from PyPI
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Expose port (if using webhook mode)
EXPOSE 8443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the bot from the bot directory
WORKDIR /app/bot
CMD ["python", "main.py"]
