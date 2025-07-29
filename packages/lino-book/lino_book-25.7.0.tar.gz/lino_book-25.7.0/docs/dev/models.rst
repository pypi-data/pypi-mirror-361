.. doctest docs/dev/models.rst

.. _dev.models:

===============================
Introduction to database models
===============================

.. contents::
    :depth: 1
    :local:

Lino applications fully use Django's :term:`ORM`.  Every :term:`database table`
is described by a subclass of :class:`django.db.models.Model`.  Every :term:`row
<database row>` of a database table is represented in your Python code as an
instance of that class.

The database models of an application are grouped into :doc:`plugins <plugins>`.
Django calls them "applications", but we prefer the word "plugin". A plugin is a
Python package with at least one file called  :xfile:`models.py`.  Here is the
:xfile:`models.py` file we are going to use in this tutorial:

.. literalinclude:: /../../book/lino_book/projects/tables/models.py

This file is defined in the ``tables`` demo project.  You can try the code
snippets on this page from within a Django shell in that project::

  $ go tables
  $ pm shell

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tables.settings')
>>> from django.conf import settings

.. initialize the database:

  We must run pm prep each time for this document because deleting a row is not
  enough. A second test run would fail because the automatic id of new authors
  changes.

    >>> from atelier.sheller import Sheller
    >>> shell = Sheller(settings.SITE.project_dir)
    >>> shell('python manage.py prep --noinput')
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
    `initdb demo` started on database .../default.db.
    ...
    Loading data from ...lino_book/projects/tables/fixtures/demo.py
    Installed 7 object(s) from 1 fixture(s)

  We must import doctest only now because (since 20221019) it calls
  check_virgin(), which opens the database in the test runner process. If we run
  prep in a subprocess while our db is open, sqlite will turn to readonly mode.

  >>> from lino.api.doctest import *

Accessing the database
======================

We import our two models:

>>> from lino_book.projects.tables.models import Author, Book

Every :class:`Model` has a class attribute :attr:`objects` which is
used for operations that *access the database*.

For example you can *count* how many authors are stored in our database.

>>> Author.objects.count()
3

Or you can loop over them:

>>> for a in Author.objects.all():
...     print(a)
Adams, Douglas
Camus, Albert
Huttner, Hannes


You can create a new author by saying:

>>> obj = Author(first_name="Joe", last_name="Doe")

That row is not yet stored in the database, but you can already use
it.  For example you can access the individual fields:

>>> print(obj.first_name)
Joe
>>> print(obj.last_name)
Doe

For example it has a :meth:`__str__` method:

>>> print(obj)
Doe, Joe

You can change the value of a field:

>>> obj.last_name = "Woe"

>>> print(obj)
Woe, Joe

In order to store our object to the database, we call its :meth:`save`
method::

>>> obj.full_clean()  # see later
>>> obj.save()

Our database now knows a new author, Joe Woe:

>>> Author.objects.count()
4
>>> for a in Author.objects.all():
...     print(a)
Adams, Douglas
Camus, Albert
Huttner, Hannes
Woe, Joe


The :meth:`all` method of the :attr:`objects` of a :class:`Model`
returns what Django calls a **queryset**.

.. glossary::

  queryset

    A volatile Python object that describes an ``SQL SELECT`` statement.

When you have a queryset object, you can see the SQL that it would generate in
order to retrieve data from the :term:`database server`:

>>> qs = Author.objects.all()
>>> print(qs.query)
SELECT "tables_author"."id", "tables_author"."first_name", "tables_author"."last_name", "tables_author"."country" FROM "tables_author"

>>> qs = Author.objects.filter(first_name="Joe")
>>> print(qs.query)
SELECT "tables_author"."id", "tables_author"."first_name", "tables_author"."last_name", "tables_author"."country" FROM "tables_author" WHERE "tables_author"."first_name" = Joe

>>> qs.count()
1
>>> qs
<QuerySet [Author #4 ('Woe, Joe')]>

Before going on we tidy up by removing Joe Woe from our demo database:

>>> obj.delete()
>>> Author.objects.count()
3


Validating data
===============

You should always call the :meth:`full_clean` method of an object
before actually calling its :meth:`save` method.  Django does not do
this automatically because they wanted to leave this decision to the
developer.

For example, we did not specify that the :attr:`last_name` of an
author may be empty.  So Django will complain if we try to create an
author without last_name:

>>> author = Author(first_name="Joe")
>>> author.full_clean() #doctest: +NORMALIZE_WHITESPACE +IGNORE_EXCEPTION_DETAIL +ELLIPSIS
Traceback (most recent call last):
...
ValidationError: {'last_name': ['This field cannot be blank.']}

Note that Django complains only when we call :meth:`full_clean` (not already
when instantiating the model).

Note that the :attr:`country` field is declared with `blank=True`, so
this field is optional.

The :class:`ValidationError` is a special kind of exception, which
contains a dictionary that can contain one error message for every
field. In the Book model we have three mandatory fields: the
:attr:`title`, the :attr:`price` and the year of publication
(:attr:`published`).  Giving only a title is not enough:

>>> book = Book(title="Foo")
>>> book.full_clean() #doctest: +NORMALIZE_WHITESPACE +IGNORE_EXCEPTION_DETAIL +ELLIPSIS
Traceback (most recent call last):
...
ValidationError: {'price': ['This field cannot be null.'], 'published': ['This field cannot be null.']}


The :class:`Book` model also shows how you can define custom validation rules
that may depend on complex conditions which involve more than one
field.

>>> book = Book(title="Foo", published=2001, price='4.2')
>>> book.full_clean() #doctest: +NORMALIZE_WHITESPACE +IGNORE_EXCEPTION_DETAIL +ELLIPSIS
Traceback (most recent call last):
...
ValidationError: ['A book from 2001 for only $4.20!']


More about database models
==========================

Tim Kholod wrote a nice introduction for beginners: `The simple way to
understand Django models <https://arevej.me/django-models/>`__

If you want to know more about Django's way to access the database
using models, read the Django documentation about
`Models and databases
<https://docs.djangoproject.com/en/5.0//topics/db/>`__.

See the reference page :doc:`/topics/model`.
