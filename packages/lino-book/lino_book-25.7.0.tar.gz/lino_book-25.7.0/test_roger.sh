#!/bin/bash
# Copyright 2021 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
# run the tests that use the roger demo project

set -e  # exit on error

doctest docs/specs/checkdata.rst
doctest docs/specs/invoicing.rst
doctest docs/specs/voga/print_labels.rst
doctest docs/specs/voga/checkdata.rst
doctest docs/specs/voga/invoicing.rst
doctest docs/specs/voga/roger.rst
doctest docs/specs/voga/voga.rst
doctest docs/specs/voga/pupils.rst
doctest docs/specs/voga/holidays.rst
doctest docs/specs/voga/partners.rst
doctest docs/specs/voga/usertypes.rst
doctest docs/specs/voga/cal.rst
doctest docs/specs/voga/sales.rst
doctest docs/specs/voga/courses.rst
doctest docs/specs/voga/ledger.rst
doctest docs/specs/voga/presences.rst
doctest docs/specs/weasyprint.rst

cd lino_book/projects/roger
python manage.py test
