Files
=====

.. xfile:: media/cache/wsdl

  See :blogref:`20120508`.

.. xfile:: models.py

The file that defines the :term:`database models <database model>` of a plugin.

Every plugin usually has such a file, and Django imports them automatically
during startup. See :doc:`/dev/plugins`.

.. xfile:: ui.py

A file that defines the data tables (the "user interface") provided by a plugin.

By convention this file, if it exists, is to be imported  into the
:xfile:`models.py` file using a line ``from .ui import *`` at the bottom of that
file.



.. xfile:: urls.py

See https://docs.djangoproject.com/en/5.0/intro/tutorial01/#creating-a-project

.. xfile:: manage.py

See https://docs.djangoproject.com/en/5.0/intro/tutorial01/#creating-a-project

.. xfile:: __init__.py

The Python language requires a file :xfile:`__init__.py` in each
directory that is to be considered as a package.  Read the `Packages
<https://docs.python.org/3/tutorial/modules.html#packages>`_ chapter
of the Python Tutorial for more.

The :xfile:`__init__.py` files of a Django app are often empty, but
with Lino these files can contain :class:`lino.core.plugin.Plugin` class
definitions.

.. xfile:: media

This is the directory where Lino expects certain subdirs.

.. xfile:: .po

:xfile:`.po` files are gettext catalogs.
They contain chunks of English text as they appear in Lino,
together with their translation into a given language.
See :doc:`/dev/translate/index`.

.. xfile:: linolib.js
.. xfile:: lino.js

These are obsolete synonyms for :xfile:`linoweb.js`.


.. xfile:: .weasy.html

An input template used by :mod:`lino.modlib.weasyprint`.
