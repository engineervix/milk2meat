"""
WSGI config for milk2meat project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if os.getenv("WEB_CONCURRENCY"):  # Feel free to change this condition
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "milk2meat.settings.production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "milk2meat.settings.dev")


application = get_wsgi_application()
