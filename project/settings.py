import os

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


# Testing settings
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--cover-package=greta']


BUILDOUT_DIR = os.path.dirname(os.path.dirname(__file__))
VAR_DIR = os.path.join(BUILDOUT_DIR, "var")

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

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(VAR_DIR, "uploads")
MEDIA_URL = ''
STATIC_ROOT = os.path.join(VAR_DIR, "static")
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    # empty
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'project.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_nose',
    'greta',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
