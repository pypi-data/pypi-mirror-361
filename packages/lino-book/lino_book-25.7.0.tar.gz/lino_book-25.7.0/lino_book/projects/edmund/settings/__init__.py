# -*- coding: UTF-8 -*-

from lino_voga.lib.voga.settings import *


class Site(Site):

    title = "Lino Voga for Edmund"
    languages = "en et"

    demo_fixtures = """std
    minimal_ledger
    demo edmund demo2""".split()

    is_demo_site = True
    # ignore_dates_before = None
    the_demo_date = 20140926

    # ignore_dates_after = datetime.date(2019, 05, 22)

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # yield ('vat', 'declaration_plugin', 'lino_xl.lib.eevat')
        yield ('countries', 'country_code', 'EE')
        yield ('periods', 'start_year', 2014)
        yield ('contacts', 'site_owner_lookup', dict(name="Juku õpib MTÜ"))
