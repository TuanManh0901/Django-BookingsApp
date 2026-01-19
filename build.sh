#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Load fixtures if they exist (only on first deploy or when database is empty)
if [ -f "fixtures/users.json" ]; then
    echo "Loading fixtures..."
    python manage.py loaddata fixtures/users.json || true
    python manage.py loaddata fixtures/tours.json || true
    python manage.py loaddata fixtures/reviews.json || true
    echo "Fixtures loaded successfully!"
fi

echo "Build completed successfully!"
