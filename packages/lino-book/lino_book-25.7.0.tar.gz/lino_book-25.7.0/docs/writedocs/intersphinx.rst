.. doctest docs/writedocs/intersphinx.rst
.. _dg.writedocs.intersphinx:

===========================
Referring to other doctrees
===========================

The different doctrees of the Synodalsoft project often refer to each other. We
do this by populating the Sphinx configuration variable
:envvar:`intersphinx_mapping`.

.. envvar:: intersphinx_mapping

  The main configuration setting of the `sphinx.ext.intersphinx
  <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`__
  extension, which we use to make documentation links to other Sphinx doctrees.

The :func:`rstgen.sphinxconf.configure` function adds all websites of the
Synodalsoft project to :envvar:`intersphinx_mapping`. This is why you may refer
to anchors in these doctrees.

You use it by adding the following line to your :xfile:`conf.py` file::

  from rstgen.sphinxconf import configure ; configure(globals())

This will define Sphinx configuration variables into your global context, one of
them is :envvar:`intersphinx_mapping`. To make this visible in a tested code
snippet, we use a fake global context:

>>> g = dict()
>>> from rstgen.sphinxconf import configure ; configure(g)
>>> from pprint import pprint
>>> pprint(g['intersphinx_mapping'])
{'atelier': ('https://atelier.lino-framework.org', None),
 'book': ('https://dev.lino-framework.org/', None),
 'cg': ('https://community.lino-framework.org/', None),
 'etgen': ('https://etgen.lino-framework.org', None),
 'getlino': ('https://getlino.lino-framework.org', None),
 'hg': ('https://hosting.lino-framework.org/', None),
 'lf': ('https://www.lino-framework.org/', None),
 'react': ('https://react.lino-framework.org', None),
 'ss': ('https://www.synodalsoft.net/', None),
 'ug': ('https://using.lino-framework.org/', None),
 'welfare': ('https://welfare.lino-framework.org', None)}

In case you are curious, here is how :func:`rstgen.sphinxconf.configure`
populates above values to the :envvar:`intersphinx_mapping` variable:

>>> import synodal
>>> for r in synodal.REPOS_LIST:
...     if r.public_url and r.nickname and r.git_repo:
...         print("intersphinx_mapping[{!r}] = {!r}".format(r.nickname, (r.public_url, None)))
intersphinx_mapping['atelier'] = ('https://atelier.lino-framework.org', None)
intersphinx_mapping['etgen'] = ('https://etgen.lino-framework.org', None)
intersphinx_mapping['getlino'] = ('https://getlino.lino-framework.org', None)
intersphinx_mapping['welfare'] = ('https://welfare.lino-framework.org', None)
intersphinx_mapping['react'] = ('https://react.lino-framework.org', None)
intersphinx_mapping['book'] = ('https://dev.lino-framework.org/', None)
intersphinx_mapping['cg'] = ('https://community.lino-framework.org/', None)
intersphinx_mapping['ug'] = ('https://using.lino-framework.org/', None)
intersphinx_mapping['hg'] = ('https://hosting.lino-framework.org/', None)
intersphinx_mapping['lf'] = ('https://www.lino-framework.org/', None)
intersphinx_mapping['ss'] = ('https://www.synodalsoft.net/', None)

The :envvar:`intersphinx_mapping` is also populated by
:func:`rstgen.sphinxconf.interproject.configure` when you specify a list of
projects to include. This feature is currently used only by Luc's blog.
