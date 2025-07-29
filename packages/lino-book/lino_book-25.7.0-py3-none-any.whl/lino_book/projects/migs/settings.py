# -*- coding: UTF-8 -*-
# Copyright 2014-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_noi.lib.noi.settings import *


class Site(Site):

    workflows_module = 'lino_book.projects.migs.workflows'
    is_demo_site = True
    the_demo_date = 20150523
    languages = "en de fr"

    # readonly = True
    # use_linod = True

    def get_installed_plugins(self):
        # add lino.modlib.restful to the std list of plugins
        yield super().get_installed_plugins()
        yield 'lino.modlib.restful'
        # yield 'lino_xl.lib.caldav'
        # yield 'lino_xl.lib.mailbox'

    def setup_plugins(self):
        super().setup_plugins()
        if self.is_installed('extjs'):
            self.plugins.extjs.configure(enter_submits_form=False)

    def get_plugin_configs(self):
        for i in super().get_plugin_configs():
            yield i
        yield ('excerpts', 'responsible_user', 'jean')
        # yield ('memo', 'front_end', 'react')


SITE = Site(globals())

DEBUG = True
ALLOWED_HOSTS = ["*"]
