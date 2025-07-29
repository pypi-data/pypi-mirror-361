.. doctest docs/plugins/peppol/documents.rst
.. _dg.plugins.peppol.documents:

=================================
Peppol document management
=================================

.. currentmodule:: lino_xl.lib.peppol

With this usage scenario of the :mod:`lino_xl.lib.peppol` plugin you can send
and receive your invoices and credit notes via the :term:`Peppol network`.

To activate this scenario, set the :data:`supplier_id` plugin setting to the
supplier id you received from your :term:`Peppol hosting provider` who
registered you as an :term:`Ibanity supplier`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

The tests in this document are skipped unless you also have :term:`Ibanity credentials`
installed. See :ref:`dg.plugins.peppol.credentials` for details.

>>> if dd.plugins.peppol.credentials is None:
...     pytest.skip('this doctest requires Ibanity credentials')

>>> ar = rt.login("robin")
>>> ses = dd.plugins.peppol.get_ibanity_session(ar)
>>> translation.activate('en')


Suppliers management
====================

The `cosi1` and `cosi2` demo sites have no suppliers management, these fictive
site owners have received a `supplier_id` from their Lino provider `noi1e`.  We
simulate this situation by importing :data:`suppliers` from noi1e
:xfile:`data.py`

>>> dd.plugins.peppol.with_suppliers
False

>>> from lino_book.projects.noi1e.settings.data import suppliers
>>> DEMO_SUPPLIER_ID = suppliers[0].supplier_id
>>> assert dd.plugins.peppol.supplier_id == DEMO_SUPPLIER_ID
>>> assert dd.plugins.contacts.site_owner.vat_id == suppliers[0].vat_id
>>> assert dd.plugins.contacts.site_owner.name == suppliers[0].names

The name of the supplier in cosi1 must be the same as it was in noi1e.

>>> dd.plugins.contacts.site_owner.name
'Number One'
>>> suppliers[0].names
'Number One'


>>> ar.show(peppol.OnboardingStates)
Traceback (most recent call last):
...
AttributeError: module 'lino_xl.lib.peppol.models' has no attribute 'OnboardingStates'...


>>> ar.show(peppol.Suppliers)
Traceback (most recent call last):
...
AttributeError: module 'lino_xl.lib.peppol.models' has no attribute 'Suppliers'


Outbound and inbound documents
==============================

When talking to the :term:`Ibanity API` about your invoices and other business
documents, you first need to differentiate between "inbound" and "outbound"
documents. Compare this to an email client where you have an "inbox" and an
"outbox".

Workflow for outbound documents:

- Customer search 🡒 Customer reachability status (Document formats supported
  by this customer)

- Send document 🡒 Receipt

- Get feedback (ask status of an outbound document). The status is either
  successful, in which case we receive a `transmissionID`, or unsuccessful
  in which case we receive more details on the reason why it failed.

Workflow for inbound documents:

- List suppliers 🡒 list of suppliers
- List Peppol inbound documents (1 request per supplier) 🡒
- Get Peppol inbound document (1 request per document) 🡒

Some properties are common to both inbound and outbound documents:

- ``attributes.createdAt`` : when the document entered the Peppol network

- ``relationships.supplier`` : the Peppol end point who posted this document into the Peppol
  network. This has nothing to do with the supplier on the invoice (who is
  called the seller)

- ``id``: unique identifier of this document.

- ``attributes.transmissionId`` : an additional unique identifier within the
  Peppol network. In case of an issue this can be used in communication with the
  sending party.

- the body of the document in :term:`UBL` format

Outbound documents have three additional properties:

- ``status``: one of {created, sending, sent, invalid, send-error}

- ``errors``: one of {invalid-malicious, invalid-format, invalid-xsd,
  invalid-schematron, invalid-size, invalid-type, error-customer-not-registered,
  error-document-type-not-supported, error-customer-access-point-issue}

- ``type``: one of {"peppolInvoice", "peppolOutboundDocument",
  "peppolOutboundInvoice", "peppolOutboundCreditNote"}

When asking for a list of documents, you specify a time range.  For outbound
documents this range means when their **status changed** (fromStatusChanged and
toStatusChanged) while for inbound documents it means their **creation time**

You cannot create (post) an incoming document.


Data tables
===========

.. class:: Inbox

  Shows the Peppol documents that were received and have not yet been processed.

.. class:: Archive

  Shows the Peppol documents that were received and have been processed.

.. class:: Outbox

  Shows the documents that have been sent to the Peppol network.


..
  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
