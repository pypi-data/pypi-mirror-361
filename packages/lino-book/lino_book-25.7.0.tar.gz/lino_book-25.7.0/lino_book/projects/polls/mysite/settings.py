from lino.projects.std.settings import *


class Site(Site):

    title = "First polls"
    verbose_name = "Lino Polls"
    default_ui = "lino_react.react"

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino_book.projects.polls.polls'

    def setup_menu(self, user_type, main, ar=None):
        m = main.add_menu("polls", "Polls")
        m.add_action('polls.Questions')
        m.add_action('polls.Choices')
        super().setup_menu(user_type, main)


SITE = Site(globals())

# your local settings here

DEBUG = True
