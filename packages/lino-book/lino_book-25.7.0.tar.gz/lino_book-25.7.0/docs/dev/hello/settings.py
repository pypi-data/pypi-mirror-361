# -*- coding: UTF-8 -*-
from lino_book.projects.polly.settings import *
from lino_local.settings import *


class Site(Site):
    title = "first"
    server_url = "http://localhost"
    languages = 'en'
    # use_linod = True
    default_ui = 'lino_react.react'
    show_internal_field_names = True

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # example of local plugin settings:
        # yield ('periods', 'start_year', 2018)
        yield ('help', 'make_help_pages', True)


SITE = Site(globals())
DEBUG = True
# ALLOWED_HOSTS = ['localhost']
SECRET_KEY = '7SPXrSWRJq7hgm4LOhoKP3mHFcM'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'first',
    }
}
EMAIL_SUBJECT_PREFIX = '[first] '
