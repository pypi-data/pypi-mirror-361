# -*- coding: UTF-8 -*-
# Copyright 2002-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""The :mod:`lino_book` package contains a set of example projects
used both for testing and explaining Lino framework.

It is not published on PyPI because that would make no sense.  You use it by
cloning the repository from GitLab (which is done automatically by
:cmd:`getlino configure` with `--devtools`).

.. autosummary::
   :toctree:

   projects

"""

from pathlib import Path

# from .setup_info import SETUP_INFO

__version__ = '25.7.0'
# intersphinx_urls = dict(docs="http://www.lino-framework.org")
# srcref_url = 'https://github.com/lino-framework/book/blob/master/%s'
srcref_url = 'https://gitlab.com/lino-framework/book/-/tree/master/%s'

doc_trees = ['docs']
# doc_trees = [ 'docs', 'apcdocs']
intersphinx_urls = {
    'docs': "https://dev.lino-framework.org",
    # 'apcdocs': "https://apcdocs.lino-framework.org",
}

DEMO_DATA = Path(__file__).parent.parent.absolute() / 'demo_data'
"""
The root directory for our demo data collection, which is used by other projects
as well.

This is a :class:`Path` instance.

"""
