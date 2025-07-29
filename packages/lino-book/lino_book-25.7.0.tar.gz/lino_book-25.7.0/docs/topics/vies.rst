.. doctest docs/topics/vies.rst
.. _dev.topics.vies:

================================
VAT number validation using VIES
================================

.. currentmodule:: lino_xl.lib.vat

The :mod:`lino_xl.lib.vat` plugin can use the `VIES (VAT Information Exchange
System) <https://ec.europa.eu/taxation_customs/vies>`__ service of the European
Union for validating :term:`VAT numbers <VAT number>` stored in the
:attr:`VatSubjectable.vat_id` field.



.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi2.startup import *

The VAT number
==============

Every business partner can have a :term:`VAT identification number` (VATIN).

The following function `validate_vat_id` is used in this document to demonstrate
the capabilities and roles of Lino in managing a VAT number.

>>> from django.core.exceptions import ValidationError
>>> def validate_vat_id(partner):
...     try:
...         partner.full_clean()
...         print(partner.vat_id)
...     except ValidationError as e:
...         print("ValidationError:\n" + e.message)

A partner who has a :attr:`vat_id` (:term:`VAT number`) field, by default
implementation, also has a :attr:`vid_manager` property, which is essentially a
pointer to an instance of a :class:`VatNumberManager
<lino_xl.lib.vat.models.VatNumberManager>` that validates an inserted :term:`VAT
number` and does some other things that we will see below.

Below example displays an error message for an invalid :term:`VAT number`.

>>> Country = countries.Country
>>> Company = contacts.Company
>>> belgium = Country.objects.get(isocode="BE")
>>> obj = Company(name="foo", country=belgium)
>>> obj.vat_id = "5468523548"
>>> validate_vat_id(obj)
ValidationError:
VAT identification number is greater than 19999999

Modulo 97 check failed for VAT identification number in BE

The validation error message is a little more self explanatory when the inserted
:term:`VAT number` does not match any format explained `here
<https://en.wikipedia.org/wiki/VAT_identification_number>`_. An example:

>>> obj = Company(name="bar Ltd.", vat_id="NL56465")
>>> validate_vat_id(obj)
ValidationError:
You have entered an invalid VAT identification number.
The general format follows: NLxxxxxxxxxBxx
Where each 'x' is a digit.

When the :attr:`country` field is empty, the ISO 3166-1-alpha-2 country code
must be given at the beginning of the VAT identification number, otherwise Lino
will treat the VAT identification number as a dummy and will not do any
validation check. The following example shows two possibilities where in first
case there's no :attr:`country` associated with the partner but has a valid
:attr:`vat_id` format and in later case there's no known country associated with
the partner not in :attr:`country` field neither in the :attr:`vat_id`. And
differences are distinguishable from the returned :term:`VAT number`, where the
valid :term:`VAT number` returns are formatted with dots (.) and a whitespace.

>>> obj = Company(name="foo Ltd.", vat_id="EE100041561")
>>> validate_vat_id(obj)
EE 100.041.561

>>> obj = Company(name="foo Inc.", vat_id="100041561")
>>> validate_vat_id(obj)
100041561

If the partner's :attr:`country` is different from the country code given in the
:term:`VAT number`, Lino will also raise a ValidationError.

>>> estonia = Country(isocode="EE")
>>> obj = Company(name="foo Inc.", country=estonia, vat_id="BE 100041561")
>>> validate_vat_id(obj)
ValidationError:
Country code (EE) does not match with BE.

By default a :class:`VatNumberManager
<lino_xl.lib.vat.VatNumberManager>` instance includes the validation for
the countries with ISO code shown in the following code output.

>>> from lino_xl.lib.vat.choicelists import VAT_ORIGINS
>>> list(VAT_ORIGINS.keys())
['BE', 'AT', 'NL', 'HR', 'DK', 'EE', 'FI', 'FR', 'DE', 'EL', 'HU', 'IT', 'LV', 'LT', 'LU']

If the given country code is not included in the above example, Lino will accept
any reasonable format of the :term:`VAT number` as valid.

>>> obj = Company(name="HyD Inc.", vat_id="BD 545454656484b6563")
>>> validate_vat_id(obj)
BD 54.545.465.648.4B6.563

Adding a VatOrigin:

>>> from lino_xl.lib.vat.choicelists import VAT_ORIGINS, VatOrigin
>>> vo = VatOrigin('CY', 8, dummy_suffix="L",
...     pattern="^(?P<country_code>CY) (?P<number>[0-9]{8})(?P<suffix>L)$")
>>> VAT_ORIGINS[vo.country_code] = vo

>>> validate_vat_id(Company(name="HyD Inc.", vat_id="CY 1234567890"))
ValidationError:
You have entered an invalid VAT identification number.
The general format follows: CYxxxxxxxxL
Where each 'x' is a digit.

>>> validate_vat_id(Company(name="HyD Inc.", vat_id="CY12345678L"))
CY 12.345.678L

When :setting:`vat.use_online_check` is `True`, the :manage:`checkdata` command
will do online verification of every :term:`VAT id`.

.. class:: VatIdChecker

  Validate VAT id from online registry.

The demo database contains some fictive VAT ids that are syntactically correct
but simply do not exist in reality.

Until 2022-12-28, Lino detected this as a :term:`data problem` because
:setting:`vat.use_online_check` was `True` in :mod:`lino_book.projects.cosi2`.
That's why we had a series of corresponding :term:`data problems <data
problem>`. The following test is now skipped because
:setting:`vat.use_online_check` caused the test suite to break when the VIES
server was unavailable during :cmd:`inv prep`.

>>> chk = checkdata.Checkers.get_by_value('vat.VatIdChecker')
>>> rt.show(checkdata.MessagesByChecker, chk)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
+-------------------------+---------------------------------+------------------------------------------------------+
| Utilisateur responsable | Database object                 | Texte du message                                     |
+=========================+=================================+======================================================+
| Robin Rood              | *Bäckerei Ausdemwald*           | Invalid VAT identification number BE 7088.996.857:   |
|                         |                                 | Not registered in BE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Bäckerei Mießen*               | Invalid VAT identification number BE 4685.739.309:   |
|                         |                                 | Not registered in BE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Bäckerei Schmitz*              | Invalid VAT identification number BE 4181.505.692:   |
|                         |                                 | Not registered in BE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Garage Mergelsberg*            | Invalid VAT identification number BE 9045.438.159:   |
|                         |                                 | Not registered in BE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Donderweer BV*                 | Invalid VAT identification number NL 220.876.686B01: |
|                         |                                 | Not registered in NL.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Van Achter NV*                 | Invalid VAT identification number NL 451.948.587B01: |
|                         |                                 | Not registered in NL.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Hans Flott & Co*               | Invalid VAT identification number DE 143.956.862:    |
|                         |                                 | Not registered in DE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Bernd Brechts Bücherladen*     | Invalid VAT identification number DE 135.079.295:    |
|                         |                                 | Not registered in DE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Reinhards Baumschule*          | Invalid VAT identification number DE 138.433.397:    |
|                         |                                 | Not registered in DE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Moulin Rouge*                  | Invalid VAT identification number FR 86.915.334.564: |
|                         |                                 | Not registered in FR.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Auto École Verte*              | Invalid VAT identification number FR 66.435.589.280: |
|                         |                                 | Not registered in FR.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Maksu- ja Tolliamet*           | Invalid VAT identification number EE 848.217.541:    |
|                         |                                 | Not registered in EE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Electrabel Customer Solutions* | Invalid VAT identification number BE 4018.258.949:   |
|                         |                                 | Not registered in BE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
| Robin Rood              | *Leffin Electronics*            | Invalid VAT identification number BE 0650.238.114:   |
|                         |                                 | Not registered in BE.                                |
+-------------------------+---------------------------------+------------------------------------------------------+
<BLANKLINE>
