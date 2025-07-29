# -*- coding: utf-8 -*-
# fmt: off

import os
import sys
import datetime
from pathlib import Path

import lino
import lino_xl
import lino_book

sys.path.insert(0, str(Path(__file__).parent.absolute()))

from atelier.sphinxconf import configure; configure(globals())
from lino.sphinxcontrib import configure; configure(globals(), 'lino_book.projects.min9.settings')

language = 'en'

exclude_patterns.append('tickets/*')
#     'old/*',
#     'tickets/*',
#     'include/*',
#     'shared/include/*',
# ]

# extensions += ['sphinxcontrib.taglist']
extensions += ['rstgen.sphinxconf.blog']
extensions += ['rstgen.sphinxconf.complex_tables']
extensions += ['lino.sphinxcontrib.logo']
extensions += ['lino.sphinxcontrib.actordoc']
extensions += ['lino.sphinxcontrib.base']
# extensions += ['sphinx.ext.napoleon']

extensions += ['rstgen.sphinxconf.sigal_image']
sigal_base_url = 'https://sigal.saffre-rumma.net'

extensions += ['lino.sphinxcontrib.help_texts_extractor']
help_texts_builder_targets = {
    # 'lino.': 'lino.modlib.lino_startup',
    'lino.': 'lino',
    # 'lino.modlib.': 'lino.modlib.lino_startup',
    'lino_xl.': 'lino_xl.lib.xl',
    'lino_tera.': 'lino_tera.lib.tera',
    'lino_vilma.': 'lino_vilma.lib.vilma',
    'lino_avanti.': 'lino_avanti.lib.avanti',
    'lino_cosi.': 'lino_cosi.lib.cosi',
    'lino_care.': 'lino_care.lib.care',
    'lino_voga.': 'lino_voga.lib.voga',
    'lino_noi.': 'lino_noi.lib.noi',
    'lino_cms.': 'lino_cms.lib.cms',
    # 'lino_welfare.': 'lino_welfare.modlib.welfare',
}

if False:
    extensions += ['sphinxcontrib.blockdiag']
    # Fontpath for blockdiag (truetype font)
    blockdiag_fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'

project = "Lino Developer Guide"
html_title = "Lino Developer Guide"
copyright = '2002-{} Rumma & Ko Ltd'.format(datetime.date.today().year)

extlinks.update({
    # 'issue': (
    #     'http://code.google.com/p/lino/issues/detail?id=%s', '# '),
    # 'checkin': (
    #     'http://code.google.com/p/lino/source/detail?r=%s', 'Checkin '),
    'srcref': (lino.srcref_url, None),
    'srcref_xl': (lino_xl.srcref_url, None),
    'srcref_book': (lino_book.srcref_url, None),
    'extjs': ('http://www.sencha.com/deploy/dev/docs/?class=%s', None),
    'extux': ('http://extjs-ux.org/ext-docs/?class=%s', None),
    'djangoticket':
    ('https://code.djangoproject.com/ticket/%s', 'Django ticket #%s'),
    'welfare': ('https://welfare.lino-framework.org%s.html', None),
})

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
# if on_rtd:
#     for n in """python django
#     atelier lino
#     lino-welfare lino-faggio lino-patrols""".split():
#         intersphinx_mapping[n] = (
#             'http://%s.readthedocs.org/en/latest/' % n, None)

# from rstgen.sphinxconf import interproject
# interproject.configure(
#     globals(), 'atelier etgen eidreader getlino')
# django=('https://docs.djangoproject.com/en/5.0/', 'https://docs.djangoproject.com/en/dev/_objects/'),
# sphinx=('https://www.sphinx-doc.org/en/master/', None))
#
# intersphinx_mapping['lf'] = ('https://www.lino-framework.org/', None)
# intersphinx_mapping['cg'] = ('https://community.lino-framework.org/', None)
# intersphinx_mapping['hg'] = ('https://hosting.lino-framework.org/', None)
# intersphinx_mapping['ug'] = ('https://using.lino-framework.org/', None)

intersphinx_mapping['django'] = (
    'https://docs.djangoproject.com/en/5.0/',
    'https://docs.djangoproject.com/en/dev/_objects/')
intersphinx_mapping['sphinx'] = ('https://www.sphinx-doc.org/en/master/', None)
intersphinx_mapping['python'] = ('https://docs.python.org/3/', None)

autosummary_generate = True

#~ nitpicky = True # use -n in Makefile instead

# http://sphinx.pocoo.org/theming.html

# html_theme = "sizzle"
# html_theme_options = dict(collapsiblesidebar=True, externalrefs=True)

# todo_include_todos = True

#~ New in version 1.1
gettext_compact = True

# print 20150311, extensions, templates_path

# print 20150701, autodoc_default_flags
# raise 123

# autodoc_default_flags = ['no-imported-members']

# autodoc_inherit_docstrings = False

extensions += ['sphinx.ext.inheritance_diagram']
inheritance_graph_attrs = dict(rankdir="TB")
# inheritance_graph_attrs.update(size='"12.0, 16.0"')
inheritance_graph_attrs.update(size='"48.0, 64.0"')
inheritance_graph_attrs.update(fontsize=14, ratio='compress')

# suppress_warnings = ['image.nonlocal_uri']

# doctest_global_setup = """
# import sys
# sys.setdefaultencoding("UTF-8")
# """

# print(20210412, html_context)

# html_context.update({
#     'public_url': 'https://www.lino-framework.org',
# })

linkcheck_anchors = False
linkcheck_ignore = [r'http://localhost:\d+/']

html_use_index = True

rst_prolog = """

:doc:`Welcome </welcome>` |
:doc:`Get started </dev/getstarted>` |
:doc:`Dive </dev/diving>` |
:doc:`Contribute </contrib/index>` |
:doc:`Topics </topics/index>` |
:doc:`Reference </ref/index>` |
:doc:`Changes </changes/2025>` |
:doc:`More </about/index>`

"""
