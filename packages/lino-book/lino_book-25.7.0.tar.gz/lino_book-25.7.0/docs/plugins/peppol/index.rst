.. doctest docs/plugins/peppol/index.rst
.. _dg.plugins.peppol:

=========================================
``peppol`` : Peppol support (e-Invoicing)
=========================================

.. module:: lino_xl.lib.peppol

The :mod:`lino_xl.lib.peppol` plugin adds functionality for accessing the
:term:`Peppol network`.  It has two **usage scenarios**, which can --but don't
need to-- be combined on a single :term:`Lino site`:

- As a :term:`Peppol hosting provider` your Lino site holds your list of
  :term:`Peppol endpoints <Peppol endpoint>` that you registered for your
  customers.

- As the customer of a :term:`Peppol hosting provider` you are registered as a
  :term:`Peppol endpoint` and can send and receive invoices from your Lino site.

See also the :ref:`User Guide <ug.plugins.peppol>`.


.. toctree::
   :maxdepth: 1

   scenarios
   jargon
   suppliers
   documents
   outbound
   inbound
   credentials
   general
   api_suppliers
   api_documents
   ubl
