# -*- coding: UTF-8 -*-
# Copyright 2012-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *
from lino.utils import i2d


class Site(Site):
    title = "Lino Mini 1"
    demo_fixtures = 'std demo demo2'
    user_types_module = 'lino_xl.lib.xl.user_types'
    use_experimental_features = True
    languages = "en de fr"
    the_demo_date = i2d(20141023)
    is_demo_site = True
    # history_aware_logging = True

    # use_ipdict = True
    # default_ui = "lino_react.react"
    # languages = "en bn"

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino.modlib.system'
        yield 'lino.modlib.users'
        yield 'lino_xl.lib.contacts'

    def setup_quicklinks(self, user, tb):
        super().setup_quicklinks(user, tb)
        tb.add_action(self.modules.contacts.Persons)
        tb.add_action(self.modules.contacts.Companies)


SITE = Site(globals())
DEBUG = True
