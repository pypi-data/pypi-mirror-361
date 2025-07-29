from lino.projects.std.settings import *


class Site(Site):

    # is_demo_site = True

    default_ui = "lino_react.react"

    def get_installed_plugins(self):
        # yield 'lino.modlib.users'
        yield super().get_installed_plugins()
        yield 'input_mask'

    def setup_menu(self, profile, main, ar=None):
        m = main.add_menu("foos", "Input Mask")
        m.add_action('input_mask.Foos')


SITE = Site(globals())

DEBUG = True
ALLOWED_HOSTS = ["*"]
