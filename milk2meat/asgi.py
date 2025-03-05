"""
ASGI config for milk2meat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

if os.getenv("WEB_CONCURRENCY"):  # Feel free to change this condition
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "milk2meat.settings.production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "milk2meat.settings.dev")

application = get_asgi_application()
