.. doctest docs/plugins/peppol/general.rst
.. _dg.plugins.peppol.general:

=========================================
Configuration and utilities
=========================================

.. currentmodule:: lino_xl.lib.peppol


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


Plugin settings
===============


The :mod:`lino_xl.lib.peppol` plugin can be configured using the following
settings.

.. data:: with_suppliers

  Whether this site can register other organizations as :term:`Ibanity suppliers
  <Ibanity supplier>`.

.. data:: supplier_id

  The identification code of this :term:`Lino site` as an :term:`Ibanity
  supplier`.

.. data:: onboarding_date

  Do not send any document having :attr:`entry_date
  <lino_xl.lib.accounting.Voucher.entry_date>` before this date.


The following three settings are filled automatically by the plugin at startup:

.. data:: credentials

   The :term:`Ibanity credentials` to use on this Lino site for accessing the
   :term:`Ibanity API`.

   Must be specified in the form ``"{client_id}:{client_secret}"``.

.. data:: cert_file

  Certification file to use for connecting to :term:`Ibanity`.

.. data:: key_file

  Private key file to use for connecting to :term:`Ibanity`.


Model mixins
============

The peppol plugin defines two model mixins that add fields to
:class:`lino_xl.lib.accounting.Journal` and
:class:`lino_xl.lib.contacts.Partner`.

.. class:: PeppolPartner

  .. attribute:: send_peppol

    Whether sales invoices and credit notes to this partner should be sent via
    the :term:`Peppol network`.

    In the demo data this field is checked for some partners (a subset of those
    with a vat_id).

  .. attribute:: peppol_id

    How this partner identifies themselves in the Peppol network. This is a
    string of style `schemaID:value`, where schemaID refers to a :term:`EAS`.

    In the demo data this field is checked for journal SLS.

  .. attribute:: endpoint_id

    A property that returns an :class:`EndpointID` instance

    Belgian participants are registered with the Belgian company number, for which
    identifier scheme 0208 can be used. Optionally, the customer can be registered
    with their :term:`VAT number`, for which identifier scheme 9925 can be used.

.. class:: PeppolJournal

  .. attribute:: is_outbound

    Whether vouchers of this journal should be sent via the :term:`Peppol
    network`.

  .. attribute:: last_sending

    The date of the latest invoice in this journal that has been sent via
    Peppol.

    What if a customer becomes send_peppol after the onboarding date, and had
    already invoices sent before the onboarding date? For example I activate my
    customer as a supplier, they start sending invoices to some of their
    customers. One month later, two customers of my customer onboard and ask to
    receive e-invoices. My customer also has sales invoices to these two customers
    during the first month, these invoices were sent outside of peppol via email.
    Right now Lino would send the invoices of the first month to these two
    customers.

Choicelists
===========

.. class:: OutboundStates

>>> rt.show(peppol.OutboundStates, language="en")
======= ============== ==============
 value   name           text
------- -------------- --------------
 10      created        Created
 20      sending        Sending
 30      sent           Sent
 40      invalid        Invalid
 50      send_error     Send-Error
 51      acknowledged   Acknowledged
 52      accepted       Accepted
 53      rejected       Rejected
======= ============== ==============
<BLANKLINE>

Or in German:

>>> rt.show(peppol.OutboundStates, language="de")
====== ============== ===============
 Wert   name           Text
------ -------------- ---------------
 10     created        Erstellt
 20     sending        Sendung
 30     sent           Versendet
 40     invalid        Ungültig
 50     send_error     Versandfehler
 51     acknowledged   Acknowledged
 52     accepted       Zugesagt
 53     rejected       Abgesagt
====== ============== ===============
<BLANKLINE>



The following choicelist is not needed because we just store the text version in
:attr:`OutboundDocument.error_message`.

>>> rt.show(peppol.OutboundErrors)  #doctest: +SKIP
======= ========================= =========================
 value   name                      text
------- ------------------------- -------------------------
 010     malicious                 Malicious
 020     format                    Invalid format
 030     xsd                       Invalid XML
 040     schematron                Invalid Schematron
 050     identifiers               Invalid identifiers
 060     size                      Invalid size
 070     invalid_type              Invalid type
 080     customer_not_registered   Customer not registered
 090     unsupported               Type not supported
 100     access_point              Access Point issue
 110     unspecified               Unspecified error
======= ========================= =========================
<BLANKLINE>


Utilities
=========

.. class:: EndpointID

  A lightweight Python object to represent a Peppol endpoint identifier.

  It can render the XML of the ``Party / EndpointID`` element of either
  `AccountingSupplierParty
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-AccountingSupplierParty/cac-Party/cbc-EndpointID/>`__
  or `AccountingCustomerParty
  <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/cac-AccountingSupplierParty/cac-Party/cbc-EndpointID/>`__.

  .. attribute:: vat_id
  .. attribute:: national_id
  .. attribute:: country_code
  .. attribute:: scheme

  .. method:: as_xml

    Used in the :xfile:`peppol-ubl.xml` template.


The :term:`Ibanity` integration environment provides test receivers that we can
use to test the sending of invoices for testing (`more
<https://documentation.ibanity.com/einvoicing/1/products#development-resources>`__).

>>> from lino_xl.lib.peppol.utils import DEMO_RECEIVERS
>>> pprint(DEMO_RECEIVERS)
{'0106': '40559537',
 '0190': '08405595370840559537',
 '0208': '0840559537',
 '9925': '0840559537',
 '9930': 'DE654321',
 '9938': 'LU654321',
 '9944': 'NL840559537B01'}

..
  This is why we have the :data:`peppol.simulate_endpoints` plugin setting, which
  is True in cosi1 and noi1e

  >> dd.plugins.peppol.simulate_endpoints
  True

  When this setting is `True`, Lino uses a fake endpoint in the XML file.

>>> obj = contacts.Company.objects.get(name="Number One")
>>> print(obj.endpoint_id)
9925:0123456749
>>> print(obj.endpoint_id.as_xml())
<cbc:EndpointID schemeID="9925">BE0123456749</cbc:EndpointID>


..
  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
