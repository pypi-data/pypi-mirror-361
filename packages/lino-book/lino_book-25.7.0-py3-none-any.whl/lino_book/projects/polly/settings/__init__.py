# -*- coding: UTF-8 -*-
# Copyright 2013-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *

# from django.utils.translation import gettext_lazy as _


class Site(Site):
    """
    Base class for a :ref:`polly` application,
    designed to be instantiated into the :setting:`SITE` setting.
    """

    verbose_name = "Lino Polly"
    description = "Create questionaires for polls and manage responses."
    version = "0.1"
    # url = "https://www.lino-framework.org/examples/polly"
    author = 'Luc Saffre'
    author_email = 'luc.saffre@gmail.com'
    is_demo_site = True

    # default_ui = "lino_react.react"

    demo_fixtures = 'std demo feedback compass demo2'.split()
    # user_types_module = 'lino_book.projects.polly.user_types'
    user_types_module = 'lino_xl.lib.xl.user_types'

    languages = 'en de et'

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino.modlib.gfks'
        yield 'lino.modlib.users'
        yield 'lino_xl.lib.polls'
