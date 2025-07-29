.. doctest docs/plugins/peppol/suppliers.rst
.. _noi.plugins.peppol:

======================================
Managing Peppol end users
======================================

.. currentmodule:: lino_xl.lib.peppol

With this usage scenario of the :mod:`lino_xl.lib.peppol` plugin you can manage
a list of :term:`Peppol end users <Peppol end user>`. To activate this
scenario, set the :data:`with_suppliers` plugin setting to `True`. This scenario
requires the :term:`site operator` to be an :term:`Peppol hosting provider`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

The code snippets in this document are tested only if you have :term:`Ibanity
credentials` installed:

>>> if not dd.plugins.peppol.credentials:
...     pytest.skip('this doctest requires Ibanity credentials')


.. currentmodule:: lino_xl.lib.peppol

Database models
===============

.. class:: Supplier

  Django model used to represent an :term:`Ibanity supplier`

A supplier is the legal person sending and/or receiving an invoice via Peppol.
They are the customers of the :term:`hosting provider`.

The term "supplier" comes from UBL, which has an element named
`AccountingSupplierParty
<https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/>`__ to specify the
"seller" party of an invoice. Internally the Ibanity team uses the term "end
user" instead of "supplier" and might change that at some point on the API, too.
An end user is the legal person using your software.


Data checkers
=============

.. class:: SuppliersListChecker

  Checks whether all suppliers that were registered by this :term:`Peppol
  hosting provider` have a :class:`Supplier` row on this Lino site.

.. class:: SupplierChecker

  Synchronizes this :class:`Supplier` row with the data registered in the
  :term:`Ibanity API`.

Note that :class:`SuppliersListChecker` and :class:`SupplierChecker` are
**manual checkers**. We do not want these checkers to run automatically during
:manage:`checkdata`, only when called manually, because it requires Ibanity
credentials, which are not available e.g. on GitLab.


Onboarding states
=================

.. class:: OnboardingStates

  A choicelist with values for the :attr:`Supplier.onboarding_state` field.


>>> rt.show(peppol.OnboardingStates)
======= ============ ============
 value   name         text
------- ------------ ------------
 10      draft        Draft
 20      created      Created
 30      approved     Approved
 40      rejected     Rejected
 50      onboarded    Onboarded
 60      offboarded   Offboarded
======= ============ ============
<BLANKLINE>

Suppliers
=========

>>> ar = rt.login("robin")
>>> rt.show(peppol.Suppliers)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
====================================== ===================== ================= ================== ==================================
 Supplier ID                            Organization          VAT id            Onboarding state   Last sync
-------------------------------------- --------------------- ----------------- ------------------ ----------------------------------
 997dc48c-b953-4588-81c0-761871e37e42   Bäckerei Ausdemwald   BE 0561.962.669   Onboarded          ...
 bcce2b6f-d636-4390-9d47-4c02969db218   Bäckerei Mießen       BE 0322.862.421   Onboarded          ...
 88fc5add-98cf-4bf1-9f7c-3214c94549b3   Bäckerei Schmitz      BE 0966.980.726   Onboarded          ...
 0aaf855b-49dd-4b65-947f-27a80f13d2d0   Garage Mergelsberg    BE 0506.780.656   Onboarded          ...
                                        Ethias s.a.           BE 0404.484.654   Draft
 76e631c1-05c7-4229-a038-6ca99d8a91f0   Niederau Eupen AG     BE 0419.897.855   Onboarded          ...
 4c78ea55-ee5f-4e98-8675-88fa099a7789   Leffin Electronics    BE 0650.238.114   Onboarded          ...
 257e1470-b192-4eff-ae30-b83a295a907e   Number One            BE 0123.456.749   Onboarded          ...
 5d314e69-e462-4a4d-8694-c34ca7805e0b   Number Two            BE 0234.567.873   Onboarded          ...
 c1b8263e-88ef-4df0-ae37-1ca46ee7ec81   Number Three          BE 0345.678.997   Onboarded          ...
====================================== ===================== ================= ================== ==================================
<BLANKLINE>

The Supplier IDs are given arbitrarily by the Ibanity environment.


..
  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
