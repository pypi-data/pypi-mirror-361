============
Lino and XML
============

.. contents::
  :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

Payment orders
==============

- :xfile:`finan/PaymentOrder/pain_001.xml`
- :meth:`lino_xl.lib.finan.PaymentOrder.write_xml`


See :ref:`dt.apps.tera.finan.xml`.

Intracom statements
===================

- :xfile:`bevat/Declaration/intracom_statement.xml`
- :meth:`lino_xl.lib.bevat.Declaration.write_intracom_statement`

Peppol documents
=========================

Peppol documents means invoices and credit notes, both sales and purchases.

While `Payment orders`_ and `Intracom statements`_ still have a button that opens the
generated XML file in a new browser window,
this is actually just a temporary solution.
Actually the end user shouldn't even see these files.

So unlike payment orders and Intracom statements, `Peppol documents`_ use the new
:class:`lino.modlib.jinja.XMLMaker` model mixin.

.. currentmodule:: lino.modlib.jinja

>>> for m in rt.models_by_base(jinja.XMLMaker):
...     if m.xml_file_template:
...         print(full_model_name(m), m.xml_file_template, m.xml_validator_file)
... #doctest: +ELLIPSIS
trading.VatProductInvoice vat/peppol-ubl.xml .../lino_xl/lib/vat/XSD/PEPPOL-EN16931-UBL.sch
vat.VatAccountInvoice vat/peppol-ubl.xml .../lino_xl/lib/vat/XSD/PEPPOL-EN16931-UBL.sch

- :xfile:`vat/peppol-ubl.xml`

The following starts as in :ref:`dg.plugins.peppol.outbound` to find our latest
sales invoice and call :meth:`XmlMaker.make_xml_file` on it, but then we focus
on validation.

>>> ar = rt.login("robin")
>>> qs = trading.VatProductInvoice.objects.filter(journal__ref="SLS")
>>> obj = qs.order_by("accounting_period__year", "number").last()
>>> obj
VatProductInvoice #318 ('SLS 15/2025')

:meth:`XmlMaker.make_xml_file` renders the XML file and returns a
:class:`MediaFile` descriptor for it:

>>> with ar.print_logger("DEBUG"):
...     xmlfile = obj.make_xml_file(ar)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
weasy2pdf render ['trading/VatProductInvoice/default.weasy.html', 'excerpts/default.weasy.html']
-> .../media/cache/weasy2pdf/SLS-2025-15.pdf ('de', {})
SLS-2025-15.pdf has been built.
Make .../cosi1/media/xml/2025/SLS-2025-15.xml from SLS 15/2025 ...

>>> xmlfile.path  #doctest: +ELLIPSIS
PosixPath('.../cosi1/media/xml/2025/SLS-2025-15.xml')

>>> xmlfile.url
'/media/xml/2025/SLS-2025-15.xml'

We can see that the :meth:`jinja.XmlMaker.xml_validator_file` points to the file
:xfile:`PEPPOL-EN16931-UBL.sch`, which is an unmodified copy from
https://docs.peppol.eu/poacc/billing/3.0/

Despite the logger message, :meth:`jinja.XmlMaker.make_xml_file` currently does
nothing when the validator file ends with ".sch".

This is because we didn't yet find a way to run Schematron validation under
Python.  See :doc:`schematron` for more about this.

>>> dbhash.check_virgin()  #doctest: +ELLIPSIS
Database ...isn't virgin:
- excerpts.Excerpt: 1 rows added
Tidy up 1 rows from database: [(<class 'lino_xl.lib.excerpts.models.Excerpt'>, {...})].
Database has been restored.
