# Start with a small Python image.
FROM python:3.12-slim

# Keep Python output visible and avoid extra cache files.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Put the app files in this folder inside the container.
WORKDIR /app

# Install the Python packages the app needs.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app into the container.
COPY src/ .

# The web app listens on this port.
EXPOSE 5000

# Start the Flask app so other devices can reach it.
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0"]
