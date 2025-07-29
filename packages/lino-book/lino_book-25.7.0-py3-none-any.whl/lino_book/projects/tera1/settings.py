# -*- coding: UTF-8 -*-
# Copyright 2017-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_tera.lib.tera.settings import *


class Site(Site):
    title = "tera1"

    demo_fixtures = ['std', 'minimal_ledger', 'demo', 'demo_bookings',
    'payments', 'demo2']

    is_demo_site = True
    the_demo_date = 20150523
    languages = "en de fr"
    use_ipdict = True

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino.modlib.search'


SITE = Site(globals())
DEBUG = True

# SITE.plugins.tim2lino.configure(
#     languages='de fr',
#     timloader_module='lino_xl.lib.tim2lino.spzloader',
#     dbf_table_ext='.FOX',
#     #use_dbf_py=True,
#     use_dbfread=True)
