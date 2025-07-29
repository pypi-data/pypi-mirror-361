from lino.projects.std.settings import *


class Site(Site):

    title = "Second Polls"
    verbose_name = "Lino Polls v2"
    demo_fixtures = "demo demo2"
    default_ui = "lino_react.react"
    # project_name = "pools2_mysite"  # avoid name clash when LINO_CACHE_ROOT is set

    def get_installed_plugins(self):
        yield 'polls'
        yield 'lino.modlib.users'
        yield super().get_installed_plugins()

    def setup_menu(self, user_type, main, ar=None):
        m = main.add_menu("polls", "Polls")
        m.add_action('polls.Questions')
        m.add_action('polls.Choices')
        super().setup_menu(user_type, main)

    def get_plugin_configs(self):
        yield "users", "allow_online_registration", True


SITE = Site(globals())

# your local settings here

DEBUG = True
