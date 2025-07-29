.. doctest docs/specs/tera/cal.rst
.. _specs.tera.cal:

=====================
Calendar in Lino Tera
=====================

This document describes the :mod:`lino_tera.lib.cal` plugin which extends
:mod:`lino_xl.lib.cal` for Tera.


.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.tera1.settings')
>>> from lino.api.doctest import *
>>> from django.db import models


.. currentmodule:: lino_tera.lib.cal



My appointments
===============

The *My appointments* table also shows in the dashboard when it has no
data to display.

>>> show_dashboard("elmar", ignore_links=False)
... #doctest:  +REPORT_UDIFF +ELLIPSIS +NORMALIZE_WHITESPACE
Quick links: [My settings](… "Edit your user preferences.") | [Calendar](… "Open a detail
window on records of calview.") | [New note](… "Insert a new Note.") | [My
Notes](…)
<BLANKLINE>
Hi, Elmar!
<BLANKLINE>
Recent birthdays: 05-22 [Laura Laschet](…) (36)
<BLANKLINE>
This is a Lino demo site. Try also the other [demo sites](http://lino-
framework.org/demos.html). Your feedback is welcome to [users@lino-
framework.org](mailto:users@lino-framework.org) or directly to the person who
invited you. **We are running with simulated date set to Saturday, 23 May
2015.**
<BLANKLINE>
## My appointments **New** [⏏](… "Show this table in own window")
<BLANKLINE>
No data to display
<BLANKLINE>
## Saturday, 23 May 2015 [⏏](… "Show this table in own window")
<BLANKLINE>
===...===... Time range External Internal \-...---...---
`All day <…>`__ ` ☉ romain Absent for private reasons <…>`__` ⚕ rolf
Absent for private reasons <…>`__ `AM <…>`__ ` 08:30 ☑ romain Réunion <…>`__ `PM
<…>`__
===...===


The calendar summary view
=========================

Note that the months are listed in reverse chronological order while
the days within a month in normal order.


>>> obj = rt.models.courses.Course.objects.order_by('id').first()
>>> rt.show(cal.EntriesByController, obj)
March 2015: `Tue 10. <…>`__☑
February 2015: `Tue 24. <…>`__☑ `Tue 10. <…>`__☑
January 2015: `Tue 27. <…>`__☉ `Tue 13. <…>`__☑
Suggested : 0 ,  Scheduled : 0 ,  Took place : 4 ,  Missed : 1 ,  Called off : 0


Missed calendar entries
=======================

In :ref:`tera` we introduce a new calendar entry state "missed" for
entries where the guest missed the appointment without a valid reason.
A *missed* appointment may get invoiced while a *cancelled*
appointment not.

Changed the symbol for a "Cancelled" calendar entry from ☉ to
⚕. Because the symbol ☉ (a sun) is used for "Missed".  The sun reminds
a day on the beach while the ⚕ reminds a drugstore.


>>> rt.show(cal.EntryStates)
======= ============ ============ ============= ============= ======== ============= =========
 value   name         text         Button text   Fill guests   Stable   Transparent   No auto
------- ------------ ------------ ------------- ------------- -------- ------------- ---------
 10      suggested    Suggested    ?             Yes           No       No            No
 20      draft        Scheduled    ☐             Yes           No       No            No
 50      took_place   Took place   ☑             No            Yes      No            No
 60      missed       Missed       ☉             No            Yes      No            Yes
 70      cancelled    Called off   ⚕             No            Yes      Yes           Yes
======= ============ ============ ============= ============= ======== ============= =========
<BLANKLINE>


>>> rt.show(cal.EntryStates, language="de")
====== ============ =============== ============= ================= ======== =================== =========
 Wert   name         Text            Button text   Gäste ausfüllen   Stabil   nicht blockierend   No auto
------ ------------ --------------- ------------- ----------------- -------- ------------------- ---------
 10     suggested    Vorschlag       ?             Ja                Nein     Nein                Nein
 20     draft        Geplant         ☐             Ja                Nein     Nein                Nein
 50     took_place   Stattgefunden   ☑             Nein              Ja       Nein                Nein
 60     missed       Verpasst        ☉             Nein              Ja       Nein                Ja
 70     cancelled    Abgesagt        ⚕             Nein              Ja       Ja                  Ja
====== ============ =============== ============= ================= ======== =================== =========
<BLANKLINE>


:ref:`tera` uses the :attr:`EntryState.guest_state` attribute.

>>> rt.show(cal.EntryStates, column_names='name text guest_state')
============ ============ =============
 name         text         Guest state
------------ ------------ -------------
 suggested    Suggested
 draft        Scheduled
 took_place   Took place   Present
 missed       Missed       Missing
 cancelled    Called off   Excused
============ ============ =============
<BLANKLINE>


Guest workflow
==============

>>> rt.show(cal.GuestStates, language="de")
====== =========== ============== ============== =============
 Wert   name        Nachträglich   Text           Button text
------ ----------- -------------- -------------- -------------
 10     invited     Nein           Eingeladen     ?
 40     present     Ja             Anwesend       ☑
 50     missing     Ja             Fehlt          ☉
 60     excused     Nein           Entschuldigt   ⚕
 90     cancelled   Nein           Storniert      ☒
====== =========== ============== ============== =============
<BLANKLINE>


>>> show_workflow(cal.GuestStates.workflow_actions, language="de")
============= ============== ============== ============== =========================
 Action name   Verbose name   Help text      Target state   Required states
------------- -------------- -------------- -------------- -------------------------
 wf1           ☑              Anwesend       Anwesend       invited
 wf2           ☉              Fehlt          Fehlt          invited
 wf3           ⚕              Entschuldigt   Entschuldigt   invited
 wf4           ?              Eingeladen     Eingeladen     missing present excused
============= ============== ============== ============== =========================

Calendar entry types
====================


>>> rt.show(cal.EventTypes)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ======================== ================== ======================== ================ ============= ===================== =================
 Reference   Designation              Designation (de)   Designation (fr)         Planner column   Appointment   Automatic presences   Locks all rooms
----------- ------------------------ ------------------ ------------------------ ---------------- ------------- --------------------- -----------------
             Absences                 Abwesenheiten      Absences                 External         Yes           No                    No
             Group meeting            Gruppengespräch    Group meeting                             Yes           No                    No
             Holidays                 Feiertage          Jours fériés             External         No            No                    Yes
             Individual appointment   Einzelgespräch     Individual appointment                    Yes           Yes                   No
             Internal                 Intern             Interne                  Internal         No            No                    No
             Meeting                  Versammlung        Réunion                  External         Yes           No                    No
=========== ======================== ================== ======================== ================ ============= ===================== =================
<BLANKLINE>


Daily planner
=============

>>> rt.show(calview.DailySlave, max_width=60)
+-----------------+--------------------------------------------------------------+----------+
| Time range      | External                                                     | Internal |
+=================+==============================================================+==========+
| `All day <…>`__ | `  ☉ romain Absent for private reasons <…>`__`  ⚕ rolf       |          |
|                 | Absent for private reasons <…>`__                            |          |
+-----------------+--------------------------------------------------------------+----------+
| `AM <…>`__      | ` 08:30 ☑ romain Réunion <…>`__                              |          |
+-----------------+--------------------------------------------------------------+----------+
| `PM <…>`__      |                                                              |          |
+-----------------+--------------------------------------------------------------+----------+
<BLANKLINE>


When you are logged in, the calendar entries are clickable:

>>> rt.login("robin").show(calview.DailySlave, max_width=60)  #doctest: +NORMALIZE_WHITESPACE
+-----------------+--------------------------------------------------------------+----------+
| Time range      | External                                                     | Internal |
+=================+==============================================================+==========+
| `All day <…>`__ | `  ☉ romain Absent for private reasons <…>`__`  ⚕ rolf       |          |
|                 | Absent for private reasons <…>`__                            |          |
+-----------------+--------------------------------------------------------------+----------+
| `AM <…>`__      | ` 08:30 ☑ romain Réunion <…>`__                              |          |
+-----------------+--------------------------------------------------------------+----------+
| `PM <…>`__      |                                                              |          |
+-----------------+--------------------------------------------------------------+----------+
<BLANKLINE>


.. class:: Event

    .. attribute:: amount

        The amount perceived during this appointment.
