from lino.projects.std.settings import *


class Site(Site):

    is_demo_site = True
    demo_fixtures = "std demo demo2"
    languages = 'en'
    # default_user = "robin"
    user_types_module = 'lino_xl.lib.xl.user_types'
    # default_ui = "lino_react.react"

    def get_installed_plugins(self):

        yield super().get_installed_plugins()
        yield 'lino_xl.lib.contacts'
        yield 'lino.modlib.changes'
        yield 'lino.modlib.users'
        yield 'lino_book.projects.watch.entries'
        # yield 'lino_xl.lib.notes'

    def setup_actions(self):
        # watch changes to Partner, Company and Entry
        # objects, grouped to their respective Partner.

        super().setup_actions()

        from lino.modlib.changes.utils import watch_changes as wc
        wc(self.models.contacts.Partner)
        wc(self.models.contacts.Company, master_key='partner_ptr')
        wc(self.models.entries.Entry, master_key='company__partner_ptr')
        # wc(self.models.notes.Note, master_key='company__partner_ptr')


SITE = Site(globals())

DEBUG = True
