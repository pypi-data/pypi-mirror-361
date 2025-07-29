# -*- coding: UTF-8 -*-
# Copyright 2017-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *

try:
    from lino_local.settings import *
except ImportError:
    pass


class Site(Site):
    verbose_name = "Lino Chatter"
    description = "A simple chatting app"
    the_demo_date = 20240406
    is_demo_site = True

    demo_fixtures = ('std', 'demo', 'demo2', 'checkdata')
    user_types_module = 'lino_xl.lib.xl.user_types'
    use_ipdict = True

    languages = 'en'

    default_ui = "lino_react.react"

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # yield ('notify', 'use_push_api', True)
        yield 'linod', 'use_channels', True
        yield 'users', 'with_nickname', True
        yield 'users', 'allow_online_registration', True

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino.modlib.users'
        yield 'lino_xl.lib.groups'
        yield 'lino.modlib.comments'
        yield 'lino.modlib.notify'


SITE = Site(globals())

DEBUG = True
