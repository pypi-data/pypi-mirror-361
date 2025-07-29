# -*- coding: UTF-8 -*-
# Copyright 2013-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
A Lino Voga site customized for Ivo.

"""

from lino_voga.lib.voga.settings import *


class Site(Site):

    is_demo_site = True
    the_demo_date = 20200522
    default_ui = 'lino_react.react'

    title = "Lino Voga for Ivo"
    languages = "en et"

    workflows_module = 'lino_xl.lib.courses.workflows.doodle'

    demo_fixtures = """std minimal_ledger
    demo tantsukool demo_bookings payments demo2 checkdata""".split()

    def get_plugin_modifiers(self, **kw):
        kw = super().get_plugin_modifiers(**kw)
        # alternative implementations:
        kw.update(courses='lino_voga.lib.roger.courses')
        return kw

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield ('countries', 'hide_region', True)
        yield ('countries', 'country_code', 'EE')
        yield ('vat', 'declaration_plugin', 'lino_xl.lib.eevat')
        # yield ('accounting', 'use_pcmn', True)
        yield ('periods', 'start_year', 2020)
        # yield ('react', 'url_prefix', 'admin')
        # yield ('react', 'force_url_prefix', True)
        yield ('contacts', 'site_owner_lookup', dict(name="Tantsutajad MTÜ"))


SITE = Site(globals())
DEBUG = True
