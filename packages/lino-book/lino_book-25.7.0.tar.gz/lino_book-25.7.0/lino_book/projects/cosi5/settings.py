# -*- coding: UTF-8 -*-
# Copyright 2014-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

from lino_cosi.lib.cosi.settings import *


class Site(Site):
    languages = 'en bn'
    # languages = 'es en'

    demo_fixtures = 'std minimal_ledger \
    furniture demo demo_bookings payments demo2'.split()

    # temporary:
    # demo_fixtures = 'std all_countries minimal_ledger \
    # furniture demo demo_bookings demo2'.split()

    #demo_fixtures = 'std few_countries minimal_ledger \
    #furniture \
    #demo demo_bookings payments demo2'.split()

    # use_shopping = True
    is_demo_site = True
    # ignore_dates_after = datetime.date(2019, 05, 22)
    the_demo_date = datetime.date(2021, 6, 12)
    default_ui = 'lino_react.react'

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # yield ('vat', 'declaration_plugin', 'lino_xl.lib.eevat')
        yield ('countries', 'hide_region', False)
        yield ('countries', 'country_code', 'BD')
        yield ('accounting', 'use_pcmn', True)
        yield ('periods', 'start_year', 2021)
        yield ('accounting', 'sales_method', 'pos')
        yield ('accounting', 'has_payment_methods', True)
        # yield ('invoicing', 'voucher_model', 'trading.CashInvoice')
        # yield ('invoicing', 'voucher_type', 'trading.CashInvoicesByJournal')


SITE = Site(globals())
DEBUG = True
