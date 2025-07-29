from lino.projects.std.settings import *


class Site(Site):

    languages = 'en de de-be'

    demo_fixtures = ['demo']

    def get_installed_plugins(self):
        yield super(Site, self).get_installed_plugins()
        yield 'lino_book.projects.de_BE'

    def setup_menu(self, user_type, main, ar=None):
        m = main.add_menu("master", "Master")
        m.add_action('de_BE.Expressions')
        super(Site, self).setup_menu(user_type, main)


SITE = Site(globals())
