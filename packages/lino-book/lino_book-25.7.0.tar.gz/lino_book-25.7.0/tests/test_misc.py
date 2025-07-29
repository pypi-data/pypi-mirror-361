# -*- coding: UTF-8 -*-
# Copyright 2010-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# $ python -m unittest tests.test_misc
# $ pytest tests/test_misc.py

import sys

from pathlib import Path
import shutil

from lino.utils.pythontest import TestCase


class LinoTestCase(TestCase):
    django_settings_module = "lino_book.projects.min9.settings"
    project_root = Path(__file__).parent.parent


class DumpTests(LinoTestCase):

    def test_double_dump(self):
        # Run a double-dump test in a few demo projects
        for prj in ["belref", "min1"]:
            p = Path("lino_book", "projects", prj)
            tmp = (p / 'tmp').absolute()
            shutil.rmtree(tmp, ignore_errors=True)
            self.assertFalse(tmp.exists())
            self.run_django_admin_command_cd(str(p), 'dump2py', str(tmp))
            self.assertTrue((tmp / 'restore.py').exists())
            self.run_django_admin_command_cd(str(p), 'run',
                                             str(tmp / 'restore.py'),
                                             "--noinput")
            tmp2 = (p / 'tmp2').absolute()
            shutil.rmtree(tmp2, ignore_errors=True)
            self.assertFalse(tmp2.exists())
            self.run_django_admin_command_cd(str(p), 'dump2py', str(tmp2))

            self.run_subprocess(["diff", tmp, tmp2], cwd=p)

            # Above `diff` of the two directories compares all the files in both
            # directories and exits with an error code 1 as soon as a single
            # byte differs in one of these files. Here is how I verified this:

            # (tmp / 'restore.py').unlink()
            # self.run_subprocess(["diff", tmp, tmp2], cwd=p)

            # txt1 = (tmp / 'restore.py').read_text()
            # txt2 = (tmp2 / 'restore.py').read_text()
            # self.assertEqual(txt1, txt2)

            shutil.rmtree(tmp)
            shutil.rmtree(tmp2)
