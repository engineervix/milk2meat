"""See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/"""

import logging
from email.utils import formataddr, getaddresses

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa

DEBUG = False  # just to make sure!

DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),  # noqa F405
        "KEY_PREFIX": env("REDIS_KEY_PREFIX"),  # noqa F405
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

# RQ_QUEUES = {
#     "default": {
#         "USE_REDIS_CACHE": "default",
#     },
# }

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# SECURITY
# ------------------------------------------------------------------------------

# if the next two settings are controlled by nginx, comment them out
# https://docs.djangoproject.com/en/5.1/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/5.1/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"
# if the next set of settings are controlled by nginx, comment them out
# https://docs.djangoproject.com/en/5.1/topics/security/#ssl-https
# https://docs.djangoproject.com/en/5.1/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
# SECURE_HSTS_SECONDS = 518400
# https://docs.djangoproject.com/en/5.1/ref/settings/#secure-hsts-include-subdomains
# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)  # noqa F405
# https://docs.djangoproject.com/en/5.1/ref/settings/#secure-hsts-preload
# SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)  # noqa F405
# https://docs.djangoproject.com/en/5.1/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)  # noqa F405

# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/#installation
INSTALLED_APPS += ["storages"]  # noqa: F405
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")  # noqa: F405
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")  # noqa: F405
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")  # noqa: F405
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")  # noqa: F405
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="auto")  # noqa: F405
# AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN")  # noqa: F405

_AWS_EXPIRY = 60 * 60 * 24 * 7
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate"}

AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_LOCATION = env("AWS_LOCATION", default="files")  # noqa: F405
AWS_S3_FILE_OVERWRITE = env("AWS_S3_FILE_OVERWRITE", default=False)  # noqa: F405

# this is a custom setting, not part of django-storages
AWS_SIGNED_URL_EXPIRE_SECONDS = env("AWS_SIGNED_URL_EXPIRE_SECONDS", default=60 * 5)  # noqa: F405

# STATIC
# ------------------------
STORAGES = {
    "default": {
        "BACKEND": "milk2meat.core.storage.PrivateS3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# Temporary hack if you experience problems: https://stackoverflow.com/a/69123932
# STORAGES = {
#     "default": {
#         "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
#     },
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedStaticFilesStoragee",
#     },
# }

# MEDIA
# ------------------------------------------------------------------------------
# MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_LOCATION}/"

# setup email backend via Anymail
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
INSTALLED_APPS += ["anymail"]  # noqa F405
# https://docs.djangoproject.com/en/5.1/ref/settings/#email-backend
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
# https://anymail.dev/en/stable/esps/brevo/
EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
ANYMAIL = {
    "BREVO_API_KEY": env("BREVO_API_KEY"),  # noqa F405
}

if len(getaddresses([env("EMAIL_RECIPIENTS")])) == 1:  # noqa F405
    ADMINS.append(getaddresses([env("EMAIL_RECIPIENTS")])[0])  # noqa F405  # noqa F405
else:
    recipients = getaddresses([env("EMAIL_RECIPIENTS")])  # noqa F405
    ADMINS += recipients  # noqa F405

LIST_OF_EMAIL_RECIPIENTS += list(map(lambda recipient: formataddr(recipient), ADMINS))  # noqa F405
email_address = getaddresses([env("DEFAULT_FROM_EMAIL")])[0]  # noqa F405
DEFAULT_FROM_EMAIL = formataddr(email_address)

# https://docs.djangoproject.com/en/5.1/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)  # noqa F405

# https://docs.djangoproject.com/en/5.1/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(  # noqa F405
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[Milk to Meat]",
)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/5.1/ref/settings/#logging
# See https://docs.djangoproject.com/en/5.1/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
        "gunicorn": {"format": "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"},
        # "rq_console": {
        #     "format": "%(asctime)s %(message)s",
        #     "datefmt": "%H:%M:%S",
        # },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "gunicorn": {
            "class": "logging.StreamHandler",
            "formatter": "gunicorn",
        },
        # "rq_console": {
        #     "level": "DEBUG",
        #     "class": "rq.logutils.ColorizingStreamHandler",
        #     "formatter": "rq_console",
        #     "exclude": ["%(asctime)s"],
        # },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "gunicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "gunicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.security": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        # Errors logged by the SDK itself
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        # "rq.worker": {"handlers": ["rq_console"], "level": "DEBUG"},
    },
}

# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN")  # noqa F405
SENTRY_LOG_LEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)  # noqa F405

sentry_logging = LoggingIntegration(
    level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)
integrations = [
    sentry_logging,
    DjangoIntegration(),
    RedisIntegration(),
]
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=integrations,
    environment=env("SENTRY_ENVIRONMENT", default="production"),  # noqa F405
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),  # noqa F405
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)
