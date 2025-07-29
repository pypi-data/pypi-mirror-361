# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *


class Site(Site):

    def setup_quicklinks(self, user, tb):
        super(Site, self).setup_quicklinks(user, tb)
        tb.add_action("ovfields.MyModels")

    def get_installed_plugins(self):
        yield super(Site, self).get_installed_plugins()
        yield 'lino_book.projects.ovfields'
        yield 'lino.modlib.system'


SITE = Site(globals())
DEBUG = True
