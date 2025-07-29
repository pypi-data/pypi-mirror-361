.. doctest docs/specs/calview.rst
.. _book.specs.calview:

================================
``calview`` : Calendar view
================================

.. currentmodule:: lino_xl.lib.calview

The :mod:`lino_xl.lib.calview` plugin adds a calendar view.

.. contents::
  :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *

>>> ar = rt.login("robin")


Calendar views
==============

.. class:: CalendarView

    Base class for all calendar views.

    A calendar view is a virtual table that opens in detail view by default, the
    grid view is useless.

    The detail of a calendar view varies, but it usually shows at least one
    slave table, which is usually a subclass of :class:`DaySlave`.

.. class:: DailyView

    Shows a calendar navigator with a configurable daily view.

    Inherits from :class:`CalendarView`.

    .. attribute:: insert_event

      Custom action for inserting a :term:`calendar entry` in the `DailyView`.

      Returns an `eval_js` that equates to running the insert window action for
      Events with the correct known values.

.. class:: WeeklyView

    Shows a calendar navigator with a configurable weekly view.

    Inherits from :class:`CalendarView`.

.. class:: MonthlyView

    Shows a calendar navigator with a configurable monthly view.

    Inherits from :class:`CalendarView`.



The calendar views
==================

The calendar views use an instance of :class:`Day` as master instance. That's a
light-weight object representing a given date, with a primary key that is an
integer representing the offset relative to today.

>>> day = calview.WeeklyView.get_row_by_pk(ar, -6)
>>> day.__class__
<class 'lino_xl.lib.calview.mixins.Day'>
>>> day
<Day(-6=2017-02-09)>
>>> day.date
datetime.date(2017, 2, 9)

>>> def showit(t, offset=0, **kwargs):
...     day = t.calendar_view.get_row_by_pk(ar, offset)
...     ar.show(t, master_instance=day, max_width=15, **kwargs)

>>> showit(calview.WeeklySlave)
+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| Time range      | Monday          | Tuesday         | Wednesday       | Thursday        | Friday          | Saturday        | Sunday          |
+=================+=================+=================+=================+=================+=================+=================+=================+
| `All day <…>`__ | **13****New**   | **14****New** ` | ****15******New | **16****New**   | **17****New**   | **18****New**   | **19****New**   |
|                 |                 | ☒ romain Absent | **  ` ☑ rolf    |   ` ☐ Absent    |    ` ? romain   |     ` ☐ rolf    |      ` ? Absent |
|                 |                 | for private     | Absent for      | for private     | Absent for      | Absent for      | for private     |
|                 |                 | reasons <…>`__  | private reasons | reasons <…>`__  | private reasons | private reasons | reasons <…>`__  |
|                 |                 |                 | <…>`__          |                 | <…>`__          | <…>`__          |                 |
+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| `AM <…>`__      | ` 09:00 ? laura | ` 09:00 ? laura | ` 08:30 ☑       | ` 09:00 ? laura | ` 09:00 ? laura |                 | ` 08:30 ?       |
|                 | Alphabetisation | Alphabetisation | romain Réunion  | Alphabetisation | Alphabetisation |                 | Interview       |
|                 | (16/01/2017)    | (16/01/2017)    | <…>`__          | (16/01/2017)    | (16/01/2017)    |                 | <…>`__` 09:40 ☐ |
|                 | Lesson 17       | Lesson 18       |                 | Lesson 19       | Lesson 20       |                 | romain Diner    |
|                 | <…>`__` 09:40 ☑ | <…>`__` 11:10 ☑ |                 | <…>`__` 09:40 ? | <…>`__` 10:20 ☐ |                 | <…>`__          |
|                 | Interview       | rolf Abendessen |                 | rolf Beratung   | Seminar         |                 |                 |
|                 | <…>`__` 10:20 ☒ | <…>`__          |                 | <…>`__          | <…>`__` 11:10 ? |                 |                 |
|                 | romain Diner    |                 |                 |                 | romain          |                 |                 |
|                 | <…>`__          |                 |                 |                 | Evaluation      |                 |                 |
|                 |                 |                 |                 |                 | <…>`__          |                 |                 |
+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| `PM <…>`__      | ` 14:00 ? laura | ` 14:00 ? laura | ` 13:30 ☒       | ` 14:00 ? laura | ` 14:00 ? laura | ` 13:30 ☐ rolf  |                 |
|                 | Alphabetisation | Alphabetisation | Breakfast       | Alphabetisation | Alphabetisation | Erstgespräch    |                 |
|                 | (16/01/2017)    | (16/01/2017)    | <…>`__          | (16/01/2017)    | (16/01/2017)    | <…>`__          |                 |
|                 | Lesson 17       | Lesson 18       |                 | Lesson 19       | Lesson 20       |                 |                 |
|                 | <…>`__` 18:00 ? | <…>`__` 18:00 ? |                 | <…>`__` 18:00 ? | <…>`__` 18:00 ? |                 |                 |
|                 | laura           | laura           |                 | laura           | laura           |                 |                 |
|                 | Alphabetisation | Alphabetisation |                 | Alphabetisation | Alphabetisation |                 |                 |
|                 | (16/01/2017)    | (16/01/2017)    |                 | (16/01/2017)    | (16/01/2017)    |                 |                 |
|                 | Lesson 17       | Lesson 18       |                 | Lesson 19       | Lesson 20       |                 |                 |
|                 | <…>`__          | <…>`__          |                 | <…>`__          | <…>`__          |                 |                 |
+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
<BLANKLINE>


>>> showit(calview.MonthlySlave)
+-------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| Week  | Monday          | Tuesday         | Wednesday       | Thursday        | Friday          | Saturday        | Sunday          |
+=======+=================+=================+=================+=================+=================+=================+=================+
| **5** | **30****New**`  | **31****New**   | **1****New**` 1 | **2****New**    | **3****New**` 0 | **4****New**    | **5****New**` 1 |
|       | 08:30 ☒ Seminar |                 | 1:10 ☑          |                 | 9:40 ☒          |                 | 3:30 ☑ Seminar  |
|       | <…>`__          |                 | Interview       |                 | Breakfast       |                 | <…>`__          |
|       |                 |                 | <…>`__          |                 | <…>`__          |                 |                 |
+-------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| **6** | **6****New**    | **7****New**` 1 | **8****New**    | **9****New**` 0 | **10****New**   | **11****New**`  | **12****New**   |
|       |                 | 0:20 ☒          |                 | 8:30 ☑          |                 | 11:10 ☒ Seminar |                 |
|       |                 | Interview       |                 | Breakfast       |                 | <…>`__          |                 |
|       |                 | <…>`__          |                 | <…>`__          |                 |                 |                 |
+-------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| **7** | **13****New**`  | **14****New**   | ****15******New | **16****New**`  | **17****New** ` | **18****New**   | **19****New** ` |
|       | 09:40 ☑         |                 | **` 13:30 ☒     | ☐ Absent for    |  10:20 ☐        |                 | ? Absent for    |
|       | Interview       |                 | Breakfast       | private reasons | Seminar <…>`__  |                 | private reasons |
|       | <…>`__          |                 | <…>`__          | <…>`__          |                 |                 | <…>`__` 08:30 ? |
|       |                 |                 |                 |                 |                 |                 | Interview       |
|       |                 |                 |                 |                 |                 |                 | <…>`__          |
+-------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| **8** | **20****New**`  | **21****New** ` | **22****New** ` | **23****New**   | **24****New**   | **25****New**   | **26****New**   |
|       | <…>`__          |  11:10 ☐        | ☐ Absent for    | ` 09:40 ?       |                 | ` 13:30 ☐       |                 |
|       |                 | Breakfast       | private reasons | Seminar <…>`__  |                 | Interview       |                 |
|       |                 | <…>`__          | <…>`__          |                 |                 | <…>`__          |                 |
+-------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
| **9** | **27****New**`  | **28****New**   | **1****New**` 0 | **2****New**    | **3****New**` 1 | **4****New**    | **5****New**` 0 |
|       | 10:20 ?         |                 | 8:30 ☐ Seminar  |                 | 1:10 ?          |                 | 9:40 ☐          |
|       | Breakfast       |                 | <…>`__          |                 | Interview       |                 | Breakfast       |
|       | <…>`__          |                 |                 |                 | <…>`__          |                 | <…>`__          |
+-------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+-----------------+
<BLANKLINE>



>>> showit(calview.DailySlave)
+-----------------+-----------------+----------+
| Time range      | External        | Internal |
+=================+=================+==========+
| `All day <…>`__ | `  ☒ romain     |          |
|                 | Absent for      |          |
|                 | private reasons |          |
|                 | <…>`__`  ☑ rolf |          |
|                 | Absent for      |          |
|                 | private reasons |          |
|                 | <…>`__          |          |
+-----------------+-----------------+----------+
| `AM <…>`__      | ` 08:30 ☑       |          |
|                 | romain Réunion  |          |
|                 | <…>`__          |          |
+-----------------+-----------------+----------+
| `PM <…>`__      |                 |          |
+-----------------+-----------------+----------+
<BLANKLINE>




The daily planner
=================

The daily planner is a table that shows an overview on all events of a day.

>>> showit(calview.DailyPlanner, -6)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
+-----------------+-----------------+----------+
| Time range      | External        | Internal |
+=================+=================+==========+
| `All day <…>`__ |                 |          |
+-----------------+-----------------+----------+
| `AM <…>`__      | ` 09:40 ☒       |          |
|                 | romain Réunion  |          |
|                 | <…>`__          |          |
+-----------------+-----------------+----------+
| `PM <…>`__      |                 |          |
+-----------------+-----------------+----------+
<BLANKLINE>



.. class:: DailyPlanner

    The virtual table used to render the daily planner.


.. >>> dd.today()
   datetime.date(2017, 2, 15)


.. class:: PlannerColumns

    A choicelist that defines the columns to appear in the daily
    planner. This list can be modified locally.


A default configuration has two columns in the daily planner:

>>> rt.show(calview.PlannerColumns)
======= ========== ==========
 value   name       text
------- ---------- ----------
 10      external   External
 20      internal   Internal
======= ========== ==========
<BLANKLINE>


.. class:: DailyPlannerRow

    A database object that represents one row of the :term:`daily planner`.
    The default configuration has "AM", "PM" and "All day".

>>> rt.show(calview.DailyPlannerRows)
===== ============= ================== ================== ============ ==========
 No.   Designation   Designation (de)   Designation (fr)   Start time   End time
----- ------------- ------------------ ------------------ ------------ ----------
 1     AM            Vormittags         Avant-midi                      12:00:00
 2     PM            Nachmittags        Après-midi         12:00:00
===== ============= ================== ================== ============ ==========
<BLANKLINE>



Utilities
=========

.. class:: Day

    An in-memory wrapper around a `datetime.date` instance.

    A subclass of :class:`lino.core.fields.TableRow`.

    .. attribute:: date
    .. attribute:: pk
    .. attribute:: ar
    .. attribute:: navigation_mode


.. class:: DaySlave

    Table mixin for slave tables of tables on :class:`Day`.

    Used by both database and virtual tables.

.. class:: DayNavigator

    Base class for the three calendar views, but also used for independent
    tables like working.WorkedHours. A virtual table whose rows are calview.Day
    instances.  Subclasses must set navigation_mode.

    Inherits from :class:`DaysTable`.





Tested translations
===================


>>> with translation.override('de'):
...     showit(calview.DailyPlanner, -6, header_level=1)
===========================
Donnerstag, 9. Februar 2017
===========================
+-----------------+-----------------+--------+
| Zeitabschnitt   | Extern          | Intern |
+=================+=================+========+
| `Ganztags       |                 |        |
| <…>`__          |                 |        |
+-----------------+-----------------+--------+
| `Vormittags     | ` 09:40 ☒       |        |
| <…>`__          | romain Réunion  |        |
|                 | <…>`__          |        |
+-----------------+-----------------+--------+
| `Nachmittags    |                 |        |
| <…>`__          |                 |        |
+-----------------+-----------------+--------+
<BLANKLINE>


>>> showit(calview.DailyPlanner, -6, language="fr", header_level=1)
====================
jeudi 9 février 2017
====================
+-----------------+-----------------+---------+
| Time range      | Externe         | Interne |
+=================+=================+=========+
| `Journée        |                 |         |
| entière <…>`__  |                 |         |
+-----------------+-----------------+---------+
| `Avant-midi     | ` 09:40 ☒       |         |
| <…>`__          | romain Réunion  |         |
|                 | <…>`__          |         |
+-----------------+-----------------+---------+
| `Après-midi     |                 |         |
| <…>`__          |                 |         |
+-----------------+-----------------+---------+
<BLANKLINE>


>>> update_guests = cal.Events.get_action_by_name('update_guests')
>>> print(update_guests.help_text)
Populate or update the list of participants for this calendar entry according to the suggestions.

>>> with translation.override('de'):
...     print(str(update_guests.help_text))
... #doctest: +NORMALIZE_WHITESPACE +REPORT_CDIFF
Teilnehmerliste für diesen Kalendereintrag füllen entsprechend der Vorschläge.

>>> update_guests.help_text.__class__
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
<class 'django.utils.functional...__proxy__'>


Class inheritance
=================


.. inheritance-diagram::
    lino_xl.lib.calview.ui.DailyView
    lino_xl.lib.calview.ui.WeeklyView
    lino_xl.lib.calview.ui.MonthlyView
    :parts: 1
    :top-classes: lino.core.actors.Actor

.. inheritance-diagram::
    lino_xl.lib.calview.ui.DailySlave
    lino_xl.lib.calview.ui.WeeklySlave
    lino_xl.lib.calview.ui.MonthlySlave
    :parts: 1
    :top-classes: lino.core.actors.Actor


Multiple "planners"
===================


>>> rt.show(calview.Planners)
========= ========= ========== ===================== ==================== ===================
 value     name      text       Monthly view          Weekly view          Daily view
--------- --------- ---------- --------------------- -------------------- -------------------
 default   default   Calendar   calview.MonthlyView   calview.WeeklyView   calview.DailyView
========= ========= ========== ===================== ==================== ===================
<BLANKLINE>

The Day object
==============

>>> from lino_xl.lib.calview.mixins import Day
>>> modes = ('day', 'week', 'month')
>>> headers = ["Offset"] + list(modes)
>>> rows = []
>>> for offset in (0, -10, 15):
...     cells = [str(offset)]
...     for nm in modes:
...         cells.append(str(Day(offset, ar, nm)))
...     rows.append(cells)
>>> print(rstgen.table(headers, rows))
... #doctest: +NORMALIZE_WHITESPACE
======== ============================= ============================= ===============
 Offset   day                          week                          month
-------- ----------------------------- ----------------------------- ---------------
 0        Wednesday, 15 February 2017   Week 7 / 2017 (13 February)   February 2017
 -10      Sunday, 5 February 2017       Week 5 / 2017 (30 January)    February 2017
 15       Thursday, 2 March 2017        Week 9 / 2017 (27 February)   March 2017
======== ============================= ============================= ===============
<BLANKLINE>




7 October 2015 : Wednesday or Saturday?
=======================================

Trying to understand #5610 (calview.WeeklyView renders the weekdays wrong)

The 2015-10-07 is a Wednesday:

>>> offset = 5
>>> print(dd.today(offset))
2017-02-20

>>> day = calview.DailyView.get_row_by_pk(ar, offset)
>>> print(day)
Monday, 20 February 2017

The following is wrong. The case should fail. It should show 20 for the first
column.

>>> ar.show(calview.WeeklySlave, master_instance=day, max_width=10)
+------------+------------+------------+------------+------------+------------+------------+------------+
| Time range | Monday     | Tuesday    | Wednesday  | Thursday   | Friday     | Saturday   | Sunday     |
+============+============+============+============+============+============+============+============+
| `All day   | **20****Ne | **21****Ne | **22****Ne | **23****Ne | **24****Ne | **25****Ne | **26****Ne |
| <…>`__     | w** ` ☐    | w**  ` ?   | w**   ` ☐  | w**    ` ? | w**        | w**        | w**        |
|            | romain     | rolf       | Absent for | romain     |            |            |            |
|            | Absent for | Absent for | private    | Absent for |            |            |            |
|            | private    | private    | reasons    | private    |            |            |            |
|            | reasons    | reasons    | <…>`__     | reasons    |            |            |            |
|            | <…>`__     | <…>`__     |            | <…>`__     |            |            |            |
+------------+------------+------------+------------+------------+------------+------------+------------+
| `AM <…>`__ | ` 09:00 ?  | ` 09:00 ?  | ` 08:30 ☐  | ` 09:00 ?  | ` 09:00 ?  | ` 08:30 ?  | ` 09:40 ☐  |
|            | laura Alph | laura Alph | rolf       | laura Alph | laura Alph | romain     | rolf       |
|            | abetisatio | abetisatio | Beratung   | abetisatio | abetisatio | Diner      | Abendessen |
|            | n (16/01/2 | n (16/01/2 | <…>`__     | n (16/01/2 | n (16/01/2 | <…>`__     | <…>`__     |
|            | 017)       | 017)       |            | 017)       | 017)       |            |            |
|            | Lesson 21  | Lesson 22  |            | Lesson 23  | Lesson 24  |            |            |
|            | <…>`__` 10 | <…>`__` 11 |            | <…>`__` 09 | <…>`__` 11 |            |            |
|            | :20 ? rolf | :10 ☐      |            | :40 ?      | :10 ? rolf |            |            |
|            | Abendessen | Breakfast  |            | Seminar <… | Erstgesprä |            |            |
|            | <…>`__     | <…>`__     |            | >`__` 10:2 | ch <…>`__  |            |            |
|            |            |            |            | 0 ☐ romain |            |            |            |
|            |            |            |            | Evaluation |            |            |            |
|            |            |            |            | <…>`__     |            |            |            |
+------------+------------+------------+------------+------------+------------+------------+------------+
| `PM <…>`__ | ` 14:00 ?  | ` 13:30 ?  |            | ` 14:00 ?  | ` 14:00 ?  | ` 13:30 ☐  |            |
|            | laura Alph | romain     |            | laura Alph | laura Alph | Interview  |            |
|            | abetisatio | Réunion <… |            | abetisatio | abetisatio | <…>`__     |            |
|            | n (16/01/2 | >`__` 14:0 |            | n (16/01/2 | n (16/01/2 |            |            |
|            | 017)       | 0 ? laura  |            | 017)       | 017)       |            |            |
|            | Lesson 21  | Alphabetis |            | Lesson 23  | Lesson 24  |            |            |
|            | <…>`__` 18 | ation (16/ |            | <…>`__` 18 | <…>`__` 18 |            |            |
|            | :00 ?      | 01/2017)   |            | :00 ?      | :00 ?      |            |            |
|            | laura Alph | Lesson 22  |            | laura Alph | laura Alph |            |            |
|            | abetisatio | <…>`__` 18 |            | abetisatio | abetisatio |            |            |
|            | n (16/01/2 | :00 ?      |            | n (16/01/2 | n (16/01/2 |            |            |
|            | 017)       | laura Alph |            | 017)       | 017)       |            |            |
|            | Lesson 21  | abetisatio |            | Lesson 23  | Lesson 24  |            |            |
|            | <…>`__     | n (16/01/2 |            | <…>`__     | <…>`__     |            |            |
|            |            | 017)       |            |            |            |            |            |
|            |            | Lesson 22  |            |            |            |            |            |
|            |            | <…>`__     |            |            |            |            |            |
+------------+------------+------------+------------+------------+------------+------------+------------+
<BLANKLINE>
