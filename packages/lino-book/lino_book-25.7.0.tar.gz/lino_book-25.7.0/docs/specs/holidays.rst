.. doctest docs/specs/holidays.rst
.. _xl.specs.holidays:

=================
Defining holidays
=================

The :mod:`lino_xl.lib.cal` plugin also adds functionality for managing holidays
and birthdays.


.. contents::
   :depth: 1
   :local:


Some initialization:

>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *
>>> settings.SITE.verbose_client_info_message = True
>>> from lino.api import rt, _
>>> from atelier.utils import i2d
>>> RecurrentEvent = cal.RecurrentEvent
>>> Recurrences = cal.Recurrences


Recurrent events
================

A series of standard holidays are defined as :term:`recurrent events <recurrent
event>` by the :fixture:`std` fixture of :mod:`lino_xl.lib.cal`:

>>> rt.show(cal.RecurrentEvents)
============ ========== ============================ ===================== =================================== ==================== =====================
 Start date   End Date   Designation                  Designation (de)      Designation (fr)                    Recurrence           Calendar entry type
------------ ---------- ---------------------------- --------------------- ----------------------------------- -------------------- ---------------------
 01/01/2013              New Year's Day               Neujahr               Jour de l'an                        yearly               Holidays
 11/02/2013              Rosenmontag                  Rosenmontag           Lundi de carnaval                   Relative to Easter   Holidays
 13/02/2013              Ash Wednesday                Aschermittwoch        Mercredi des Cendres                Relative to Easter   Holidays
 29/03/2013              Good Friday                  Karfreitag            Vendredi Saint                      Relative to Easter   Holidays
 31/03/2013              Easter sunday                Ostersonntag          Pâques                              Relative to Easter   Holidays
 01/04/2013              Easter monday                Ostermontag           Lundi de Pâques                     Relative to Easter   Holidays
 01/05/2013              International Workers' Day   Tag der Arbeit        Premier Mai                         yearly               Holidays
 09/05/2013              Ascension of Jesus           Christi Himmelfahrt   Ascension                           Relative to Easter   Holidays
 20/05/2013              Pentecost                    Pfingsten             Pentecôte                           Relative to Easter   Holidays
 21/07/2013              National Day                 Nationalfeiertag      Fête nationale                      yearly               Holidays
 15/08/2013              Assumption of Mary           Mariä Himmelfahrt     Assomption de Marie                 yearly               Holidays
 31/10/2013              All Souls' Day               Allerseelen           Commémoration des fidèles défunts   yearly               Holidays
 01/11/2013              All Saints' Day              Allerheiligen         Toussaint                           yearly               Holidays
 11/11/2013              Armistice with Germany       Waffenstillstand      Armistice                           yearly               Holidays
 25/12/2013              Christmas                    Weihnachten           Noël                                yearly               Holidays
============ ========== ============================ ===================== =================================== ==================== =====================
<BLANKLINE>


Relative to Easter
==================

Certain :term:`recurrent events <recurrent event>` are :term:`relative to
Easter`. Let's look at one of them, Ash Wednesday::

>>> ash = RecurrentEvent.objects.get(name="Ash Wednesday")

.. the following doesn't yet work:

    >>> # screenshot(ash, 'ash.png')

    followed by a .. image:: ash.png directive.


The :fixture:`std`
fixture of :mod:`lino_xl.lib.cal`
generates
automatically all Ash Wednesdays for a range of years:

>>> rt.show(cal.EntriesByController, master_instance=ash, nosummary=True)
================ =================== ================= ===== ================== =====================
 When             Short description   Workflow          No.   Responsible user   Calendar entry type
---------------- ------------------- ----------------- ----- ------------------ ---------------------
 Wed 06/03/2019   Ash Wednesday       **? Suggested**   7                        Holidays
 Wed 14/02/2018   Ash Wednesday       **? Suggested**   6                        Holidays
 Wed 01/03/2017   Ash Wednesday       **? Suggested**   5                        Holidays
 Wed 10/02/2016   Ash Wednesday       **? Suggested**   4                        Holidays
 Wed 18/02/2015   Ash Wednesday       **? Suggested**   3                        Holidays
 Wed 05/03/2014   Ash Wednesday       **? Suggested**   2                        Holidays
================ =================== ================= ===== ================== =====================
<BLANKLINE>

Actually the user sees just the summary:

>>> rt.show(cal.EntriesByController, master_instance=ash)
March 2019: `Wed 06. <…>`__?
February 2018: `Wed 14. <…>`__?
March 2017: `Wed 01. <…>`__?
February 2016: `Wed 10. <…>`__?
February 2015: `Wed 18. <…>`__?
March 2014: `Wed 05. <…>`__?
Suggested : 6 ,  Draft : 0 ,  Published : 0 ,  Took place : 0 ,  Cancelled : 0

That range of years depends on some configuration variables:

- :attr:`ignore_dates_before <lino_xl.lib.cal.Plugin.ignore_dates_before>`
- :attr:`ignore_dates_after <lino_xl.lib.cal.Plugin.ignore_dates_after>`
- :attr:`lino.modlib.system.SiteConfig.max_auto_events`
- :attr:`the_demo_date <lino.core.site.Site.the_demo_date>`

>>> dd.plugins.cal.ignore_dates_before
>>> dd.plugins.cal.ignore_dates_after
datetime.date(2019, 10, 23)
>>> settings.SITE.site_config.max_auto_events
72
>>> settings.SITE.the_demo_date
datetime.date(2014, 10, 23)

Manually creating moving feasts
===============================

The :term:`recurrency rules<recurrency rule>`  for moving feasts have their
:attr:`every_unit <lino_xl.lib.cal.RecurrentEvent.every_unit>` field set to
:attr:`easter <lino.modlib.system.Recurrences.easter>`.

Lino then computes the offset (number of days) between your :attr:`start_date`
and the Easter date of the start year, and generates subsequent events by moving
their date so that the offset remains the same.

Lino uses the `easter()
<https://labix.org/python-dateutil#head-8863c4fc47132b106fcb00b9153e3ac0ab486a0d>`_
function of `dateutil` for getting the Easter date.

>>> from dateutil.easter import easter
>>> easter(2015)
datetime.date(2015, 4, 5)



Adding a local moving feast
===========================

.. verify that no events have actually been saved:
   >>> cal.Event.objects.count()
   171

We can add our own local custom holidays which depend on easter.

We create a :term:`recurrency rule` for it, specifying :attr:`easter
<lino.modlib.system.Recurrences.easter>` in their
:attr:`every_unit <lino_xl.lib.cal.RecurrentEvent.every_unit>`
field.

>>> holidays = cal.EventType.objects.get(**dd.str2kw('name', _("Holidays")))
>>> obj = RecurrentEvent(name="Karneval in Kettenis",
...     every_unit=Recurrences.easter,
...     start_date=i2d(20160209), event_type=holidays)
>>> obj.full_clean()
>>> obj.find_start_date(i2d(20160209))
datetime.date(2016, 2, 9)

>>> set_log_level(logging.DEBUG)
>>> ar = rt.login()
>>> wanted, unwanted = obj.get_wanted_auto_events(ar)
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS -REPORT_NDIFF
Generating events between 2016-02-09 and 2019-10-23 (max. 72).
Reached upper date limit 2019-10-23 for 4

>>> len(wanted)
4

.. Note that owner_type in below snippet depends on whether the database has
   been prepared under Py2 or Py3

>>> wanted[0]  #doctest: +ELLIPSIS
Event(start_date=2016-02-09,owner_type=...,summary='Karneval in Kettenis',auto_type=1,priority=<xl.Priorities.normal:30>,event_type=2,state=<cal.EntryStates.suggested:10>,notify_unit=<cal.NotifyBeforeUnits.minutes:10>)
