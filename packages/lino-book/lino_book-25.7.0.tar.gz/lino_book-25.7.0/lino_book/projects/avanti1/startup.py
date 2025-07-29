# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# This script gets imported from doctests. It does some assertions to ensure
# that the database content hasn't been modified e.g. by some other doctest.

# fmt: off

import lino
lino.startup('lino_book.projects.avanti1.settings')
from lino.api.doctest import *

dbhash.check_virgin()
