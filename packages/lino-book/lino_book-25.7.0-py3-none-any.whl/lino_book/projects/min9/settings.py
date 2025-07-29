# -*- coding: UTF-8 -*-
# Copyright 2012-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *
from lino.utils import i2d
try:
    from lino_local.settings import *
except ImportError:
    pass


class Site(Site):
    title = "Lino Mini 9"
    project_model = 'contacts.Person'
    languages = 'en de fr'
    user_types_module = 'lino_xl.lib.xl.user_types'
    demo_fixtures = """std minimal_ledger demo demo2 checkdata""".split()
    default_build_method = 'weasy2pdf'
    is_demo_site = True
    the_demo_date = i2d(20141023)
    webdav_protocol = 'davlink'
    # default_ui = "lino_react.react"

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        # yield 'lino.modlib.users'
        yield 'lino.modlib.help'
        yield 'lino_book.projects.min9.modlib.contacts'
        yield 'lino_xl.lib.excerpts'
        yield 'lino_xl.lib.addresses'
        yield 'lino_xl.lib.phones'
        yield 'lino_xl.lib.reception'
        yield 'lino_xl.lib.courses'
        yield 'lino_xl.lib.sepa'
        yield 'lino_xl.lib.notes'
        # yield 'lino_xl.lib.projects'
        yield 'lino_xl.lib.humanlinks'
        yield 'lino_xl.lib.households'
        yield 'lino_xl.lib.calview'
        # yield 'lino_xl.lib.extensible'
        yield 'lino.modlib.publisher'
        yield 'lino.modlib.export_excel'
        yield 'lino_xl.lib.dupable_partners'
        yield 'lino.modlib.checkdata'
        yield 'lino.modlib.tinymce'
        # yield 'lino.modlib.wkhtmltopdf'
        yield 'lino.modlib.weasyprint'
        yield 'lino_xl.lib.appypod'
        yield 'lino.modlib.notify'
        yield 'lino.modlib.changes'
        yield 'lino.modlib.comments'
        yield 'lino.modlib.uploads'
        yield 'lino_xl.lib.properties'
        yield 'lino_xl.lib.cv'
        yield 'lino_xl.lib.b2c'
        yield 'lino_xl.lib.trading'
        yield 'lino_xl.lib.finan'
        yield 'lino_xl.lib.shopping'
        yield 'lino_xl.lib.tickets'
        # yield 'lino_xl.lib.topics'
        yield 'lino_xl.lib.agenda'

    def get_plugin_configs(self):
        """
        Change the default value of certain plugin settings.
        """
        yield super().get_plugin_configs()
        yield ('countries', 'country_code', 'BE')
        yield ('users', 'allow_online_registration', True)
        yield ('b2c', 'import_statements_path', self.project_dir / 'sepa_in')
        yield ('topics', 'hidden', True)

    # def on_init(self):
    #     super().on_init()
    #     self.plugins.topics.deactivate()

    def do_site_startup(self):
        # lino_xl.lib.reception requires some workflow to be imported
        from lino_xl.lib.cal.workflows import feedback
        super().do_site_startup()


SITE = Site(globals())

# ALLOWED_HOSTS = ['*']
DEBUG = True
# SECRET_KEY = "20227"  # see :djangoticket:`20227`
