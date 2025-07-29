=======================================
Migrate from setup.py to pyproject.toml
=======================================

How to migrate a package repository
===================================

- Replace :xfile:`setup.py` by :xfile:`pyproject.toml`
- Say :cmd:`pip uninstall lino` followed by :cmd:`pip install -e lino`
- Check whether you need a `__version__`  variable.

How to get the version
======================

Old::

  from .setup_info import SETUP_INFO
  __version__ = SETUP_INFO["version"]

New::

  from xyz import __version__

For other metadata than the version, see usage example in
:file:`synodal/make_code.py`::

  from importlib import metadata
  description = metadata.metadata("xyz")['Summary']


How to release a new version after migrating from setup to pyproject
====================================================================

See :ref:`dg.howto.release`.


How to get other metadata than the version
==========================================

For example :meth:`lino.core.site.Site.get_used_libs` wants the "url", which is
now in the ``[project.urls]`` table, under "Homepage" or "Repository" key.
