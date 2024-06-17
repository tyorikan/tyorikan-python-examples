FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8080
EXPOSE 8080

# Start Gunicorn server
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080"]
