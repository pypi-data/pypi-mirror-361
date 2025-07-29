.. doctest docs/specs/xl.rst
.. _book.specs.xl:

============================================
``xl`` : General utilities for XL plugins
============================================

.. currentmodule:: lino_xl.lib.xl

The :mod:`lino.modlib.xl` plugin is installed in every application that uses at
least one Lino XL plugin. It does not define any models, but a :xfile:`locale`
directory with translation messages for Django.

It also adds some utilities.

See also :ref:`dev.xl`.



.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min1.settings')
>>> from lino.api.doctest import *

Which means that code snippets in this document are tested using the
:mod:`lino_book.projects.min1` demo project.


The ``Priorities`` choicelist
=============================

.. class:: Priorities

>>> rt.show(xl.Priorities)
======= ========== ==========
 value   name       text
------- ---------- ----------
 10      critical   Critical
 20      high       High
 30      normal     Normal
 40      low        Low
 50      very_low   Very Low
======= ========== ==========
<BLANKLINE>

Used by :attr:`lino_xl.lib.cal.Task.priority` and
:attr:`lino_xl.lib.tickets.Ticket.priority`.


The ``locale`` directory of XL
===============================

.. xfile:: lino_xl/lib/xl/locale
