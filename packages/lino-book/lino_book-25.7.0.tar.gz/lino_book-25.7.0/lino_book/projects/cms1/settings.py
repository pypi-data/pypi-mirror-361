# -*- coding: UTF-8 -*-
# Copyright 2022-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_cms.lib.cms.settings import *
from lino_book import DEMO_DATA

class Site(Site):

    copyright_name = "Example Ltd."
    copyright_url = "https://www.example.com"

    is_demo_site = True
    the_demo_date = 20220920
    languages = "en de fr"

    # default_ui = 'lino.modlib.extjs'

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # yield ('memo', 'use_markup', True)
        yield ('inbox', 'mailbox_path', DEMO_DATA / 'Maildir')
        yield ('inbox', 'mailbox_type', 'mailbox.Maildir')


from lino.core.auth.utils import activate_social_auth_testing
activate_social_auth_testing(globals())

SITE = Site(globals())

DEBUG = True

USE_TZ = True
TIME_ZONE = 'UTC'

# the following line should not be active in a checked-in version
# DATABASES['default']['NAME'] = ':memory:'
