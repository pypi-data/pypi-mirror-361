from unittest import TestCase
# from lino_book.projects.diamond.main.models import PizzaBar
from lino.api import rt

# install the fix no longer needed
# from lino.core.inject import django_patch
# django_patch()


class DocTest(TestCase):

    def test_django(self):
        p = rt.models.main.PizzaBar(name="Michaels",
                                    min_age=21,
                                    specialty="Cheese",
                                    pizza_bar_specific_field="Doodle",
                                    street="E")
        self.assertEqual(p.pizza_bar_specific_field, 'Doodle')
        self.assertEqual(p.name, 'Michaels')
        self.assertEqual(p.street, 'E')

        # In Django before 1.11, the `name` field was not being initialized
        # because it is inherited from a grand-parent.
