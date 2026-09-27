"""
WSGI config for expensetracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expensetracker.settings')

application = get_wsgi_application()

# Automatically run database migrations and seed default superuser on WSGI startup
try:
    from django.core.management import call_command
    from django.contrib.auth import get_user_model
    call_command('migrate', interactive=False)
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'Admin@12345')
except Exception as e:
    print(f"Auto-migration error on startup: {e}")

