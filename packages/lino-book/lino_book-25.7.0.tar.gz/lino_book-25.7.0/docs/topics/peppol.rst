.. _dg.topics.peppol:

====================================
Peppol support (e-Invoicing) in Lino
====================================

Lino supports receiving and sending digital invoices via the :term:`Peppol
network` as `required by companies in Belgium from January 2026
<https://finances.belgium.be/fr/entreprises/tva/e-facturation/utilisation-obligatoire-factures-electroniques-structurees-a-partir-de-2026#:~>`__.

See:

- :ref:`User Guide <ug.plugins.peppol>`.
- :doc:`Developer reference </plugins/peppol/index>`.

..
  As a Lino :term:`site operator` you need a contract with a :term:`hosting
  provider` who has a contract with :term:`Ibanity`. Your :term:`hosting provider`
  will register you as an :term:`Ibanity` end user and :term:`Ibanity` will act as
  your Peppol access point. We are considering other access point providers as
  well, for example `soluz.io <https://www.soluz.io/general-9>`__.


.. contents::
   :depth: 1
   :local:


.. What's implemented

.. Choosing your Access Point provider

..
  Every Lino :term:`site operator` who wants Peppol access must make a contract
  with some AP provider to get credentials for accessing their API.

..
  We are considering other implementation as well, for example `Tickstart
  <https://www.tickstar.com/>`_. There are many `certified AP providers
  <https://peppol.org/members/peppol-certified-service-providers/>`__, but some
  of them cannot help because they provide access only via their own accounting
  software.


..
  Lino can generate electronic sales invoices compliant with the `European
  standard on eInvoicing
  <https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/eInvoicing>`__.

  To create the XML of an electronic sales invoice, simply print the invoice. This
  will generate an :term:`XML file` that follows the EN 16931-1 standard
  (:term:`Peppol` format). The printable PDF file contains a link to the generated
  :term:`XML file`.

  Note that invoices to private persons don't generate any :term:`XML file`
  because :term:`Peppol` is currently meant for B2B exchanges.

  Try our demo

  If you want to see it with your own eyes:

  - Go to https://cosi1e.lino-framework.org and sign in as ``robin``

  - Click on the link "730 Sales invoices (SLS)" in the main page

  - Select an invoice having a company (not a private person) as partner. For
    example invoice SLS 26/2024.

  - Click on the :guilabel:`Print` button in the toolbar. If needed, tell your
    browser to accept pop-up windows from this site.

  - When the pdf opens, click on `e-invoice: /media/xml/SLS/1787.xml
    <https://cosi1e.lino-framework.org/media/xml/SLS/1815.xml>`__ to see the XML
    file.


  There is more to do

  - Transmission of the XML file to an access point is not yet implemented.

  - Import Peppol invoice files.

  - The ecosio validator still reports issues.

.. Here is some :term:`UBL` jargon and how it maps to general Peppol jargon.


Sources of information
======================

ec.europa.eu (European Commission):

- `Transmitting electronic invoices <https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Transmitting+electronic+invoices>`__
- `eDelivery AS4 specification v1.15 <https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/eDelivery+AS4+-+1.15>`__
- `Code lists <https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Code+lists>`__

peppol.eu (Copyright OpenPeppol AISBL):

- `OpenPeppol eDEC Specifications <https://docs.peppol.eu/edelivery/>`__
  lists the specifications of the Peppol eDelivery network.

peppol.org  (Copyright OpenPeppol AISBL):

- https://peppol.org/documentation/technical-documentation/edelivery-documentation/

other:

- https://github.com/OpenPEPPOL/peppol-bis-invoice-3/blob/master/rules/examples/base-example.xml

- `Free PEPPOL and XML document validator <https://ecosio.com/en/peppol-and-xml-document-validator/>`__

- 2020-06-01 `The European Commission updates the Electronic Address Scheme (EAS) code lists
  <https://lmtgroup.eu/the-european-commission-updates-the-electronic-address-scheme-eas-code-lists/>`__

- https://bosa.belgium.be/fr/applications/hermes

Luc's blog entries
==================

- https://luc.lino-framework.org/blog/2024/0624.html
- https://luc.lino-framework.org/blog/2024/0704.html
- https://luc.lino-framework.org/blog/2024/1219.html (ff.)
- https://luc.lino-framework.org/blog/2025/0113.html (ff.)
- etc.
