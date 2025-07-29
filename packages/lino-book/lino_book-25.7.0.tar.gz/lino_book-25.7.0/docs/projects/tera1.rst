.. doctest docs/projects/tera1.rst

===========================================
``tera1`` : A customized Lino Tera site
===========================================

.. module:: lino_book.projects.tera1

A :ref:`tera` site with a few local customizations.

Used in :doc:`/specs/tera/index`.


.. contents::
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *

>>> dd.demo_date()
datetime.date(2015, 5, 23)

>>> tuple(l.django_code for l in settings.SITE.languages)
('en', 'de', 'fr')
