import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bootcamp.settings")

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
application = get_wsgi_application()
application = DjangoWhiteNoise(application)
