.. doctest docs/dev/printing.rst
.. _lino.admin.printing:

===========================
Developer intro to printing
===========================

See also :ref:`ug.topics.printing` in the User Guide.

.. contents::
  :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')
>>> from lino.api.shell import *
>>> from lino.api.doctest import *


.. currentmodule:: lino.modlib.printing


End users see a printable document by invoking the Print button on any database
object whose model inherits from :class:`Printable`.


The print action
================

Here is what happens when a user invokes the :attr:`do_print
<Printable.do_print>` action of a printable object:

- Lino generates ("builds") the :term:`printable document` on the server.
  For cached printables (see :class:`CachedPrintable`), Lino may skip
  this step if that document had been generated earlier.

- Lino **delivers** the document to the user by letting the action respond with
  `open_url`.


Build methods
=============

Lino comes with a series of "build methods".

>>> rt.show(printing.BuildMethods)
============ ============ ======================
 value        name         text
------------ ------------ ----------------------
 appydoc      appydoc      AppyDocBuildMethod
 appyodt      appyodt      AppyOdtBuildMethod
 appypdf      appypdf      AppyPdfBuildMethod
 appyrtf      appyrtf      AppyRtfBuildMethod
 latex        latex        LatexBuildMethod
 pub          pub          PublisherBuildMethod
 rtf          rtf          RtfBuildMethod
 weasy2html   weasy2html   WeasyHtmlBuildMethod
 weasy2pdf    weasy2pdf    WeasyPdfBuildMethod
 xml          xml          XmlBuildMethod
============ ============ ======================
<BLANKLINE>


Template engines
================

A `template engine <http://en.wikipedia.org/wiki/Template_engine_(web)>`_
is responsible for replacing *template commands* by their result.
The template engine determines the syntax for specifying template
commands when designing templates.

- :class:`PisaBuildMethod` and :class:`LatexBuildMethod` use
  `Django's template engine
  <https://docs.djangoproject.com/en/5.0/topics/templates/>`_ whose
  template commands look for example like
  ``{% if instance.has_family %}yes{% else %}no{% endif %}``
  or
  ``My name is {{ instance.name }}.``.

- :class:`RtfBuildMethod` uses :term:`pyratemp` as template engine
  whose template commands looks like ``@!instance.name!@``.
  We cannot use Django's template engine because
  both use curly braces as command delimiters.

  This build method has a flaw: I did not find a way to
  "protect" the template commands in your RTF files from being formatted by Word.


Markup versus WYSIWYG
=====================

There are two fundamentally different categories of templates:
**WYSIWYG** (`.odt`, `.rtf`) or **Markup** (`.html`, `.tex`).

Template collections that use some markup language are usually less
redundant because you can design your collection intelligently by
using template inheritance.

On the other hand, maintaining a collection of markup templates
requires a relatively skilled person because the maintainer must know
two "languages": the template engine's syntax and the markup syntax.

WYSIWYG templates (LibreOffice or Microsoft Word) increase the
probability that an end-user is able to maintain the template
collection because there's only on language to learn (the template
engine's syntax)


Post-processing
===============

Some print methods need post-processing: the result of parsing must be
run through another software in order to turn into a usable format.
Post-processing creates dependencies to other software and has of
course influence on runtime performance.

Utility functions
=================

Some usage examples of the :meth:`lino.core.site.Site.decfmt` method:

>>> from lino.core.site import TestSite as Site
>>> from decimal import Decimal
>>> self = Site()
>>> print(self.decimal_group_separator)
\xa0
>>> print(self.decimal_separator)
,

>>> x = Decimal(1234)
>>> print(self.decfmt(x))
1\xa0234,00

>>> print(self.decfmt(x, sep="."))
1.234,00

>>> self.decimal_group_separator = '.'
>>> print(self.decfmt(x))
1.234,00

>>> self.decimal_group_separator = "oops"
>>> print(self.decfmt(x))
1oops234,00



Weblinks
========

.. glossary::

  Pisa
    https://www.sejda.com/html-to-pdf
    HTML/CSS to PDF converter written in Python.

  odtwriter
    http://www.rexx.com/~dkuhlman/odtwriter.html
    http://www.linuxbeacon.com/doku.php?id=articles:odfwriter

  pyratemp
    http://www.simple-is-better.org/template/pyratemp.html
