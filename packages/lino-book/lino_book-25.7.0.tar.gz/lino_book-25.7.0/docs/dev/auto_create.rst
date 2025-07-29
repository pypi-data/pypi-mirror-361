.. doctest docs/dev/auto_create.rst
.. _lino.tutorial.auto_create:

================================================
`lookup_or_create` and the `auto_create` signal
================================================

This document describes and tests the
:meth:`lookup_or_create <lino.core.model.Model.lookup_or_create>`
method and the
:attr:`auto_create <lino.core.signals.auto_create>` signal.



.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.auto_create.settings')
>>> from lino.api.doctest import *

.. flush the database to remove data from a previous test run

    >>> from django.core.management import call_command
    >>> call_command('initdb', interactive=False) #doctest: +ELLIPSIS
    `initdb ` started on database ...lino_book/projects/auto_create/default.db.
    ...
      No migrations to apply.


We define a single simple model and a handler for the auto_create signal:

.. literalinclude:: ../../lino_book/projects/auto_create/models.py

>>> from lino_book.projects.auto_create.models import Tag

..
  20190909 : for some reason (maybe inside Django) we have to define the
  receiver in the models.py file

Manually create a Tag:

>>> Tag(name="Foo").save()

A first call to `lookup_or_create`:

>>> Tag.lookup_or_create("name", "Foo")
Tag #1 ('Foo')

The signal was not emitted here because the Foo tag existed before.

>>> print(Tag.lookup_or_create("name", "Bar"))
My handler was called with Bar
Bar

>>> print(list(Tag.objects.all()))
[Tag #1 ('Foo'), Tag #2 ('Bar')]

Voilà.
