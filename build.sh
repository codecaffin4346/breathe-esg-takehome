#!/usr/bin/env bash
# exit on error
set -o errexit

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Install backend requirements
pip install -r backend/requirements.txt

# Run Django management commands (manage.py is in the root directory)
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py load_mock_data
