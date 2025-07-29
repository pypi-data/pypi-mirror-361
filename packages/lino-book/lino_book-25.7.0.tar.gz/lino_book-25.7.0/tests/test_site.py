# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# $ python -m unittest tests.test_site
# $ pytest tests/test_site.py

import sys

from pathlib import Path
import shutil

from lino.utils.pythontest import TestCase
from lino.core.site import Site

class NeededByTest(TestCase):
    # The customized uploads must come before blogs, because blogs needs albums,
    # which needs uploads:
    def test_01(self):

        class Site1(Site):
            def get_installed_plugins(self):
                yield super().get_installed_plugins()
                yield 'lino_xl.lib.blogs'
                yield 'lino_cms.lib.uploads'
                yield 'lino_xl.lib.albums'

        try:
            Site1(globals())
            self.fail("Failed to raise exception")
        except Exception as e:
            self.assertEqual(str(e),
                "Tried to install lino_cms.lib.uploads, "
                "but lino.modlib.uploads(needed by lino_xl.lib.albums) "
                "is already installed.")
