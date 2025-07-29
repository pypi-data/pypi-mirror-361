from lino.projects.std.settings import *

# configure_plugin('countries', country_code='BE')


class Site(Site):

    verbose_name = "AddressLocation tutorial"

    demo_fixtures = ["demo"]

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino_xl.lib.countries'
        yield 'lino_book.projects.addrloc'

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # self.plugins.topics.deactivate()
        yield 'countries', 'country_code', 'BE'


SITE = Site(globals())
DEBUG = True
