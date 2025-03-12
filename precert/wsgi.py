"""
WSGI config for precert project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'precert.settings')

# Setup Django before calling management commands
django.setup()

# Run migrations automatically on startup
try:
    call_command('migrate', interactive=False)
    print("✅ Migrations applied successfully!")
except Exception as e:
    print(f"⚠️ Migration error: {e}")

# Now load the application
application = get_wsgi_application()
