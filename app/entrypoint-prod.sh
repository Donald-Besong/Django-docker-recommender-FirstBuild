#!/bin/sh

# Get the environment (default to development if not set)
DJANGO_ENV=${DJANGO_ENV:-development}

echo "Starting with environment: $DJANGO_ENV"

chown -R nginx:nginx /usr/src/app/static || echo "chown failed, likely due to volume permissions"

if [ "$DJANGO_ENV" = "production" ]; then
    echo "Collecting static files for production..."
    python manage.py collectstatic --noinput || { echo "collectstatic failed"; exit 1; }
    echo "*** static files collected."
    # Ensure the correct permissions for static files so Nginx can access them

# Only wait for Postgres in development

elif [ "$DJANGO_ENV" = "development" ]; then
    echo "Waiting for PostgreSQL to be ready..."

    # Retry settings
    MAX_RETRIES=30
    RETRIES=0

    while ! nc -z $SQL_HOST $SQL_PORT && [ $RETRIES -lt $MAX_RETRIES ]; do
        sleep 1
        RETRIES=$((RETRIES + 1))
    done

    if [ $RETRIES -ge $MAX_RETRIES ]; then
        echo "PostgreSQL did not become available in time. Exiting."
        exit 1
    fi

    echo "PostgreSQL is up and running!"
fi

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput || { echo "Migrations failed"; exit 1; }

# Create superuser if not already created
echo "Creating superuser (if necessary)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'donbes@yahoo.com', 'adminpassword')
EOF
echo "*** superuser created."
# Execute the command to start the application (usually runs the Django app)
exec gosu app "$@"
