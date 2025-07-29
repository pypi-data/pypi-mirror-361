.. doctest docs/topics/schematron.rst

=====================
Schematron validation
=====================

Lino can generate the XML of a :term:`Peppol document` but currrently is not
able to validate it. Here is why.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


.. currentmodule:: lino.modlib.jinja

Let's get our latest sales invoice and call :meth:`XMLMaker.make_xml_file` on it
(The following snippet is from :ref:`dg.plugins.peppol.outbound`, but here we
will focus on validation).

>>> ar = rt.login('robin')
>>> qs = trading.VatProductInvoice.objects.filter(journal__ref="SLS")
>>> obj = qs.order_by("accounting_period__year", "number").last()
>>> obj
VatProductInvoice #318 ('SLS 15/2025')

We have an invoice and now we can call its :meth:`XMLMaker.make_xml_file` method
to render its XML file:

>>> with ar.print_logger("DEBUG"):
...     xmlfile = obj.make_xml_file(ar)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
weasy2pdf render ['trading/VatProductInvoice/default.weasy.html',
'excerpts/default.weasy.html'] -> ...media/cache/weasy2pdf/SLS-2025-15.pdf ('de', {})
SLS-2025-15.pdf has been built.
Make .../cosi1/media/xml/2025/SLS-2025-15.xml from SLS 15/2025 ...

We tidy up because this has created a database excerpt, which might mess up
other doctests:

>>> dbhash.check_virgin()  #doctest: +ELLIPSIS
Database ...isn't virgin:
- excerpts.Excerpt: 1 rows added
Tidy up 1 rows from database: [(<class 'lino_xl.lib.excerpts.models.Excerpt'>, {...})].
Database has been restored.


The :meth:`jinja.XmlMaker.xml_validator_file` points to the file
:xfile:`PEPPOL-EN16931-UBL.sch`, which is an unmodified copy from
https://docs.peppol.eu/poacc/billing/3.0/

>>> obj.xml_validator_file  #doctest: +ELLIPSIS
PosixPath('.../lino_xl/lib/vat/XSD/PEPPOL-EN16931-UBL.sch')

Right now the :meth:`jinja.XmlMaker.make_xml_file` method does nothing when the
validator file ends with ".sch". Because we didn't yet find a way to run
Schematron validation under Python. If you look at the code, you can see that we
tried :mod:`lxml` and `saxon
<https://www.saxonica.com/documentation12/index.html#!using-xsl/commandline>`_.

The third and most promising method is tested in the following snippet. It is
Robbert Harms' `pyschematron <https://github.com/robbert-harms/pyschematron>`__
package.

The tests in this document are skipped unless you have :mod:`pyschematron`
installed.


>>> from importlib.util import find_spec
>>> if not find_spec('pyschematron'):
...     pytest.skip('The rest of this doctest requires pyschematron')


>>> from pyschematron import validate_document
>>> from lxml import etree
>>> result = validate_document(xmlfile, obj.xml_validator_file)
>>> result.is_valid()
True
>>> print(etree.tostring(result.get_svrl(), pretty_print=True).decode(), end='')
... #doctest: +ELLIPSIS
<svrl:schematron-output xmlns:svrl="http://purl.oclc.org/dsdl/svrl" xmlns:sch="http://purl.oclc.org/dsdl/schematron" xmlns:xs="http://www.w3.org/2001/XMLSchema" schemaVersion="iso">
  <svrl:metadata xmlns:dct="http://purl.org/dc/terms/" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:pysch="https://github.com/robbert-harms/pyschematron">
    <dct:creator>
      <dct:agent>
        <skos:prefLabel>PySchematron 1.1.6</skos:prefLabel>
      </dct:agent>
    </dct:creator>
    <dct:created>...</dct:created>
    <dct:source>
      <rdf:Description>
        <dct:creator>
          <dct:Agent>
            <skos:prefLabel>PySchematron 1.1.6</skos:prefLabel>
          </dct:Agent>
        </dct:creator>
        <dct:created>...</dct:created>
      </rdf:Description>
    </dct:source>
  </svrl:metadata>
</svrl:schematron-output>

We join Robbert when he writes in his README file: "In the future we hope to
expand this library with an XSLT transformation based processing. Unfortunately
XSLT transformations require an XSLT processor, which is currently not available
in Python for XSLT >= 2.0."

There are other people who would like to validate XML using Schematron in Python
without needing a Java machine.

- https://stackoverflow.com/questions/78147292/how-to-validate-xml-using-sch-schematron-and-xsd-in-python
