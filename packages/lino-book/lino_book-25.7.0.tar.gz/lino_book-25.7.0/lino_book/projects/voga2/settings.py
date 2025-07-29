# -*- coding: UTF-8 -*-

from lino_voga.lib.voga.settings import *


class Site(Site):

    default_ui = 'lino_react.react'

    # title = "Lino Voga for Roger"
    languages = "en de fr"

    # custom_layouts_module = "lino_book.projects.voga2.settings.layouts"

    demo_fixtures = """std minimal_ledger
    demo eiche demo_bookings payments demo2 demo3 checkdata""".split()
    is_demo_site = True
    the_demo_date = 20150522

    def get_plugin_modifiers(self, **kw):
        kw = super().get_plugin_modifiers(**kw)
        # alternative implementations:
        kw.update(courses='lino_voga.lib.roger.courses')
        return kw

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield ('countries', 'hide_region', True)
        yield ('countries', 'country_code', 'BE')
        yield ('vat', 'declaration_plugin', 'lino_xl.lib.bevats')
        yield ('accounting', 'use_pcmn', True)
        yield ('periods', 'start_year', 2014)
        # yield ('vat', 'use_online_check', True)
        # yield ('react', 'url_prefix', 'admin')
        # yield ('react', 'force_url_prefix', True)
        yield ('contacts', 'site_owner_lookup', dict(name="Die Buche V.o.G."))


SITE = Site(globals())
DEBUG = True
