.. $ doctest docs/specs/weasyprint.rst
.. _specs.weasyprint:

===================================================
``weasyprint``: Printing documents using WeasyPrint
===================================================

The :mod:`lino.modlib.weasyprint` plugin installs two build methods for
generating :term:`printable documents <printable document>` using `weasyprint
<https://weasyprint.org/>`__.

Applications that use this plugin will automatically install the `'weasyprint'`
Python package when the :term:`server administrator` runs :manage:`install`.

The two build methods defined by this plugin both use the same input template,
whose ending must be :xfile:`.weasy.html`.  Both methods then render the input
template through Jinja with the standard context variables (defined by
:meth:`get_printable_context <lino.core.model.Model.get_printable_context>`.
The base build method :class:`WeasyBuildMethod
<lino.modlib.weasyprint.choicelists.WeasyBuildMethod>` then returns this HTML
output "as is", the other method runs weasyprint over the HTML file to convert
it to a :file:`.pdf` file.

Examples in this document use the :mod:`lino_book.projects.tera1` demo
project.

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.shell import *
>>> from lino.api.doctest import *

See also :doc:`printing`.



Build methods
=============

This plugin defines no models, it just adds two build methods to your the global
list of build methods (:class:`lino.modlib.printing.BuildMethods`).


.. currentmodule:: lino.modlib.weasyprint

.. class:: WeasyBuildMethod

    The base class for both build methods.


.. class:: WeasyHtmlBuildMethod

    Renders the input template and returns the unmodified output as
    plain HTML.

.. class:: WeasyPdfBuildMethod

    Like :class:`WeasyBuildMethod`, but the rendered HTML is then
    passed through weasyprint which converts from HTML to PDF.


Templates
=========

.. xfile:: weasyprint/base.weasy.html

  The **base template**. Defines the general HTML and CSS and block definitions
  to be used by every weasyprint template. See the :srcref:`source code
  <lino/modlib/weasyprint/config/weasyprint/base.weasy.html>`.

Actual templates use the base template by starting adding the following line::

  {%- extends "weasyprint/base.weasy.html" -%}

.. _specs.weasyprint.examples:

Examples of weasyprint templates
================================

Here is a list of weasyprint templates that use the base template. You can use
them as examples for your own work.  We also use this list for manual end-user
testing.

- In demo project :mod:`lino_book.projects.cosi1`, go to :menuselection:`Sales
  --> Invoices` and print one of them. (template
  :xfile:`trading/VatProductInvoice/default.weasy.html` in
  :mod:`lino_xl.lib.trading`)

- In demo project :mod:`lino_book.projects.cosi3`,
  same as before but this site has a :data:`page_background_image`.

- In demo project :mod:`lino_book.projects.tera1`, go to
  :menuselection:`Accounting --> VAT Declarations` and print one of them.
  (template :xfile:`bevats/Declaration/default.weasy.html` in
  :mod:`lino_xl.lib.bevats`)

- In demo project :mod:`lino_book.projects.tera1`, go to :menuselection:`Reports
  --> Accounting --> Debtors`, click on one of the partners, then click
  :guilabel:`Print`. (template
  :xfile:`contacts/Partner/payment_reminder.weasy.html` in
  :mod:`lino_xl.lib.accounting`)

- In demo project :mod:`lino_book.projects.tera1`, go to :menuselection:`Contacts --> Partner lists`,
  double-cick on one of them to open the detail window, and then click "Members"
  or "Members (HTML)" in the `Print` field.
  (template :mod:`lino_xl.lib.lists` in
  :xfile:`lists/List/list_members.weasy.html`)

- In demo project :mod:`lino_book.projects.tera1`, go to :menuselection:`Reports --> Accounting -->
  Accounting report`, then click the print button (template
  :xfile:`sheets/Report/default.weasy.html` in :mod:`lino_xl.lib.sheets`).

- In demo project :mod:`lino_book.projects.voga2`, open the detail view of some course and click on one of
  the `Presence sheet` links. Try several date ranges and options.
  (template :xfile:`courses/Course/presence_sheet.weasy.html` in :mod:`lino_xl.lib.courses`)

- :mod:`lino_xl.lib.working` --
  :xfile:`working/ServiceReport/default.weasy.html`

- In demo project :mod:`lino_book.projects.avanti1`, go to some client and click
  the print button. (template :xfile:`avanti/Client/final_report.weasy.html` in
  :mod:`lino_avanti.lib.clients`)


Here is a list of the weasy templates included with the :ref:`xl`:

>>> import lino_xl
>>> from os.path import dirname
>>> from atelier.sheller import Sheller
>>> shell = Sheller(dirname(lino_xl.__file__))
>>> shell("find -name '*.weasy.html' | sort")
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
./lib/accounting/config/contacts/Partner/payment_reminder.weasy.html
./lib/agenda/config/cal/Event/base.weasy.html
./lib/agenda/config/cal/Event/default.weasy.html
./lib/bevats/config/bevats/Declaration/default.weasy.html
./lib/cars/config/trading/VatProductInvoice/cars.weasy.html
./lib/courses/config/courses/Course/description.weasy.html
./lib/courses/config/courses/Course/presence_sheet.weasy.html
./lib/excerpts/config/excerpts/base.weasy.html
./lib/lists/config/lists/List/list_members.weasy.html
./lib/orders/config/orders/Order/base.weasy.html
./lib/orders/config/orders/Order/default.weasy.html
./lib/products/config/products/Product/product_barcode.weasy.html
./lib/sheets/config/sheets/Report/default.weasy.html
./lib/storage/config/storage/DeliveryNote/base.weasy.html
./lib/storage/config/storage/DeliveryNote/default.weasy.html
./lib/subscriptions/config/subscriptions/Subscription/base.weasy.html
./lib/subscriptions/config/subscriptions/Subscription/default.weasy.html
./lib/trading/config/trading/VatProductInvoice/base.weasy.html
./lib/trading/config/trading/VatProductInvoice/default.weasy.html

Note that `excerpts`, `orders` and `trading` have their own
:file:`FOO/base.weasy.html` templates, which inherit from the main base
:xfile:`weasyprint/base.weasy.html`.

For other usage examples see the specs of :ref:`welfare`.

Warnings about Cairo and Pango
==============================

This plugin installs a warnings filter for the `cffi.model` module in
order to get rid of a disturbing warning :message:`There are known
rendering problems with Cairo <= 1.14.0` and :message:`@font-face
support needs Pango >= 1.38` issued by weasyprint.


.. _specs.weasyprint.logo:

How to customize your logo in the header or footer
==================================================

You can add a logo to all your weasyprint documents by adding a local
:xfile:`config` directory with a subdirectory :file:`weasyprint`, and then
one of the following files:

- :file:`page-background.jpg`
- :file:`top-right.jpg`
- :file:`header.jpg`

The suffix may be either :file:`.jpg` or :file:`.png`.

The :file:`top-right.jpg` and :file:`header.jpg` are used only when
:data:`header_height` is not `None`.

.. data:: margin

  Top and bottom page margin in mm. Default value is 10.

.. data:: margin_left

  Left page margin in mm. Default value is 17.

.. data:: margin_right

  Right page margin in mm. Default value is 10.

.. data:: header_height

  Height of header in mm.
  Default value is 20.
  Set to `None` if you want no header.

.. data:: footer_height

  Height of footer in mm.
  Default value is 20.
  Set to `None` if you want no footer.

.. data:: top_right_width

  Width of :data:`top_right_image` in mm. If not given, Lino computes it based
  on :data:`header_height` and the actual height of the image.


.. data:: page_background_image

  Full path to an image to print as background of every page.

  Default value is the first image file found in :xfile:`config` named either
  :file:`page-background.jpg` or :file:`page-background.png`.

.. data:: top_right_image

  Full path to an image to print in the top right corner of every page.

  Default value is the first image file found in :xfile:`config` named either
  :file:`top-right.jpg` or :file:`top-right.png`.

.. data:: header_image

  Full path to an image to print in the top margin of every page.

  Default value is the first image file found in :xfile:`config` named either
  :file:`header.jpg` or :file:`header.png`.



.. xfile:: weasyprint/page-background.jpg

  When a config file of that name exists, it will get printed as the background
  of every page.  The :doc:`cosi3 </projects/cosi3>` demo project shows an
  example.

.. xfile:: weasyprint/header.jpg

.. xfile:: weasyprint/top-right.jpg

  When a config file of that name exists, the logo will get printed in the top
  right area of every page (unless you override the template).
  Additionally, this file causes the page margins of all documents to change:
  margin: 15mm; margin-top: 35mm;

  The :doc:`cosi1 </projects/cosi1>` and :doc:`avanti1 </projects/avanti1>` demo
  projects show examples.


Customizable template blocks
============================

The base template defines the following blocks, which you can override in a local
child template.

- pagesize : either "portrait" or "landscape"

- header : printed on every page. The default implementation checks whether a
  file :xfile:`weasyprint/header.jpg` exists.

- footer : the default implementation prints the address of the
  :attr:`SiteConfig.site_company`, the page number and print time.

- intro

- main

- bottomright
- bottomleft




How it all works
================

What happens when I print an invoice?

When Lino starts up, it finds the :term:`excerpt type` for trading invoices  (more
precisely the :class:`trading.VatProductInvoice
<lino_xl.lib.trading.VatProductInvoice>` model) and therefore installs the print
action on that model. This is why you a have a print button per invoice.

The :term:`excerpt type` tells Lino which :term:`build method` you want to use
for building your printable document. The default build method is ``weasypdf``.

When we know the build method, we can compute the name of the template to use.
This name is a combination
of ``trading/VatProductInvoice`` (the plugin and model name) and
``default.weasy.html`` (the default template filename for weasypdf when
:class:`lino_xl.lib.excerpts.ExcerptType.template` is empty).

Lino now searches for a file named :xfile:`trading/VatProductInvoice/default.weasy.html`.
This file can exist under any :xfile:`config` directory.
If you have a local :xfile:`config` directory, this is searched first.
Otherwise Lino uses a default file from the source code directory.
More about config directories in :doc:`/dev/config_dirs`.

Now look at the default :xfile:`trading/VatProductInvoice/default.weasy.html`
template file.  The first line is::

  {%- extends "weasyprint/base.weasy.html" -%}

Which means that Lino first loads yet another template, called
:xfile:`weasyprint/base.weasy.html`.


How weasyprint templates work
=============================

The weasyprint template uses the CSS @-rules
`@page <https://www.quackit.com/css/at-rules/css_page_at-rule.cfm>`__ and
`@bottom-right
<https://www.quackit.com/css/at-rules/css_bottom-right_at-rule.cfm>`__,
which
define styles to apply to individual pages when printing the document.
That is, they are used to apply styles for *paged media* only,
not for continuous media like a browser window.

List of all ``page-margin`` properties:
https://www.quackit.com/css/at-rules/css_page-margin_properties_list.cfm

Setting the height attribute in HTML is called a "presentational hint"
and it's now recommended not to use them and use CSS instead.
Presentational hints are ignored by WeasyPrint by default,
but you can handle them using the --presentational-hints CLI parameter.
https://github.com/Kozea/WeasyPrint/issues/872

Lino currently doesn't use arbitrary "complex" HTML in headers and footers (as
`documented here
<https://weasyprint.readthedocs.io/en/latest/tips-tricks.html#include-header-and-footer-of-arbitrary-complexity-in-a-pdf>`__).
The standard system with at-rules works well for us.

It contains pseudo-elements for styling the first page as well as the
left and right margins of the page.

It can contain something like this::

  <style type="text/css">
  @page {
      @top-right {
        height: 20mm;
        padding: 0px;
        text-align: right;
        content: url(file://{{logo_file}});
      }
  </style>

More readings:

- https://www.qhmit.com/css/at-rules/
- https://www.quackit.com/css/properties/css_content.cfm
- https://stackoverflow.com/questions/39941967/generate-pdf-with-weasyprint-having-common-header-footer-and-pagination
- https://github.com/Kozea/WeasyPrint/blob/gh-pages/samples/invoice/invoice.css
- https://gist.github.com/pikhovkin/5642563 complex headers

Related work:

- pText (`intro
  <https://stackabuse.com/creating-pdf-invoices-in-python-with-ptext/>`__ ,
  `docs <https://github.com/jorisschellekens/ptext-release/blob/master/EXAMPLES.md>`_,
  `code <https://github.com/jorisschellekens/ptext-release>`__)
