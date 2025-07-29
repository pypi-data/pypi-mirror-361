.. doctest docs/plugins/periods.rst
.. _dg.plugins.periods:

==================================
``periods``: Stored periods
==================================

The plugin defines two models: :class:`StoredYear` and  :class:`StoredPeriod`.

This document assumes that you have read the :ref:`end-user documentation
<ug.plugins.periods>` for this plugin.

.. module:: lino.modlib.periods

Table of contents:

.. contents::
   :depth: 1
   :local:

Examples in this document use the :mod:`lino_book.projects.cosi1` demo project.

>>> from lino_book.projects.cosi1.startup import *

>>> ses = rt.login("robin")
>>> translation.activate('en')


Fiscal years
============

If :mod:`lino_xl.lib.sheets` is installed, the detail window of a :term:`fiscal
year` object shows the financial reports (balance sheet and income statement)
for this year.

The :fixture:`std` fixture of the :mod:`lino.modlib.periods` plugins fills
:class:`StoredYear` with 5 years starting from :setting:`periods.start_year`.


>>> settings.SITE.the_demo_date
datetime.date(2025, 3, 12)

>>> dd.plugins.periods.start_year
2023

>>> dd.today()
datetime.date(2025, 3, 12)

>>> dd.today().year + 5
2030

>>> rt.show(periods.StoredYears)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ============ ============ ========
 Reference   Start date   End date     State
----------- ------------ ------------ --------
 2023        01/01/2023   31/12/2023   Closed
 2024        01/01/2024   31/12/2024   Open
 2025        01/01/2025   31/12/2025   Open
 2026        01/01/2026   31/12/2026   Open
 2027        01/01/2027   31/12/2027   Open
 2028        01/01/2028   31/12/2028   Open
 2029        01/01/2029   31/12/2029   Open
 2030        01/01/2030   31/12/2030   Open
=========== ============ ============ ========
<BLANKLINE>

The :meth:`lino.mixins.ref.Referrable.get_next_row` method returns the next
fiscal year if it is defined (otherwise `None`):

>>> for obj in periods.StoredYear.objects.all():
...     print(f"{obj} --> {obj.get_next_row()}")
2023 --> 2024
2024 --> 2025
2025 --> 2026
2026 --> 2027
2027 --> 2028
2028 --> 2029
2029 --> 2030
2030 --> None



Accounting periods
==================

For each period it is possible to specify the dates during which it is allowed
to register vouchers into this period, and also its "state": whether it is
"closed" or not.

Each ledger movement happens in a given :term:`accounting period`.
An accounting period usually corresponds to a month of the calendar.

Accounting periods are automatically created the first time they are needed by
some operation.

>>> rt.show(periods.StoredPeriods)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ============ ============ ============= ======== ========
 Reference   Start date   End date     Fiscal year   State    Remark
----------- ------------ ------------ ------------- -------- --------
 2023-01     01/01/2023   31/01/2023   2023          Closed
 2023-02     01/02/2023   28/02/2023   2023          Closed
 2023-03     01/03/2023   31/03/2023   2023          Closed
 2023-04     01/04/2023   30/04/2023   2023          Closed
 2023-05     01/05/2023   31/05/2023   2023          Closed
 2023-06     01/06/2023   30/06/2023   2023          Closed
 2023-07     01/07/2023   31/07/2023   2023          Closed
 2023-08     01/08/2023   31/08/2023   2023          Closed
 2023-09     01/09/2023   30/09/2023   2023          Closed
 2023-10     01/10/2023   31/10/2023   2023          Closed
 2023-11     01/11/2023   30/11/2023   2023          Closed
 2023-12     01/12/2023   31/12/2023   2023          Closed
 2024-01     01/01/2024   31/01/2024   2024          Open
 2024-02     01/02/2024   29/02/2024   2024          Open
 2024-03     01/03/2024   31/03/2024   2024          Open
 2024-04     01/04/2024   30/04/2024   2024          Open
 2024-05     01/05/2024   31/05/2024   2024          Open
 2024-06     01/06/2024   30/06/2024   2024          Open
 2024-07     01/07/2024   31/07/2024   2024          Open
 2024-08     01/08/2024   31/08/2024   2024          Open
 2024-09     01/09/2024   30/09/2024   2024          Open
 2024-10     01/10/2024   31/10/2024   2024          Open
 2024-11     01/11/2024   30/11/2024   2024          Open
 2024-12     01/12/2024   31/12/2024   2024          Open
 2025-01     01/01/2025   31/01/2025   2025          Open
 2025-02     01/02/2025   28/02/2025   2025          Open
 2025-03     01/03/2025   31/03/2025   2025          Open
 2025-12     01/12/2025   31/12/2025   2025          Open
=========== ============ ============ ============= ======== ========
<BLANKLINE>

The *reference* of a new accounting period is computed by applying the
voucher's entry date to the template defined in the :attr:`date_to_period_tpl
<lino_xl.lib.periods.StoredPeriod.get_for_date>` attribute of the accounting
plugin.  The default implementation leads to the following references:

>>> from lino.modlib.periods.models import date2ref

>>> date2ref(i2d(19940202))
'1994-02'
>>> date2ref(i2d(20150228))
'2015-02'
>>> date2ref(i2d(20150401))
'2015-04'

Special accounting periods
==========================

You may manually create additional accounting periods. For example

- `2025-00` might stand for a fictive "opening" period before January
  2025 and after December 2024.

- `2025-13` might stand for January 2026 in a company that is
  changing their fiscal year from "January-December" to "July-June".

- in certain public
  administrations "January 2024" can be considered as the "Thirteenth month of
  2023" for operations that are bound to the fiscal year 2023.
  We call this **overlapping periods**.


.. _dg.plugins.periods.period_filter:

Filtering the list of stored periods
====================================

The parameter panel of the :class:`StoredPeriods` table has two fields,
:attr:`start_date` and :attr:`end_date`.

>>> ses = rt.login("robin")
>>> pv = dict(start_date=i2d(20240212))
>>> ses.show(periods.StoredPeriods, param_values=pv)
... #doctest: +REPORT_UDIFF +ELLIPSIS
=========== ============ ============ ============= ======= ========
 Reference   Start date   End date     Fiscal year   State   Remark
----------- ------------ ------------ ------------- ------- --------
 2024-02     01/02/2024   29/02/2024   2024          Open
=========== ============ ============ ============= ======= ========
<BLANKLINE>

>>> pv = dict(start_date=i2d(20240212), end_date=i2d(20240312))
>>> ses.show(periods.StoredPeriods, param_values=pv)
... #doctest: +REPORT_UDIFF +ELLIPSIS
=========== ============ ============ ============= ======= ========
 Reference   Start date   End date     Fiscal year   State   Remark
----------- ------------ ------------ ------------- ------- --------
 2024-02     01/02/2024   29/02/2024   2024          Open
 2024-03     01/03/2024   31/03/2024   2024          Open
=========== ============ ============ ============= ======= ========
<BLANKLINE>


>>> dd.today()
datetime.date(2025, 3, 12)
>>> pv = dict(start_date=i2d(20241118), end_date=i2d(20260312))
>>> ses.show(periods.StoredPeriods, param_values=pv, display_mode="summary")
... #doctest: +REPORT_UDIFF +ELLIPSIS
`2024-11 <…>`__, `2024-12 <…>`__, `2025-01 <…>`__, `2025-02 <…>`__, `2025-03 <…>`__, `2025-12 <…>`__


Test examples
=============

>>> TEST_DATES = list(map(i2d, [
...    19850203, 19990901, 20000101, 20150427, 20240324,
...    20590601, 29970123]))


>>> Y, P = periods.StoredYear, periods.StoredPeriod
>>> def run_test():
...     headers = ["Date", "year", "period", "ref", "start date", "end date"]
...     rows = []
...     for d in TEST_DATES:
...         sd, ed = P.get_range_for_date(d)
...         rows.append([str(d), Y.get_ref_for_date(d), P.get_ref_for_date(d),
...             date2ref(d), str(sd), str(ed)])
...     print(rstgen.table(headers, rows))

>>> run_test()
============ ====== ======== ========= ============ ============
 Date         year   period   ref       start date   end date
------------ ------ -------- --------- ------------ ------------
 1985-02-03   1985   02       1985-02   1985-02-01   1985-02-28
 1999-09-01   1999   09       1999-09   1999-09-01   1999-09-30
 2000-01-01   2000   01       2000-01   2000-01-01   2000-01-31
 2015-04-27   2015   04       2015-04   2015-04-01   2015-04-30
 2024-03-24   2024   03       2024-03   2024-03-01   2024-03-31
 2059-06-01   2059   06       2059-06   2059-06-01   2059-06-30
 2997-01-23   2997   01       2997-01   2997-01-01   2997-01-31
============ ====== ======== ========= ============ ============
<BLANKLINE>

A quick test to verify :meth:`StoredYear.get_range_for_date`:

>>> for d in TEST_DATES:
...     print(str(d), *Y.get_range_for_date(d))
1985-02-03 1985-01-01 1985-12-31
1999-09-01 1999-01-01 1999-12-31
2000-01-01 2000-01-01 2000-12-31
2015-04-27 2015-01-01 2015-12-31
2024-03-24 2024-01-01 2024-12-31
2059-06-01 2059-01-01 2059-12-31
2997-01-23 2997-01-01 2997-12-31


Period types
=============

Some organizations subdivide their years in periods other than months. You can
customize this by setting :setting:`periods.period_type`, which contains one of
the choices defined in :class:`PeriodTypes`.

>>> rt.show(periods.PeriodTypes)
=========== =========== ========== ========================
 value       text        Duration   Template for reference
----------- ----------- ---------- ------------------------
 month       Month       1          {month:0>2}
 quarter     Quarter     3          Q{period}
 trimester   Trimester   4          T{period}
 semester    Semester    6          S{period}
=========== =========== ========== ========================
<BLANKLINE>

>>> dd.plugins.periods.period_type = periods.PeriodTypes.quarter

>>> run_test()
============ ====== ======== ========= ============ ============
 Date         year   period   ref       start date   end date
------------ ------ -------- --------- ------------ ------------
 1985-02-03   1985   Q1       1985-Q1   1985-01-01   1985-03-31
 1999-09-01   1999   Q3       1999-Q3   1999-07-01   1999-09-30
 2000-01-01   2000   Q1       2000-Q1   2000-01-01   2000-03-31
 2015-04-27   2015   Q2       2015-Q2   2015-04-01   2015-06-30
 2024-03-24   2024   Q1       2024-Q1   2024-01-01   2024-03-31
 2059-06-01   2059   Q2       2059-Q2   2059-04-01   2059-06-30
 2997-01-23   2997   Q1       2997-Q1   2997-01-01   2997-03-31
============ ====== ======== ========= ============ ============
<BLANKLINE>

>>> dd.plugins.periods.period_type = periods.PeriodTypes.trimester

>>> run_test()
============ ====== ======== ========= ============ ============
 Date         year   period   ref       start date   end date
------------ ------ -------- --------- ------------ ------------
 1985-02-03   1985   T1       1985-T1   1985-01-01   1985-04-30
 1999-09-01   1999   T3       1999-T3   1999-09-01   1999-12-31
 2000-01-01   2000   T1       2000-T1   2000-01-01   2000-04-30
 2015-04-27   2015   T1       2015-T1   2015-01-01   2015-04-30
 2024-03-24   2024   T1       2024-T1   2024-01-01   2024-04-30
 2059-06-01   2059   T2       2059-T2   2059-05-01   2059-08-31
 2997-01-23   2997   T1       2997-T1   2997-01-01   2997-04-30
============ ====== ======== ========= ============ ============
<BLANKLINE>


>>> dd.plugins.periods.period_type = periods.PeriodTypes.month  # restore default


Short references
================

Lino usually represents a :term:`fiscal year` using 4 digits. You can set
:setting:`periods.short_ref` to use a two-letter code.

>>> dd.plugins.periods.short_ref = True

>>> run_test()
============ ====== ======== ======= ============ ============
 Date         year   period   ref     start date   end date
------------ ------ -------- ------- ------------ ------------
 1985-02-03   85     02       85-02   1985-02-01   1985-02-28
 1999-09-01   99     09       99-09   1999-09-01   1999-09-30
 2000-01-01   00     01       00-01   2000-01-01   2000-01-31
 2015-04-27   15     04       15-04   2015-04-01   2015-04-30
 2024-03-24   24     03       24-03   2024-03-01   2024-03-31
 2059-06-01   59     06       59-06   2059-06-01   2059-06-30
 2997-01-23   97     01       97-01   2997-01-01   2997-01-31
============ ====== ======== ======= ============ ============
<BLANKLINE>

>>> dd.plugins.periods.short_ref = False  # restore default



The Y2K problem
===============

There are legacy systems where the year was internally
represented using a two-letter code. That's why we have a setting :setting:`periods.fix_y2k`, which
is either `True` or `False`. Default is `False`. If you want to represent years
using only two digits and remain y2k-proof,  set :setting:`periods.fix_y2k` to
`True` and Lino will give different reference names:

>>> dd.plugins.periods.fix_y2k = True
>>> run_test()
============ ====== ======== ======= ============ ============
 Date         year   period   ref     start date   end date
------------ ------ -------- ------- ------------ ------------
 1985-02-03   85     02       85-02   1985-02-01   1985-02-28
 1999-09-01   99     09       99-09   1999-09-01   1999-09-30
 2000-01-01   A0     01       A0-01   2000-01-01   2000-01-31
 2015-04-27   B5     04       B5-04   2015-04-01   2015-04-30
 2024-03-24   C4     03       C4-03   2024-03-01   2024-03-31
 2059-06-01   F9     06       F9-06   2059-06-01   2059-06-30
 2997-01-23   ¤7     01       ¤7-01   2997-01-01   2997-01-31
============ ====== ======== ======= ============ ============
<BLANKLINE>

This system works only for the next two hundred years, more precisely until
2259. After this the short references will look silly:

>>> print(date2ref(i2d(22591231)))
Z9-12

>>> print(date2ref(i2d(22600101)))
[0-01



>>> dd.plugins.periods.fix_y2k = False  # Restore default value

.. _dg.plugins.periods.shifted_years:

Shifted years
=============

When your fiscal or academic year starts in another month than January, you set
:setting:`periods.start_month` to the number of the first month of your fiscal
year.

On a site with shifted year, Lino represents the stored year as "YEAR/YEAR+1"

>>> dd.plugins.periods.start_month = 9
>>> run_test()
============ ========= ======== ============ ============ ============
 Date         year      period   ref          start date   end date
------------ --------- -------- ------------ ------------ ------------
 1985-02-03   1984/85   02       1984/85-02   1985-02-01   1985-02-28
 1999-09-01   1999/00   09       1999/00-09   1999-09-01   1999-09-30
 2000-01-01   1999/00   01       1999/00-01   2000-01-01   2000-01-31
 2015-04-27   2014/15   04       2014/15-04   2015-04-01   2015-04-30
 2024-03-24   2023/24   03       2023/24-03   2024-03-01   2024-03-31
 2059-06-01   2058/59   06       2058/59-06   2059-06-01   2059-06-30
 2997-01-23   2996/97   01       2996/97-01   2997-01-01   2997-01-31
============ ========= ======== ============ ============ ============
<BLANKLINE>

>>> dd.plugins.periods.start_month = 1  # Restore default value


School years
============

A school year in Belgium starts in September and has two periods called
"semesters":

>>> dd.plugins.periods.year_name = "Year"
>>> dd.plugins.periods.period_name = "Period"
>>> dd.plugins.periods.short_ref = True
>>> dd.plugins.periods.start_month = 9
>>> dd.plugins.periods.period_type = periods.PeriodTypes.semester
>>> run_test()  #doctest: +REPORT_UDIFF
============ ======= ======== ========== ============ ============
 Date         year    period   ref        start date   end date
------------ ------- -------- ---------- ------------ ------------
 1985-02-03   84/85   S1       84/85-S1   1984-09-01   1985-02-28
 1999-09-01   99/00   S1       99/00-S1   1999-09-01   2000-02-29
 2000-01-01   99/00   S1       99/00-S1   1999-09-01   2000-02-29
 2015-04-27   14/15   S2       14/15-S2   2015-03-01   2015-08-31
 2024-03-24   23/24   S2       23/24-S2   2024-03-01   2024-08-31
 2059-06-01   58/59   S2       58/59-S2   2059-03-01   2059-08-31
 2997-01-23   96/97   S1       96/97-S1   2996-09-01   2997-02-28
============ ======= ======== ========== ============ ============
<BLANKLINE>


You can customize the format used to represent a period

>>> dd.plugins.periods.period_type.ref_template
'S{period}'
>>> dd.plugins.periods.period_type.ref_template = 'P{period}'
>>> run_test()  #doctest: +REPORT_UDIFF
============ ======= ======== ========== ============ ============
 Date         year    period   ref        start date   end date
------------ ------- -------- ---------- ------------ ------------
 1985-02-03   84/85   P1       84/85-P1   1984-09-01   1985-02-28
 1999-09-01   99/00   P1       99/00-P1   1999-09-01   2000-02-29
 2000-01-01   99/00   P1       99/00-P1   1999-09-01   2000-02-29
 2015-04-27   14/15   P2       14/15-P2   2015-03-01   2015-08-31
 2024-03-24   23/24   P2       23/24-P2   2024-03-01   2024-08-31
 2059-06-01   58/59   P2       58/59-P2   2059-03-01   2059-08-31
 2997-01-23   96/97   P1       96/97-P1   2996-09-01   2997-02-28
============ ======= ======== ========== ============ ============
<BLANKLINE>


A quick test to verify :meth:`StoredYear.get_range_for_date`:

>>> for d in TEST_DATES:
...     print(str(d), *Y.get_range_for_date(d))
1985-02-03 1984-09-01 1985-08-31
1999-09-01 1999-09-01 2000-08-31
2000-01-01 1999-09-01 2000-08-31
2015-04-27 2014-09-01 2015-08-31
2024-03-24 2023-09-01 2024-08-31
2059-06-01 2058-09-01 2059-08-31
2997-01-23 2996-09-01 2997-08-31



>>> dd.plugins.periods.start_month = 1  # Restore default value
>>> dd.plugins.periods.short_ref = False
>>> dd.plugins.periods.period_type.ref_template = 'S{period}'



Plugin configuration settings
=============================

Here is a list of the :term:`plugin settings <plugin setting>` for this plugin.

.. setting:: periods.period_name
.. setting:: periods.period_name_plural
.. setting:: periods.year_name
.. setting:: periods.year_name_plural

  The end-user designation of a "stored period" and a "stored year",
  respectively.

.. setting:: periods.start_year

  An integer with the calendar year in which this site starts working.

  This is used by the :fixture:`std` fixture to fill the default list of
  :class:`StoredYears`, and by certain ``demo`` fixtures for generating demo
  invoices.

.. setting:: periods.fix_y2k

  Whether to use a Y2K compatible representation for fiscal years.
  See `The Y2K problem`_

.. setting:: periods.start_month

  The number of the first month of your fiscal year. Allowed values are 1 to 12.
  Default value is 1 (January). See `Shifted years`_.

.. setting:: periods.period_type

  A string that specifies into what kinds of periods to subdivide a years.
  Default value is 'month'. See `Period types`_.

Class reference
===============

.. class:: StoredYear

  The Django model used to store a :term:`fiscal year`.

    .. attribute:: start_date
    .. attribute:: end_date
    .. attribute:: state

.. class:: StoredPeriod

  The Django model used to store an :term:`accounting period`.

  .. attribute:: start_date
  .. attribute:: end_date
  .. attribute:: state
  .. attribute:: year
  .. attribute:: ref

.. class:: StoredYears

    The :term:`fiscal years <fiscal year>` defined in this database.

.. class:: StoredPeriods

    The :term:`accounting periods <accounting period>` defined in this database.


.. class:: PeriodTypes

  A list of choices for the values allowed as :setting:`periods.period_type`.



.. class:: PeriodRange

    Model mixin for objects that cover a range of :term:`accounting periods
    <accounting period>`.

    .. attribute:: start_period

       The first period of the range to cover.

    .. attribute:: end_period

       The last period of the range to cover.

       Leave empty if you want only one period (specified in
       :attr:`start_period`). If this is non-empty, all periods between and
       including these two are covered.

    .. method:: get_period_filter(self, voucher_prefix, **kwargs)


.. class:: PeriodRangeObservable

    Model mixin for objects that can be filtered by a range of :term:`accounting
    periods <accounting period>`. This adds two parameter fields
    :attr:`start_period` and :attr:`end_period` to every table on this model.

    Class attribute:

    .. attribute:: observable_period_field = 'accounting_period'

        The name of the database field on the observed model to use for
        filtering.

.. class:: StoredPeriodRange

    A parameter panel with two fields:

    .. attribute:: start_period

        Start of observed period range.

    .. attribute:: end_period

        Optional end of observed period range.  Leave empty to
        consider only the Start period.
