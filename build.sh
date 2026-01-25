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

# Load data strategy: Prefer database_backup.json (full local mirror)
if [ -f "database_backup.json" ]; then
    echo "==> Found database_backup.json. Resetting DB to match local..."
    # Flush current database to remove conflicts
    python manage.py flush --no-input
    
    echo "Loading full database backup..."
    python manage.py loaddata database_backup.json
    echo "✅ Database restored from backup (20 tours)!"

# If no backup, fallback to default fixtures
elif [ -f "fixtures/users.json" ]; then
    echo "==> No backup found. Loading default fixtures..."
    python manage.py loaddata fixtures/users.json || true
    python manage.py loaddata fixtures/tours.json || true
    python manage.py loaddata fixtures/reviews.json || true
    echo "Fixtures loaded!"
fi

# Create/update superadmin user (MUST run after data is loaded so users exist)
echo "==> Configuring superadmin..."
python manage.py create_superadmin || echo "Superadmin configuration skipped"

echo "Build completed successfully!"
# echo "Login: superadmin / VNTravel@2026"  <-- Removed as create_superadmin deletes this user often

# Force redeploy Tue Jan 20 16:18:42 +07 2026
