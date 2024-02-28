"""The Celery application."""

import os

from celery import Celery
from celery.signals import setup_logging
from django.conf import settings  # noqa

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcgplayer.settings'

app = Celery('Tcgplayer')

app.config_from_object('tcgplayer.settings', namespace='CELERY')

app.conf.task_default_priority = 1


@setup_logging.connect
def config_loggers(*args, **kwags):
    from logging.config import dictConfig

    from django.conf import settings
    dictConfig(settings.LOGGING)


app.autodiscover_tasks()
