# -*- coding: UTF-8 -*-
# Copyright 2014-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

from lino_noi.lib.noi.settings import *


class Site(Site):
    # languages = 'en et'
    languages = ['en', 'bn', 'de']

    demo_fixtures = 'std demo demo2 synodalworld checkdata'.split()

    # use_shopping = True
    is_demo_site = True
    # ignore_dates_after = datetime.date(2019, 05, 22)
    the_demo_date = 20240512

    with_polls = True
    with_cms = True
    with_accounting = False

    default_ui = None
    web_front_ends = [(None, "lino.modlib.publisher"),
                      ('admin', "lino_react.react")]

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # yield ('vat', 'declaration_plugin', 'lino_xl.lib.eevat')
        # yield ('noi', 'with_cms', True)
        # yield ('noi', 'with_accounting', False)
        yield ('countries', 'hide_region', False)
        yield ('countries', 'country_code', 'EE')
        yield ('memo', 'short_preview_length', 300)
        yield ('publisher', 'locations',
               (('b', 'blogs.LatestEntries'),
                ('p', 'publisher.Pages'),
                ('r', 'uploads.Uploads'),
                ('s', 'sources.Sources'),
                ('t', 'topics.Topics'),
                ('u', 'users.Users')))
        # yield ('accounting', 'use_pcmn', True)
        # yield ('periods', 'start_year', 2021)
        # yield ('accounting', 'sales_method', 'pos')
        # yield ('accounting', 'has_payment_methods', True)
        yield 'help', 'make_help_pages', False


SITE = Site(globals())
DEBUG = True
