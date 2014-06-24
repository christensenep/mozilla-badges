# This is an example settings/local.py file.
# These settings overrides what's in settings/base.py

from . import base

# To extend any settings from settings/base.py here's an example:
INSTALLED_APPS = ['django_roa'] + base.INSTALLED_APPS

# Static asset configuration
import os
import sys
import urlparse
from urllib2 import Request, urlopen
import json

SITE_TITLE = 'badges.mozilla.org'

MIDDLEWARE_CLASSES = ['sslify.middleware.SSLifyMiddleware'] + base.MIDDLEWARE_CLASSES
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

request = Request("https://mailtrap.io/api/v1/inboxes?api_token=7888bc66ffe60ad42933412866a0612c")
response_body = urlopen(request).read()
credentials = json.loads(response_body)[0]

EMAIL_HOST = credentials['domain'].encode('ascii','ignore')
EMAIL_HOST_USER = credentials['username'].encode('ascii','ignore')
EMAIL_HOST_PASSWORD = credentials['password'].encode('ascii','ignore')
EMAIL_PORT = credentials['smtp_ports'][0]
EMAIL_USE_TLS = True

url = urlparse.urlparse(os.environ['CLEARDB_DATABASE_URL'])
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': url.path[1:],
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname,
        'PORT': url.port,
        'OPTIONS': {
            'init_command': 'SET storage_engine=InnoDB',
            'charset' : 'utf8',
            'use_unicode' : True,
        },
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
    # 'slave': {
    #     ...
    # },
}

# Uncomment this and set to all slave DBs in use on the site.
# SLAVE_DATABASES = ['slave']

CACHES = {
    'default': {
        'BACKEND': 'django_bmemcached.memcached.BMemcached',
        'LOCATION': os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
        'OPTIONS': {
                    'username': os.environ.get('MEMCACHEDCLOUD_USERNAME'),
                    'password': os.environ.get('MEMCACHEDCLOUD_PASSWORD')
            }
    }
}

# Recipients of traceback emails and other notifications.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# Debugging displays nice error messages, but leaks memory. Set this to False
# on all server instances and True only for development.
DEBUG = TEMPLATE_DEBUG = False

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = False

# By default, BrowserID expects your app to use http://127.0.0.1:8000
# Uncomment the following line if you prefer to access your app via localhost
SITE_URL = 'https://bmo.herokuapp.com'

# Playdoh ships with Bcrypt+HMAC by default because it's the most secure.
# To use bcrypt, fill in a secret HMAC key. It cannot be blank.
HMAC_KEYS = {
    os.environ.get('HMAC_KEY'): os.environ.get('HMAC_SECRET'),
}

from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(base.BASE_PASSWORD_HASHERS, HMAC_KEYS)

# Make this unique, and don't share it with anybody.  It cannot be blank.
SECRET_KEY = os.environ.get('SECRET_KEY')

# Should robots.txt allow web crawlers?  Set this to True for production
ENGAGE_ROBOTS = True

# Uncomment these to activate and customize Celery:
# CELERY_ALWAYS_EAGER = False  # required to activate celeryd
# BROKER_HOST = 'localhost'
# BROKER_PORT = 5672
# BROKER_USER = 'playdoh'
# BROKER_PASSWORD = 'playdoh'
# BROKER_VHOST = 'playdoh'
# CELERY_RESULT_BACKEND = 'amqp'

## Log settings

# SYSLOG_TAG = "http_app_playdoh"  # Make this unique to your project.
# LOGGING = dict(loggers=dict(playdoh={'level': logging.DEBUG}))

# Common Event Format logging parameters
#CEF_PRODUCT = 'Playdoh'
#CEF_VENDOR = 'Mozilla'

BADGER_ALLOW_ADD_BY_ANYONE = True

FACEBOOK_APP_ID = "APP ID"
FACEBOOK_ADMINS = "ADMIN ID"

# Uncomment this line if you are running a local development install without
# HTTPS to disable HTTPS-only cookies.
#SESSION_COOKIE_SECURE = False

BADGEKIT_API_ENDPOINT = os.environ.get('BADGEKIT_API_ENDPOINT')
BADGEKIT_API_AUTH = {
  'key': os.environ.get('BADGEKIT_API_KEY'),
  'secret': os.environ.get('BADGEKIT_API_SECRET')
}
BADGEKIT_API_SYSTEM = os.environ.get('BADGEKIT_API_SYSTEM')

ROA_MODELS = True

