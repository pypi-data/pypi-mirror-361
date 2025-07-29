=============
Peppol jargon
=============

Here are some Peppol-related terms and abbreviations and what they mean.

.. glossary::

  PEPPOL

    (Pan-European Public Procurement Online) An international standard for
    exchanging invoices and other business documents in machine-readable
    formats.

    Through Peppol, participant organisations can deliver procurement documents
    to each other including electronic invoices in machine readable formats,
    avoiding the labour of data entry. -- `Wikipedia
    <https://en.wikipedia.org/wiki/PEPPOL>`_

  Peppol document

    A business document that can be exchanged via the :term:`Peppol network`.
    Right now this means an *invoice* or *credit note*, either *sales* or
    *purchase*.

  Peppol network

    The network of organizations who use the :term:`PEPPOL` standard for
    doing their business communication.

  Peppol access point

    An organization that provides to their customers a connection to the
    :term:`Peppol network`.

  Peppol endpoint

    A legal person who receives and sends invoices using the :term:`Peppol
    network`.

    An **endpoint** uses one and only one **access point** in order to register
    to the **network**.

  Peppol end user

    An organization that receives and sends their invoices and credit notes via
    a software that uses the :term:`Ibanity API` to access the :term:`Peppol
    network`.

    You become an :term:`Peppol end user <Peppol end user>` when  an
    :term:`Peppol hosting provider` register you.

  Peppol hosting provider

    An organization who can register their customers as :term:`Peppol endpoints
    <Peppol endpoint>`.

    If you want to act as a :term:`Peppol hosting provider` with Lino, you need
    a contract with :term:`Ibanity` as your :term:`Peppol access point`
    provider. You can then host one or multiple :term:`Lino sites <Lino site>`
    that share the same :term:`credentials <Ibanity credentials>` for accessing
    the :term:`Ibanity API`.

  Ibanity

    A :term:`Peppol access point` provider for software developers who access
    the Peppol network via an API.

    See https://ibanity.com/company

    Ibanity is a solution of `Isabel Group
    <https://www.isabelgroup.eu/en/isabel-the-company>`__ in Brussels.

  Ibanity supplier

    Jargon synonym for :term:`Peppol end user` used by the :term:`Ibanity API`
    for historical reasons.

  Ibanity API

    The public Application Programmers Interface provided by :term:`Ibanity` to
    their customers.

    Also known under its older name `Flowin e-invoicing Services
    <https://documentation.ibanity.com/einvoicing/1/products>`__.

  Ibanity credentials

    A set of files with security keys to identify an :term:`Peppol hosting
    provider` when accessing the :term:`Ibanity API`.

  Ibanity developer portal

    The web interface where an :term:`Peppol hosting provider` gets their
    :term:`credentials <Ibanity credentials>`.

    See https://documentation.ibanity.com/go-live

  UBL

    Universal Business Language

    `UBL Invoice Syntax reference <https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/tree>`__

  BIS

    Business Interoperability Specifications

    See https://docs.peppol.eu/poacc/billing/3.0/bis/

  SML

    Service Metadata Locator

    A service needed for looking up a business partner using :attr:`EAS`.

    https://docs.peppol.eu/edelivery/sml/PEPPOL-EDN-Service-Metadata-Locator-1.2.0-2021-05-13.pdf

    The :mod:`commondata.peppolcodes` module has a dict :data:`COUNTRY2SCHEME`.

  SMP

    Service Metadata Publisher

    A service needed for looking up a business partner using :attr:`EAS`.


  AS4

    The only transport profile still in use.

    "The AS4 technical specification [AS4] defines a secure and reliable
    messaging protocol. It can be used for message exchange in
    Business-to-Business (B2B), Administration-to-Administration (A2A),
    Administration-to-Business (A2B) and Business-to-Administration (B2A)
    contexts. AS4 messages can carry any number of payloads. Payloads may be
    structured or unstructured documents or data." (`ec.europa.eu
    <https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/eDelivery+AS4+-+2.0>`__)

  Hermes

    A platform provided by the Belgian government where SMEs can sign in and
    communicate with the Peppol network. They can manually enter outbound
    documents (sales invoices and credit notes) to be sent to their customers,
    and they can view their inbound documents.

    - https://hermes-belgium.be
    - https://bosa.belgium.be/fr/applications/hermes
