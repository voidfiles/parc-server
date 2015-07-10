"""
Django settings for server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('PARC_SECRET_KEY', 'secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = unicode(os.environ.get("PARC_DEBUG", "1")) == "1"

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kombu.transport.django',
    'djcelery',
    'catalog',
    'taggit',
    'server',
    'integration',
    'django_nose',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'server.urls'

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DEFAULT_DATABASE_PATH = "sqlite:///%s" % os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {'default': dj_database_url.config(default=DEFAULT_DATABASE_PATH)}

if 'db.sqlite3' not in DATABASES['default']['NAME']:
    DATABASES['default']['ENGINE'] = 'django_postgrespool'
    DATABASES['default']['AUTOCOMMIT'] = True
    DATABASES['default']['ATOMIC_REQUESTS'] = False

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
ENVIRONMENT = 'dev'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'simpleapi': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

SIMPLEAPI_ENABLE_CORS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ORIGIN_REGEX_WHITELIST = ('^(https?://).*$', )

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
BROKER_URL = 'django://'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
