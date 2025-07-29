.. doctest docs/dev/tables/index.rst
.. _lino.tutorial.tables:

===========================
Introduction to tables
===========================


.. contents::
    :depth: 1
    :local:

Tables aren't models
=====================

A :term:`table`, in Lino, is a Python class that describes how to render a set
of data rows.

While a :term:`model <database model>` describes how data is *stored in the
database*, a :term:`table` describes how data is *presented to end users*.

While models are known to every Django developer, tables exist only in the Lino
framework.

By convention, models are named using the *singular* form of a noun while tables
are named using the *plural* form.

A same :term:`table` can be used to render data

- interactively in a web :term:`front end`
- as a :term:`printable document`
- in a :term:`tested document`

When a table is being rendered, this is done using a given :term:`display mode`.
The default display mode is ``grid``.

Lino differentiates between :term:`model-based tables <model-based table>` and
:term:`virtual tables <virtual table>`.  A model-based table gets its data
directly from the database using a Django model, a virtual table has no database
model associated, it gets its data programmatically.

..
  Don't mix up Lino's data tables with `Django's views
  <https://docs.djangoproject.com/en/5.0/topics/http/views/>`__.  With Lino you
  don't need to write Django views because Lino writes them for you. A single
  :term:`data table` can lead to multiple Django views.

Model-based tables are subclasses of
:class:`lino.core.dbtables.Table` (generally imported via its shortcut
:mod:`dd.Table <lino.api.dd>`), *virtual tables* are subclasses of
:class:`lino.core.tables.VirtualTable` (generally imported via its shortcut
:mod:`dd.VirtualTable <lino.api.dd>`).

To define tables, you simply declare their classes. Lino discovers and analyzes
them during :term:`site startup`. For this to work, tables must be defined in
your :xfile:`models.py`. You might prefer to actually define them in a separate
file and import them into your :xfile:`models.py` by saying::

   from .ui import *

By convention we name such a file :xfile:`ui.py`.

Tables never get instantiated.

Each table has a list of :term:`actions <action>` and a set of :term:`layouts
<layout>`.

The remaining part of this page focuses on :term:`model-based tables
<model-based table>`, for :doc:`virtual tables </dev/vtables>` we have a
separate page.


The ``tables`` demo project
===========================

To illustrate :term:`model-based tables <model-based table>`, we will
have a look at the :mod:`tables <lino_book.projects.tables>` demo project.

Here are the :term:`database models <database model>`:

.. literalinclude:: /../../book/lino_book/projects/tables/models.py

And here are the :term:`tables <table>`:

.. literalinclude:: /../../book/lino_book/projects/tables/ui.py

.. Note that using a :xfile:`desktop.py` file is deprecated.


>>> from lino import startup
>>> startup('lino_book.projects.tables.settings')

All tables are globally available at runtime in the :mod:`lino.api.rt` module.

>>> from lino.api import rt, dd
>>> rt.models.tables.Books
lino_book.projects.tables.ui.Books
>>> issubclass(rt.models.tables.Books, dd.Table)
True

A given database model can have multiple tables. For example, there are three
tables based on the :class:`Book` model: :class:`Books`, :class:`BooksByAuthor`
and :class:`RecentBooks`.

There can be more than one table for a given database model, but each
(model-based) table has exactly one model as its data source. This model is
specified in the :attr:`model <lino.core.dbtables.Table.model>` attribute.

For every database model there should be at least one table, otherwise Lino will
generate a default table for it during :term:`site startup`.

Much information about your table is automatically extracted from the model:
the **columns** correspond to the *fields* of your database model.  The
**header** of every column is the `verbose_name` of its field.  The values in a
column are of same **data type** for each row. So Lino knows all these things
from your models.

The **rows** of a table can be **sorted** and **filtered**. These things are
done in Django on a :class:`QuerySet`.  Lino forwards them to their
corresponding Django methods: :attr:`order_by
<lino.core.tables.AbstractTable.order_by>`, :attr:`filter
<lino.core.tables.AbstractTable.filter>` and :attr:`exclude
<lino.core.tables.AbstractTable.exclude>`.

But here is something you cannot express on a Django model: *which*
columns are to be shown, and how they are ordered.  This is defined by
the :attr:`column_names <lino.core.tables.AbstractTable.column_names>`
attribute, a simple string with a space-separated list of field names.

Tables can hold information that goes beyond a database model or a queryset. For
example we set :attr:`hide_sums <lino.core.tables.AbstractTable.hide_sums>` to
`True` on the ``Books`` table because otherwise Lino would display a sum for the
"published" column.


.. _slave_tables:

Slave tables
============

A :term:`table` is called a **slave table** when it "depends" on a master.

For example the :class:`BooksByAuthor` table shows the *books* written by a
given *author*. You cannot ask Lino to render the :class:`BooksByAuthor` table
if you don't specify for *which* author you want it. A slave table cannot render
if we don't define the master.


..
  Or the `ChoicesByQuestion` table in
  :ref:`lino.tutorial.polls`
  shows the *choices* for a given *question*
  (its master).  Other examples of slave tables are used in
  :ref:`dev.lets` and :doc:`/dev/display_modes`.


Slave tables are often rendered as elements of a :term:`detail layout`.  In this
case Lino renders them in a *slave panel* widget, and the current record is the
master.

See also :doc:`/dev/slave_tables`.


Designing your data
=====================

Tables may inherit from other tables. For example, :class:`BooksByAuthor`
inherits from :class:`Books`: it is basically a list of books, with the
difference that it shows only the books of a given author.

Each model-based table must have at least one class attribute :attr:`model
<lino.core.dbtables.Table.model>`, which points to the model on which this table
will "work". Every row of a table represents an instance of its model.

Since tabless are normal Python classes, they can use inheritance.  In our
code `BooksByAuthor` inherits from `Books`.  That's why we don't need to
explicitly specify a `model` attribute for `BooksByAuthor`.

`BooksByAuthor` is an example of a :ref:`slave table <slave_tables>`. It shows
the books of a given `Author`.  This given `Author` is called the "master" of
these Books.  We also say that a slave table *depends* on its master.

Lino manages this dependency almost automatically.  The application developer
just needs to specify a class attribute :attr:`master_key
<lino.core.tables.AbstractTable.master_key>`.  This attribute, when set, must be
a string containing the name of a `ForeignKey` field of the table's
:attr:`model`.

A table can define attributes like :attr:`filter
<lino.core.tables.AbstractTable.filter>` and :attr:`order_by
<lino.core.tables.AbstractTable.order_by>`, which you know from Django's
`QuerySet API <https://docs.djangoproject.com/en/5.0/ref/models/querysets/>`_.


.. _lino.dev.tables.columns:

The columns of a table
===========================

An important attribute of a table is :attr:`column_names
<lino.core.tables.AbstractTable.column_names>`, which describes the columns to
show in tabular display modes.

.. currentmodule:: lino.core.tables

.. class:: AbstractTable
  :noindex:

  .. attribute:: column_names

    A string that describes the list of columns of this table.

    Default value is ``'*'``, which means to show all columns.

    Lino will automatically create a
    :class:`lino.core.layouts.ColumnsLayout` from this.
    This string must not contain any newline characters because a
    ColumnsLayout's `main` panel descriptor must be horizontal.

    See also :meth:`setup_column` and :meth:`get_column_names`.

  .. attribute:: hidden_columns

    If given, this is specifies the data elements that should be
    hidden by default when rendering this table.  Example::

      hidden_columns = "long_name expected_date"

    **Value** : The default value is an empty set. Application code should
    specify this as a *single string* containing a space-separated list of field
    names.  Lino will automatically resolve this during site startup using
    :func:`lino.core.utils.fields_list`.  The runtime value of this attribute is
    a *set of strings*, each one the name of a data element.

    **Inheritance** : Note that this can be specified either on a
    :class:`Model` or on a :class:`Table`.  Lino will make a union of
    both.

Wildcard columns
================

The asterisk (``'*'``) in a column specifier is a wildcard and means "insert at
this point all columns that have not been named explicitly". It can be combined
with explicitly specified names.  These :term:`wildcard columns <wildcard
column>`

If ``'*'`` is not present in the string, only explicitly named columns will be
available.

For example::

  column_names = "name owner * date"

specifies that `name` and `owner` come first, followed by inserted
columns and finally by `date`.

Virtual fields are not included as wildcard field unless they have
:attr:`lino.core.fields.VirtualField.wildcard_field` set to `True`. This rule is
for performance reasons. Some virtual fields a rather heavy (e.g. the
:attr:`navigation_panel <lino.core.model.Model.navigation_panel>` must query the
whole database to get all primary keys), and even when they are hidden, Lino has
to include :term:`wildcard fields <wildcard field>` in the result because the
end user might have enabled them.

Other table view attributes
===========================

But the table is even more than the description of a grid widget.  It
also has attributes like :attr:`detail_layout
<lino.core.actors.Actor.detail_layout>`, which tells it how to display
the detail of a single record in a form view.

Using tables without a web server
=================================

An important thing with tables is that they are independent of any
front end. You define them once, and you can use them on the
console, in a script, in a testcase, in a web interface or in a GUI
window.

At this point of our tutorial, we won't yet fire up a web browser
(because we want to explain a few more concepts like menus and layouts
before we can do that), but we can already play with our data using
Django's console shell::

  $ python manage.py shell

The first thing you do in a :manage:`shell` session is to import
everything from :mod:`lino.api.shell`:

>>> from lino.api.shell import *

This imports especially a name ``rt`` which points to the
:mod:`lino.api.rt` module.  ``rt`` stands for "run time" and it
exposes Lino's runtime API.  In our first session we are going to use
the :meth:`show <lino.api.rt.show>` method and the :meth:`actors
<lino.core.site.Site.actors>` object.

>>> rt.show(tables.Authors)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
============ =========== =========
 First name   Last name   Country
------------ ----------- ---------
 Douglas      Adams       UK
 Albert       Camus       FR
 Hannes       Huttner     DE
============ =========== =========
<BLANKLINE>

So here is, our ``Authors`` table, in a testable console format!

And here is the ``Books`` table:

>>> rt.show(tables.Books)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
================= ====================================== ===========
 author            Title                                  Published
----------------- -------------------------------------- -----------
 Adams, Douglas    Last chance to see...                  1990
 Adams, Douglas    The Hitchhiker's Guide to the Galaxy   1978
 Huttner, Hannes   Das Blaue vom Himmel                   1975
 Camus, Albert     L'etranger                             1957
================= ====================================== ===========
<BLANKLINE>

These were so-called **master tables**.  We can also show the content
of :ref:`slave tables <slave_tables>` :

>>> adams = tables.Author.objects.get(last_name="Adams")
>>> rt.show(tables.BooksByAuthor, adams)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ======================================
 Published   Title
----------- --------------------------------------
 1978        The Hitchhiker's Guide to the Galaxy
 1990        Last chance to see...
=========== ======================================
<BLANKLINE>


Before going on, please note that the preceding code snippets are
**tested** as part of Lino's test suite.  This means that as a core
developer you can run a command (:cmd:`inv test` in case you are
curious) which will parse the source file of this page, execute every
line that starts with ``>>>`` and verifies that the output is the same
as in this document.  If a single dot changes, the test "fails" and
the developer will find out the reason.

Writing test cases is an important part of software development.  It
might look less funny than developing cool widgets, but actually these
are part of analyzing and describing how your users want their data to
be structured.  Which is the more important part of software
development.



Defining a web interface
========================

The last piece of the user interface is the *menu definition*, located
in the :xfile:`__init__.py` file of this tutorial:

.. literalinclude:: /../../book/lino_book/projects/tables/__init__.py

Every plugin of a Lino application can define its own subclass of
:class:`lino.core.plugin.Plugin`, and Lino instantiates these objects
automatically a startup, even before importing your database models.

Note that a plugin corresponds to what Django calls an application. More about
this in :ref:`dev.plugins`.





Exercises
=========

Explore the application and try to extend it: change things in the
code and see what happens.


You can interactively play around with the little application used in
this tutorial::

  $ go tables
  $ python manage.py runserver

Some screenshots:

.. image:: 1.png
.. image:: 2.png


The :file:`fixtures/demo.py` file contains the data we used to fill our
database:

.. literalinclude:: /../../book/lino_book/projects/tables/fixtures/demo.py



Glossary
========

This page explains the following terms:

.. glossary::

  table

    A Python class that describes how to render a set of data rows.

  data table

    A more specific term for what this document simple calls a :term:`table`.

  tabular display mode

    A :term:`display mode` that uses columns and rows to display the data. Which
    means either :term:`grid mode` or :term:`plain mode`).

  model-based table

    A :term:`table` that get its data from a :term:`database model`.

  virtual table

    A :term:`table` that is not connected to any :term:`database model`.
    Which means that the :term:`application developer` is responsible for
    defining that data.

  wildcard column

    A data element that has been inserted by a ``*`` and which is hidden by
    default. See `Wildcard columns`_.

  wildcard field

    A database field that is candidate to becoming a :term:`wildcard column`.
