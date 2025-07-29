# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# This script gets imported from doctests. It does some assertions to ensure
# that the database content hasn't been modified e.g. by some other doctest.

#fmt: off

from lino import startup
startup('lino_book.projects.noi2.settings')
from lino.api.doctest import *

dbhash.check_virgin()

# for obj in linod.SystemTask.objects.filter(requested_at__isnull=False):
#     print(f"Oops, {obj} has requested_at")
