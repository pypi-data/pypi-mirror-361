# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *


class Site(Site):
    title = "Lino Mini 2"
    demo_fixtures = 'std demo demo2'
    user_types_module = 'lino_xl.lib.xl.user_types'
    workflows_module = 'lino_xl.lib.cal.workflows.feedback'
    use_experimental_features = True

    def setup_quicklinks(self, user, tb):
        super(Site, self).setup_quicklinks(user, tb)
        tb.add_action(self.modules.contacts.Persons)
        tb.add_action(self.modules.contacts.Companies)

    # def setup_plugins(self):
    #     super(Site, self).setup_plugins()
    #     self.plugins.contacts.configure(use_vcard_export=True)

    def get_installed_plugins(self):
        yield super(Site, self).get_installed_plugins()

        yield 'lino.modlib.system'
        yield 'lino.modlib.users'
        yield 'lino_xl.lib.contacts'
        yield 'lino_xl.lib.cal'
        yield 'lino.modlib.export_excel'
        yield 'lino.modlib.checkdata'
