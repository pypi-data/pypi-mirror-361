# -*- coding: UTF-8 -*-
# Copyright 2014-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_cosi.lib.cosi.settings import *


class Site(Site):
    # languages = 'en zh-hant'
    languages = 'en es'

    demo_fixtures = 'std minimal_ledger \
    furniture demo demo_bookings payments demo2 checkdata'.split()

    # temporary:
    # demo_fixtures = 'std all_countries minimal_ledger \
    # furniture demo demo_bookings demo2'.split()

    #demo_fixtures = 'std few_countries minimal_ledger \
    #furniture \
    #demo demo_bookings payments demo2'.split()

    is_demo_site = True
    # ignore_dates_after = datetime.date(2019, 05, 22)
    the_demo_date = 20240308

    # default_ui = 'lino_react.react'

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # yield ('vat', 'declaration_plugin', 'lino_xl.lib.eevat')
        yield ('contacts', 'demo_region', 'UY')
        yield ('countries', 'hide_region', False)
        yield ('countries', 'country_code', 'UY')
        yield ('countries', 'full_data', True)
        yield ('accounting', 'use_pcmn', True)
        yield ('periods', 'start_year', 2024)


SITE = Site(globals())
DEBUG = True
