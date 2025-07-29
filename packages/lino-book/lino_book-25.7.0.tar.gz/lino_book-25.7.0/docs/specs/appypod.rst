.. doctest docs/specs/appypod.rst
.. _xl.specs.appypod:

=============================================================
``appypod`` : Generate printable documents from odt templates
=============================================================

.. currentmodule:: lino_xl.lib.appypod

The :mod:`lino_xl.lib.appypod` plugin adds a series of build methods for
generating printable documents using LibreOffice and the :term:`appy.pod`
package.  It also adds certain generic actions for printing tables using these
methods.

See also the user documentation in :ref:`lino.admin.appypod`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *


Dependencies
============

A site that uses the :mod:`lino_xl.lib.appypod` plugin must also have appy installed::

    $ pip install appy

This is done automatically by :manage:`install`.

Rendering a printable document using an appypod build method requires a running
LibreOffice server (see :ref:`admin.oood`).  While this might refrain you from
using them, they has several advantages compared to the built-in methods
:class:`WeasyBuildMethod <lino.modlib.weasyprint.WeasyBuildMethod>` and the (now
deprecated) :class:`PisaBuildMethod <lino.modlib.printing.PisaBuildMethod>`:

- They can be used to produce editable files (`.rtf` or `.odt`) from
  the same `.odt` template.
- Features like automatic hyphenation, sophisticated fonts and layouts
  are beyond the scope of pisa or weasyprint.
- Templates are `.odt` files (not `.html`), meaning that end users
  dare to edit them more easily.

Build methods
=============

.. class:: AppyBuildMethod

    Base class for Build Methods that use `.odt` templates designed
    for :term:`appy.pod`.

.. class:: AppyOdtBuildMethod

    Generates .odt files from .odt templates.

    This method doesn't require OpenOffice nor the
    Python UNO bridge installed
    (except in some cases like updating fields).

.. class:: AppyPdfBuildMethod

    Generates .pdf files from .odt templates.

.. class:: AppyRtfBuildMethod

    Generates .rtf files from .odt templates.

.. class:: AppyDocBuildMethod

    Generates .doc files from .odt templates.


Actions
=======

The :mod:`lino_xl.lib.appypod` plugin adds two actions
:class:`PrintTableAction` and :class:`PortraitPrintTableAction` to
every table in your application.

If :mod:`lino_xl.lib.contacts` (or a child thereof) is installed, it
also adds a :class:`PrintLabelsAction
<lino_xl.lib.appypod.mixins.PrintLabelsAction>`.

.. class:: PrintTableAction

    Show this table as a pdf document.

.. class:: PortraitPrintTableAction

.. class:: PrintLabelsAction

    Add this action to your table, which is expected to execute on a
    model which implements
    :class:`Addressable <lino.utils.addressable.Addressable>`.

    .. method:: get_recipients(self, ar)

        Return an iterator over the recipients for which we want to
        print labels.

        This is here so you can override it. For example::

            class MyLabelsAction(PrintLabelsAction)
                # silently ignore all recipients with empty 'street' field
                def get_recipients(self,ar):
                    for obj in ar:
                        if obj.street:
                            yield obj

        You might want to subclass this action and add a parameters
        panel so that users can explicitly say whether they want
        labels for invalid addresses or not::

            class MyTable(dd.Table):
                parameters = dict(
                    only_valid_recipients=models.BooleanField(
                        _("only valid recipients"),default=False
                    )



Templates
=========

.. xfile:: Table.odt

    Template used to print a table in landscape orientation.

.. xfile:: Table-portrait.odt

    Template used to print a table in portrait orientation.

.. xfile:: appypod/Labels.odt

    Template used to print address labels.




The Appy renderer
=================

.. class:: AppyRenderer

    The extended `appy.pod.renderer` used by Lino.

    A subclass of :class:`appy.pod.renderer.Renderer` (not of
    :class:`lino.core.renderer.Renderer`.

    .. method:: restify_func(self, text)
    .. method:: insert_jinja(self, template)
    .. method:: insert_html(self, html)

        Insert a chunk of HTML (not XHTML) provided as a string or as an
        etree element.

        This is the function that gets called when a template contains a
        ``do text from html(...)`` statement.

    .. method:: insert_story(self, story)
    .. method:: insert_table(self, ar)

        This is the function that gets called when a template contains a
        ``do text from table(...)`` statement.

    .. method:: story2odt(self, story, *args, **kwargs)

        Yield a sequence of ODT chunks (as utf8 encoded strings).

How tables are rendered using appypod
=====================================

We chose a simple Lino table request and then have a look how such a
request is being rendered into a pdf document using appypod.


>>> from lxml import etree
>>> from unipath import Path
>>> import tempfile

Here is a simple Lino table request:

>>> ar = rt.login('robin').spawn(countries.Countries)
>>> ar.show()
============================= ================================ ================================= ==========
 Designation                   Designation (de)                 Designation (fr)                  ISO code
----------------------------- -------------------------------- --------------------------------- ----------
 Bangladesh                    Bangladesh                       Bangladesh                        BD
 Belgium                       Belgien                          Belgique                          BE
 Congo (Democratic Republic)   Kongo (Demokratische Republik)   Congo (République democratique)   CD
 Estonia                       Estland                          Estonie                           EE
 France                        Frankreich                       France                            FR
 Germany                       Deutschland                      Allemagne                         DE
 Maroc                         Marokko                          Maroc                             MA
 Netherlands                   Niederlande                      Pays-Bas                          NL
 Russia                        Russland                         Russie                            RU
 United States                 United States                    United States                     US
============================= ================================ ================================= ==========
<BLANKLINE>



This code is produced by the :meth:`insert_table
<lino_xl.lib.appy_pod.appy_renderer.AppyRenderer.insert_table>` method,
which dynamically creates a style for every column and respects the
widths it gets from the request's :meth:`get_field_info
<lino.core.tablerequest.TableRequest.get_field_info>`, which returns
`col.width or col.preferred_width` for each column.

To get an AppyRenderer for this test case, we must give a template
file and a target file.  As template we will use :xfile:`Table.odt`.
The target file must be in a temporary directory because and every
test run will create a temporary directory next to the target.

>>> from lino_xl.lib.appypod.appy_renderer import AppyRenderer
>>> ctx = {}
>>> template = rt.find_config_file('Table.odt')
>>> target = Path(tempfile.gettempdir()).child("out.odt")
>>> rnd = AppyRenderer(ar, template, ctx, target)

If you open the :xfile:`Table.odt`, you can see that it is mostly
empty, except for headers and footers and a comment which says::

  do text
  from table(ar)

Background information about this syntax in the `appy.pod docs
<http://appyframework.org/podWritingTemplates.html>`__.

This command uses the :func:`table` function to insert a chunk of
ODF XML.

>>> odf = rnd.insert_table(ar)
>>> print(odf)  #doctest: +ELLIPSIS
<table:table ... table:...name="countries.Countries" ...name="countries.Countries">...

Let's parse that long string so that we can see what it contains.

>>> root = etree.fromstring(odf)

The root element is of course our table

>>> root  #doctest: +ELLIPSIS
<Element {urn:oasis:names:tc:opendocument:xmlns:table:1.0}table at ...>

Every ODF table has three children:

>>> children = list(root)
>>> len(children)
3
>>> print('\n'.join(e.tag for e in children))
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-columns
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-header-rows
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-rows

>>> columns = children[0]
>>> header_rows = children[1]
>>> rows = children[2]

The rows

>>> len(rows)
10
>>> len(rows) == ar.get_total_count()
True

>>> cells = list(rows[0])
>>> print('\n'.join(e.tag for e in cells))
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell

The columns

>>> print('\n'.join(e.tag for e in columns))
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-column
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-column
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-column
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-column

>>> print('\n'.join(e.tag for e in header_rows))
{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row

Related projects
================

.. glossary::
  :sorted:

  ODFPy
    A Python library for manipulating OpenDocument documents
    (.odt, .ods, .odp, ...):
    read existing files, modify, create new files from scratch.
    Read more on `PyPI <http://pypi.python.org/pypi/odfpy>`_.
    Project home page https://joinup.ec.europa.eu/software/odfpy

  appy.pod
    A tool for generating pdf and other formats, including .odt
    or .doc) from .odt templates.  See
    http://appyframework.org/pod.html
    http://appyframework.org/podRenderingTemplates.html

  appypod
    As long as :term:`appy.pod` does not support Python 3, we use
    `Stefan Klug's Python 3 port
    <https://libraries.io/github/stefanklug/appypod>`_.


The ``appy_params`` setting
===========================

.. envvar:: pythonWithUnoPath

This setting was needed on sites where Lino ran under Python **2** while
`python-uno` needed Python **3**.  To resolve that conflict, `appy.pod` has this
configuration option which caused it to run its UNO call in a subprocess with
Python 3.

If you have Python 3 installed under :file:`/usr/bin/python3`, then you don't
need to read on.  Otherwise you must set your :attr:`appy_params
<lino.core.site.Site.appy_params>` to point to your `python3` executable, e.g.
by specifying in your :xfile:`settings.py`::

  SITE.appy_params.update(pythonWithUnoPath='/usr/bin/python3')

.. _lino.admin.appypod:
.. _lino.admin.appy_templates:

Using Appy POD templates
========================

When a :term:`printable document` is generated using a subclass of
:class:`AppyBuildMethod <lino_xl.lib.appypod.AppyBuildMethod>`, then you provide
a document as template in `.odt` format, which you can edit using LibreOffice
Writer.

This template document contains special instructions defined by the
`appy.pod <https://appyframework.org/pod.html>`__ library.


.. currentmodule:: lino_xl.lib.appypod.context

The Appy renderer installs additional functions to be used in `do
text|section|table from` statements (described `here
<https://appyframe.work/19>`__).

.. function:: jinja(template_name)

    Render the template named `template_name` using Jinja.
    The template is supposed to produce HTML markup.

    If `template_name` contains no dot, then the default filename extension
    :file:`.body.html` is added.


.. function:: restify(s)

    Render a string `s` which contains reStructuredText markup.

    The string is first passed to
    :func:`lino.utils.restify.restify` to convert it to XHTML,
    then to `appy.pod`'s built-in :func:`xhtml` function.
    Without this, users would have to write each time something like::

        do text
        from xhtml(restify(self.body).encode('utf-8'))

.. function:: html(html)

    Render a string that is in HTML (not XHTML).

.. function:: ehtml(e)

    Render an ElementTree node
    (generated using :mod:`etgen.html`)
    into this document.
    This is done by passing it to :mod:`lino.utils.html2odf`.

.. function:: table(ar, column_names=None)`

    Render an :class:`lino.core.tables.TableRequest` as a
    table. Example::

        do text
        from table(ar.spawn('users.UsersOverview'))
