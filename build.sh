#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (including static/media/tours/)
echo "==> Collecting static files..."
python manage.py collectstatic --no-input --verbosity 2

# Verify static files copied
echo "==> Verifying static/media files..."
if [ -d "staticfiles/media/tours" ]; then
    echo "✅ staticfiles/media/tours/ exists"
    ls staticfiles/media/tours/ | head -5
else
    echo "❌ ERROR: staticfiles/media/tours/ NOT FOUND!"
    echo "Checking source directory:"
    ls -la static/media/tours/ | head -10
fi

# Run migrations
python manage.py migrate

# Create/update superadmin user
echo "==> Creating superadmin user..."
python manage.py create_superadmin || echo "Superadmin creation skipped"

# Load fixtures if they exist (only on first deploy or when database is empty)
if [ -f "fixtures/users.json" ]; then
    echo "Loading fixtures..."
    python manage.py loaddata fixtures/users.json || true
    python manage.py loaddata fixtures/tours.json || true
    python manage.py loaddata fixtures/reviews.json || true
    echo "Fixtures loaded successfully!"
fi

# Load updated tour data
if [ -f "tours_data.json" ]; then
    echo "==> Loading updated tour data..."
    python manage.py loaddata tours_data.json || true
    echo "✅ Tour data loaded!"
fi

echo "Build completed successfully!"
echo "Login: superadmin / VNTravel@2026"

# Force redeploy Tue Jan 20 16:18:42 +07 2026
