# how to run a single test:
# python -m unittest tests.test_demo.Main.test_noi1e_maketour
# python -m unittest tests.test_demo.Main.test_lydia
# python -m unittest tests.test_demo.Misc.test_makehelp
from lino.utils.pythontest import TestCase
import unittest


class Main(TestCase):

    demo_projects_root = 'lino_book/projects'

    def test_cms1(self):
        self.do_test_demo_project('cms1')

    def test_mti(self):
        self.do_test_demo_project('mti')

    def test_auto_create(self):
        self.do_test_demo_project('auto_create')

    def test_actions(self):
        self.do_test_demo_project('actions')

    def test_actors(self):
        self.do_test_demo_project('actors')

    # def test_watch(self):
    #     self.do_test_demo_project('watch_tutorial')

    def test_vtables(self):
        self.do_test_demo_project('vtables')

    def test_tables(self):
        self.do_test_demo_project('tables')

    def test_addrloc(self):
        self.do_test_demo_project('addrloc')

    def test_polls(self):
        self.do_test_demo_project('polls')

    def test_polls2(self):
        self.do_test_demo_project('polls2')

    def test_gfktest(self):
        self.do_test_demo_project('gfktest')

    def test_mldbc(self):
        self.do_test_demo_project('mldbc')

    def test_belref(self):
        self.do_test_demo_project('belref')

    def test_events(self):
        self.do_test_demo_project("events")

    def test_watch(self):
        self.do_test_demo_project("watch")

    def test_estref(self):
        self.do_test_demo_project("estref")

    def test_babel_tutorial(self):
        self.do_test_demo_project("babel_tutorial")

    def test_min1(self):
        self.do_test_demo_project("min1")

    def test_min2(self):
        self.do_test_demo_project("min2")

    def test_min9(self):
        self.do_test_demo_project("min9")

    def test_cosi1(self):
        self.do_test_demo_project('cosi1')

    def test_cosi3(self):
        self.do_test_demo_project('cosi3')

    def test_lets1(self):
        self.do_test_demo_project('lets1')

    def test_noi1e(self):
        self.do_test_demo_project('noi1e')

    def test_noi1r(self):
        self.do_test_demo_project('noi1r')

    def test_noi2(self):
        self.do_test_demo_project('noi2')

    def test_anna(self):
        self.do_test_demo_project('anna')

    def test_liina(self):
        self.do_test_demo_project('liina')

    def test_avanti(self):
        self.do_test_demo_project('avanti1')
        self.do_test_demo_project('avanti2')

    def test_tera1(self):
        self.do_test_demo_project('tera1')

    def test_voga1(self):
        self.do_test_demo_project('voga1')

    def test_voga2(self):
        self.do_test_demo_project('voga2')

    def test_nomti(self):
        self.do_test_demo_project('nomti')

    def test_lets2(self):
        self.do_test_demo_project('lets2')


class Misc(TestCase):

    def test_translate(self):
        self.run_django_manage_test('docs/dev/translate')

    def test_bs3(self):
        self.run_django_manage_test('lino_book/projects/bs3')

    def test_diamond(self):
        self.run_django_manage_test('lino_book/projects/diamond')

    def test_integer_pk(self):
        self.run_django_manage_test('lino_book/projects/integer_pk')

    def test_float2decimal(self):
        self.run_django_manage_test('lino_book/projects/float2decimal')

    @unittest.skip("""Had it working in 2021-02-xx, but then
it started to fail after a firefox upgrade. Selenium seems too unstable.""")
    def test_noi1e_maketour(self):
        self.run_django_admin_command_cd('lino_book/projects/noi1e', 'run',
                                         'maketour.py')

    def test_makehelp(self):
        # for name in ('noi1e', 'roger', 'tera1', 'cosi1'):
        for name in ('voga2', ):
            self.run_django_admin_command_cd('lino_book/projects/' + name,
                                             'makehelp')
