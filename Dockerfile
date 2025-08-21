FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Verify critical directories exist
RUN ls -la && \
    echo "Checking folklife-screens-x..." && \
    ls -la folklife-screens-x/ | head -10

# Create templates directory and generate templates
RUN python cluster_viewer.py --generate-templates-only

# Expose port
EXPOSE 5000

# Set environment variables for production
ENV FLASK_ENV=production
ENV FLASK_APP=cluster_viewer.py

# Run the application
CMD ["python", "cluster_viewer.py"]
