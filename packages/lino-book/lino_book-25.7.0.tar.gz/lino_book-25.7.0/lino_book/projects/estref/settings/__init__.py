# -*- coding: UTF-8 -*-
# Copyright 2014 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *

from django.utils.translation import gettext_lazy as _


class Site(Site):

    verbose_name = "Lino EstRef"
    description = _("Estonian Reference")
    version = "0.1"
    url = "http://www.lino-framework.org/estref.html"
    author = 'Luc Saffre'
    author_email = 'luc.saffre@gmail.com'

    demo_fixtures = 'all_countries demo eesti'

    default_ui = 'lino_react.react'
    languages = 'et en'

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino.modlib.system'
        yield 'lino_xl.lib.countries'
        # yield 'lino_xl.lib.concepts'
        yield 'lino_book.projects.estref'
