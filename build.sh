#!/usr/bin/env bash
# exit on error
set -o errexit

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Build backend
cd backend
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py load_mock_data
cd ..
