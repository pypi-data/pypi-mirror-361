# -*- coding: UTF-8 -*-
# Copyright 2013-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

from lino.projects.std.settings import *


class Site(Site):

    title = "Lino Events"
    verbose_name = "Lino Events"

    demo_fixtures = 'demo vor'.split()
    is_demo_site = True
    the_demo_date = datetime.date(2013, 5, 12)
    # default_ui = "lino_react.react"

    languages = 'de fr nl en'

    def get_installed_plugins(self):
        yield super(Site, self).get_installed_plugins()
        # yield 'lino.modlib.system'
        yield 'lino_xl.lib.countries'
        yield 'lino_xl.lib.events'

    def get_dashboard_items(self, user):
        from lino.core.dashboard import RequestItem
        for obj in self.models.events.Type.objects.order_by('id'):
            yield RequestItem(
                obj.EventsByType(renderer=self.kernel.default_renderer))


SITE = Site(globals())

DEBUG = True
