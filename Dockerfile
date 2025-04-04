# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy in our application code
COPY . .

# Expose the port Dash will run on
EXPOSE 8050

# Start the dash application
CMD ["python", "app.py"]
