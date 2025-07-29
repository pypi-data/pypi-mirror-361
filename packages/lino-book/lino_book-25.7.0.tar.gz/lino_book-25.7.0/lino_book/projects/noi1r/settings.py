# -*- coding: UTF-8 -*-
# Copyright 2015-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_book.projects.noi1e.settings.demo import *


class Site(Site):
    default_ui = 'lino_react.react'
    # title = "Noi React demo"
    title = "noi1r"
    master_site = SITE
    # languages = ["de", "en"]
    # log_each_action_request = True
    # use_elasticsearch = True
    # use_ipdict = True

    if False:

        def get_installed_plugins(self):
            yield super().get_installed_plugins()
            # yield 'lino.modlib.chat'
            # yield 'lino_xl.lib.mastodon'


SITE = Site(globals())
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# from django.utils.log import DEFAULT_LOGGING
# from pprint import pprint
# pprint(DEFAULT_LOGGING)
