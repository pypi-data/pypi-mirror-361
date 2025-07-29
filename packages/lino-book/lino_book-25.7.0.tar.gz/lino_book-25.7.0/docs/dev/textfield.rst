.. doctest docs/dev/textfield.rst
.. _dev.textfield:

===========
Text fields
===========

.. currentmodule:: lino.core.fields


Overview
========

Django defines two types of database fields that contain text and the value of
which is represented in Python as a :class:`str`: :term:`charfields <charfield>`
and :term:`textfields <textfield>`.

.. glossary::

  charfield

    A field that contains a single line of text (no line breaks).

  textfield

    A :term:`charfield` that can contain more than one line of text.


A :term:`charfield` requires a `max_length
<https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.CharField.max_length>`__
while a :term:`textfield` doesn't.

A :term:`textfield` has a flexible height in layouts, while a :term:`charfield` hasn't.

A :term:`charfield` is defined using `Django CharField
<https://docs.djangoproject.com/en/5.0/ref/models/fields/#charfield>`__ while a
:term:`textfield` is a  `Django TextField
<https://docs.djangoproject.com/en/5.0/ref/models/fields/#textfield>`__.

Lino adds a :class:`dd.CharField <CharField>` class, but this is not much used
and might get deprecated.

Two types of textfields
=======================

Lino knows two basic forms of :term:`textfields <textfield>`:

.. glossary::

  plain textfield

    A :term:`textfield` meant to contain "raw" text without any formatting.

  rich textfield

    A :term:`textfield` that can contain HTML formatting like character style,
    links, tables, headers, enumerations, ...

Both types of textfields are specified using the :class:`dd.RichTextField
<RichTextField>` class where :attr:`format` is either either ``'plain'`` or
``'html'``.

The content of a :term:`rich textfield` can be *limited** using
:doc:`/dev/bleach`.

The content of a :term:`rich textfield` can contain :term:`memo commands <memo
command>` (see :doc:`/specs/memo`).


The ``textfield_format`` site setting
=====================================

There is a site attribute :attr:`lino.core.site.Site.textfield_format`, which
defaults to ``'plain'``.

You'll probably better leave the site setting as 'plain', and specify explicitly
the fields you want as html by declaring them::

    foo = fields.RichTextField(..., format='html')

We recommend that you declare your *plain* text fields also using
`fields.RichTextField` and not `models.TextField`::

    foo = fields.RichTextField()

Because that gives subclasses of your application the possibility to
make that specific field html-formatted::

   resolve_field('Bar.foo').set_format('html')


Class reference
===============

.. class:: RichTextField

    A thin wrapper around Django's :class:`TextField
    <django.db.models.fields.TextField>` class, but you can specify two
    additional keyword arguments :attr:`format` and :attr:`bleached`.

    .. attribute:: format

        Contains either ``'plain'`` or ``'html'``.

        Default value is the :attr:`lino.core.site.Site.textfield_format`
        setting.

    .. attribute:: bleached

        See :doc:`/dev/bleach`.


.. class:: PreviewTextField

    A text field that is previewable and editable at the same time.

    I currently works only on the :attr:`lino.modlib.memo.mixins.Previewable.body`
