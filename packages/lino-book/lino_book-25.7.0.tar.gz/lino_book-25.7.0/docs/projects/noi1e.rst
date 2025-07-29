.. doctest docs/projects/noi1e.rst
.. _dg.projects.noi1e:

==================================================
``noi1e`` : A Lino Noi using ExtJS front end
==================================================

An example of a :ref:`noi` using the :term:`ExtJS front end`.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

>>> ses = rt.login('robin')

>>> settings.SITE.default_ui
'lino.modlib.extjs'
