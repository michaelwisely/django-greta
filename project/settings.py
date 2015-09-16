import os

SETTINGS_DIR = os.path.dirname(__file__)
BUILDOUT_DIR = os.path.dirname(SETTINGS_DIR)
VAR_DIR = os.path.join(BUILDOUT_DIR, "var")

# If a secret_settings file isn't defined, open a new one and save a
# SECRET_KEY in it. Then import it.
try:
    from secret_settings import *
except ImportError:
    print "Couldn't find secret_settings file. Creating a new one."
    settings_loc = os.path.dirname(__file__)
    secret_settings_loc = os.path.join(settings_loc, "secret_settings.py")
    with open(secret_settings_loc, 'w') as secret_settings:
        secret_key = ''.join([chr(ord(x) % 90 + 33) for x in os.urandom(40)])
        secret_settings.write("SECRET_KEY = '''%s'''\n" % secret_key)
    from secret_settings import *


# Django celery settings
import djcelery
djcelery.setup_loader()

# Default to the django backend if necessary.
# ... this is the only way i can find to see if
# a variable is defined.
try:
    BROKER_URL
except NameError:
    BROKER_URL = 'django://'

GRETA_ROOT_DIR = os.path.join(VAR_DIR, "repos")
GRETA_ROOT_TEST_DIR = os.path.join(VAR_DIR, "test_repos")
GRETA_ARCHIVE_DIR = os.path.join(VAR_DIR, "archives")
GRETA_PAGE_COMMITS_BY = 10

ADMINS = (
    # empty
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(VAR_DIR, "db", "greta.db"),
    }
}

LOGIN_REDIRECT_URL = '/'

# For Django guardian.
ANONYMOUS_USER_ID = -1
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(VAR_DIR, "uploads")
MEDIA_URL = ''
STATIC_ROOT = os.path.join(VAR_DIR, "static")
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

FIXTURE_DIRS = (
    os.path.join(SETTINGS_DIR, "fixtures"),
)

STATICFILES_DIRS = (
    os.path.join(SETTINGS_DIR, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), "templates"),
        ],
        'OPTIONS': {
            'debug': False,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.contrib.messages.context_processors.messages',

                # for django-admin-tools
                'django.core.context_processors.request',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'project.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django Admin Tools
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    'greta',

    # django-crispy-forms
    'crispy_forms',

    # Django celery
    'kombu.transport.django',
    'djcelery',

    'django_extensions',
    'guardian',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(VAR_DIR, "logs", "log.txt"),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'greta': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
