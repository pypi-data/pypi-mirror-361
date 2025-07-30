"""
Minimal Django settings for Django Revolution tests.
"""

SECRET_KEY = 'django-insecure-test-key-for-testing-only-do-not-use-in-production'

DEBUG = True

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'drf_spectacular',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Revolution Test API',
    'DESCRIPTION': 'Test API for Django Revolution',
    'VERSION': '1.0.0',
}

DJANGO_REVOLUTION = {
    'api_prefix': 'api',
    'zones': {}
} 