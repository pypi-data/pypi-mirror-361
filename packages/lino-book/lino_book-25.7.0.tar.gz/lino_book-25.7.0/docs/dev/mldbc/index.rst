.. doctest docs/dev/mldbc/index.rst
.. _mldbc_tutorial:

=============================================
Introduction to multilingual database content
=============================================

One feature of Lino is its built-in support for :ref:`single-table
multilingual database content <mldbc>`.  This document explains what it is.


.. contents::
   :local:
   :depth: 2


Note that this is **not** about internationalization (i18n).
*Internationalization* is when the :term:`front end` can speak different
languages. Lino uses the existing Django techniques about `Internationalization
<https://docs.djangoproject.com/en/5.0/topics/i18n/>`__.


When to use MLDBC
=======================

Imagine a Canadian company that wants to print catalogues and price offers in
two different languages, either English or French, depending on the customer's
preferred language. They don't want to maintain different product tables because
it is one company, one accounting, and prices are the same in French and in
English.  They need a Products table like this:

  +------------------+------------------+-------------+-------+----+
  | Designation (en) | Designation (fr) | Category    | Price | ID |
  +==================+==================+=============+=======+====+
  | Chair            | Chaise           | Accessories | 29.95 | 1  |
  +------------------+------------------+-------------+-------+----+
  | Table            | Table            | Accessories | 89.95 | 2  |
  +------------------+------------------+-------------+-------+----+
  | Monitor          | Écran            | Hardware    | 19.95 | 3  |
  +------------------+------------------+-------------+-------+----+
  | Mouse            | Souris           | Accessories |  2.95 | 4  |
  +------------------+------------------+-------------+-------+----+
  | Keyboard         | Clavier          | Accessories |  4.95 | 5  |
  +------------------+------------------+-------------+-------+----+

Now imagine that your application is being used not only in Canada but also in
the United States.  Your US customers don't want to have a "useless" column for
the French designation of their products.

This is where you want multi-lingual database content. In that case you would
simply

- use a :term:`babel field` instead of Django's :class:`CharField` for
  every translatable field

- and set the :attr:`languages
  <lino.core.site.Site.languages>` attribute to ``"en"`` for your US customer and
  to ``"en fr"`` for your Canadian customer.

.. glossary::

  babel field

    A special :term:`database field` that behaves like a normal Django field but
    actually generates a series of fields in the database model, one for each
    :attr:`language <lino.core.site.Site.language>` of the site.

.. currentmodule:: lino.utils.mldbc.fields

Babel fields are implemented by :class:`BabelCharField` and
:class:`BabelTextField` defined in module :mod:`lino.utils.mldbc.fields`. The
former creates single-line :class:`CharField` while The latter creates
multi-line :class:`TextField`.



An example
==========


Go to the :mod:`lino_book.projects.mldbc` demo project::

   $ go mldbc

Make sure that the demo database is initialized::

   $ python manage.py prep

Open the interactive Django shell::

  $ pm shell


..  doctest init:
    >>> from lino import startup
    >>> startup('lino_book.projects.mldbc.settings')

>>> from lino.api.doctest import *
>>> Product = rt.models.mldbc.Product

You can print a catalog in different languages:

>>> print(', '.join([str(p) for p in Product.objects.all()]))
Chair, Table, Monitor, Mouse, Keyboard, Consultation

>>> from django.utils import translation
>>> with translation.override('fr'):
...     print(', '.join([str(p) for p in Product.objects.all()]))
Chaise, Table, Ecran, Souris, Clavier, Consultation

Here is how we got the above table:

>>> from lino.api import rt
>>> rt.show(mldbc.Products)
==================== ================== ============= ============
 Designation          Designation (fr)   Category      Price
-------------------- ------------------ ------------- ------------
 Chair                Chaise             Accessories   29,95
 Table                Table              Accessories   89,95
 Monitor              Ecran              Hardware      19,95
 Mouse                Souris             Accessories   2,95
 Keyboard             Clavier            Accessories   4,95
 Consultation         Consultation       Service       59,95
 **Total (6 rows)**                                    **207,70**
==================== ================== ============= ============
<BLANKLINE>


Screenshots
===========

The screenshots on the left have been taken on a server with
``languages = ['en']``,
those on the right on a server with
``languages = ['de','fr']``.


.. image:: babel1a.jpg
    :scale: 50

.. image:: babel1b.jpg
    :scale: 50

.. image:: babel2a.jpg
    :scale: 50

.. image:: babel2b.jpg
    :scale: 50

.. image:: babel3a.jpg
    :scale: 50

.. image:: babel3b.jpg
    :scale: 50




The :xfile:`settings.py` file
=============================

.. literalinclude:: /../../book/lino_book/projects/mldbc/settings.py

This is where you specify the :setting:`languages` setting.


The :xfile:`models.py` file
=============================

.. literalinclude:: /../../book/lino_book/projects/mldbc/models.py

In case you wonder what a choicelist is, see :doc:`/dev/choicelists`.



The `demo` fixture
==================

.. literalinclude:: /../../book/lino_book/projects/mldbc/fixtures/demo.py

Note how the application developer doesn't know which :attr:`languages
<lino.core.site.Site.languages>` will be set at runtime.

Of course the fixture above supposes a single person who knows
all the languages, but that's just because we are simplifying.
In reality you can do it as sophisticated as you want,
reading the content from different sources.

BabelFields and migrations
==========================

BabelFields cause the database structure to change when a :term:`server
administrator` locally changes the :attr:`languages
<lino.core.site.Site.languages>` setting of a :term:`Lino site`.

That's why the :term:`application developer` does not provide Django migrations for
their product.
See :doc:`/dev/datamig` and :doc:`/specs/migrate`.


Related work
============

- `django-datatrans <https://pypi.python.org/pypi/django-datatrans>`_ (Jef Geskens)
- `django-localeurl <https://pypi.python.org/pypi/django-localeurl>`_ (Carl Meyer)
- `django-transmeta <https://pypi.python.org/pypi/django-transmeta>`_ (Marc Garcia, Manuel Saelices, Pablo Martin)

TODO: write comparisons about these
