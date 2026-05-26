FROM python:3.11-slim

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Copy everything into the container
COPY . /app/

# Make the build script executable and run it
RUN chmod +x ./build.sh && ./build.sh

# Expose the port (Railway provides $PORT, defaulting to 8000 here)
EXPOSE 8000

# Start command
CMD cd backend && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
