.. doctest docs/plugins/blogs.rst
.. _dg.plugins.blogs:

====================================
``blogs`` : Blogging functionality
====================================

.. currentmodule:: lino_xl.lib.blogs

The :mod:`lino_xl.lib.blogs` plugin adds blogging functionality.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *

Which means that code snippets in this document are tested using the
:mod:`lino_book.projects.cms1` demo project.


.. class:: Blog

  The Django model to represent a :term:`blog`.

.. class:: Entry

  The Django model to represent a :term:`blog entry`.

  .. attribute:: pub_date

    The publication date.

  .. attribute:: user

    The author.

  .. attribute:: blog

    The :term:`blog` to which this entry belongs.

    This is a :term:`foreign key` pointing to :class:`Blog`.

  .. attribute:: title
  .. attribute:: body
