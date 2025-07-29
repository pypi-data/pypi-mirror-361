from unipath import Path

from lino.utils.pythontest import TestCase
from lino import PYAFTER26
from lino.utils.html2xhtml import HAS_TIDYLIB
import lino

LINO_SRC = Path(lino.__file__).parent.parent + '/'


class LinoTestCase(TestCase):
    django_settings_module = "lino_book.projects.min2.settings.demo"
    project_root = Path(__file__).parent.parent


# class UtilsTests(LinoTestCase):
class UnusedTestCases:

    def test_utils(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/__init__.py')

    def test_instantiator(self):
        self.run_simple_doctests(LINO_SRC + "lino/utils/instantiator.py")

    def test_quantities(self):
        self.run_simple_doctests(LINO_SRC + "lino/utils/quantities.py")

    def test_dates(self):
        self.run_simple_doctests(LINO_SRC + "lino/utils/dates.py")

    def test_html2odf(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/html2odf.py')

    def test_jinja(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/jinja.py')

    def test_tidy(self):
        if HAS_TIDYLIB:
            self.run_simple_doctests(LINO_SRC + 'lino/utils/html2xhtml.py')

    def test_odsreader(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/odsreader.py')

    # def test_choicelists(self):
    #     self.run_simple_doctests(LINO_SRC+'lino/core/choicelists.py')

    def test_jsgen(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/jsgen.py')

    def test_format_date(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/format_date.py')

    def test_ranges(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/ranges.py')

    def test_addressable(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/addressable.py')

    def test_cycler(self):
        self.run_simple_doctests(LINO_SRC + 'lino/utils/cycler.py')
