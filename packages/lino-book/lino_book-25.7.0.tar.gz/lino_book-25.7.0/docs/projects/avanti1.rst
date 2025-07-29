.. doctest docs/projects/avanti1.rst
.. _dg.projects.avanti1:

==================================================
``avanti1`` : A Lino Avanti
==================================================

An example of a :ref:`avanti` using the :term:`React front end`.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *
>>> ses = rt.login('robin')

>>> settings.SITE.default_ui
'lino_react.react'
