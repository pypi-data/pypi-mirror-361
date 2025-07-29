.. doctest docs/specs/avanti/cal.rst
.. _avanti.specs.cal:

=================================
Calendar functions in Lino Avanti
=================================

This document describes how standard calendar functionality is being extended by
:ref:`avanti`.


.. contents::
  :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *


Lino Avanti defines a plugin :mod:`lino_avanti.lib.cal` that extends
:mod:`lino_xl.lib.cal`.


.. currentmodule:: lino_avanti.lib.cal

.. class:: Guest

    .. attribute:: absence_reason

        Why the pupil was absent.  Choices for this field are defined
        in :class:`AbsenceReasons`.

Calendar workflow
=================

It's almost like :mod:`lino_xl.lib.cal.workflows.voga`, except that the workflow
transition for presence state "excused" (:class:`GuestStates`) is customized.
It gives permission only when the course has "Excuses permitted" checked.

In existing data (until June 2018) the "excused" and "absent" states.  In August
2018 we decided to no longer make this differentiation. In September 2024 we
partly re-introduced it for courses that have the new database field
:attr:`can_excuse <lino_avanti.lib.courses.Course.can_excuse>` checked.



>>> rt.show(cal.GuestStates)
======= =========== ============ =========== =============
 value   name        Afterwards   text        Button text
------- ----------- ------------ ----------- -------------
 10      invited     No           Invited     ?
 40      present     Yes          Present     ☑
 50      missing     Yes          Missing     ☉
 60      excused     No           Excused     ⚕
 90      cancelled   No           Cancelled   ☒
======= =========== ============ =========== =============
<BLANKLINE>

>>> show_workflow(cal.GuestStates.workflow_actions)
============= ============== =========== ============== ===================================
 Action name   Verbose name   Help text   Target state   Required states
------------- -------------- ----------- -------------- -----------------------------------
 wf1           ☑              Present     Present        invited
 wf2           ☉              Missing     Missing        invited
 wf3           Excused        Excused     Excused        invited
 wf4           ?              Invited     Invited        missing present excused cancelled
 wf5           ☒              Cancelled   Cancelled      invited
============= ============== =========== ============== ===================================


>>> rt.show(cal.EntryStates)
======= ============ ============ ============= ============= ======== ============= =========
 value   name         text         Button text   Fill guests   Stable   Transparent   No auto
------- ------------ ------------ ------------- ------------- -------- ------------- ---------
 10      suggested    Suggested    ?             Yes           No       No            No
 20      draft        Draft        ☐             Yes           No       No            No
 50      took_place   Took place   ☑             No            Yes      No            No
 70      cancelled    Cancelled    ☒             No            Yes      Yes           Yes
======= ============ ============ ============= ============= ======== ============= =========
<BLANKLINE>


>>> show_workflow(cal.EntryStates.workflow_actions)
============== ============== ============ ============== ================================
 Action name    Verbose name   Help text    Target state   Required states
-------------- -------------- ------------ -------------- --------------------------------
 reset_event    Reset          Suggested    Suggested      suggested took_place cancelled
 wf2            ☐              Draft        Draft          suggested cancelled took_place
 wf3            Took place     Took place   Took place     suggested draft cancelled
 cancel_entry   Cancel         Cancelled    Cancelled      suggested draft scheduled
============== ============== ============ ============== ================================



Choicelists
===========

>>> base = '/choices/cal/Guests/partner'
>>> show_choices("rolf", base + '?query=') #doctest: +ELLIPSIS
<BLANKLINE>
ABAD Aábdeen (15/nathalie)
ABBAS Aábid (16/nelly)
ABBASI Aáishá (19/romain)
ABDALLA Aádil (21/rolf)
ABDALLAH Aáish (28/robin)
ABDELLA Aákif (29/nathalie)
ABDELNOUR Aámir (26/nelly)
...

>>> show_choices("audrey", base + '?query=') #doctest: +ELLIPSIS
<BLANKLINE>
(15) from Eupen
(16) from Eupen
(19) from Eupen
(21) from Eupen
(28) from Eupen
(29) from Eupen
(26) from Eupen
(34) from Eupen
(37) from Eupen
...


GuestsByPartner
===============

:class:`GuestsByPartner` shows all presences except those in more than
one week and sorts them chronologically:

>>> obj = avanti.Client.objects.get(pk=16)
>>> rt.show(cal.GuestsByPartner, obj) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
January 2017: *Mon 16.*☑ *Tue 17.*☑ *Thu 19.*☑ *Fri 20.*☑ *Mon 23.*☑ *Tue 24.*☑ *Thu 26.*☒ *Fri 27.*☑ *Mon 30.*☑ *Tue 31.*☑
February 2017: *Thu 02.*☑ *Fri 03.*☑ *Mon 06.*☑ *Tue 07.*☑ *Thu 09.*? *Fri 10.*? *Mon 13.*? *Tue 14.*? *Thu 16.*? *Fri 17.*? *Mon 20.*? *Tue 21.*?
Suggested : 8 ,  Draft : 0 ,  Took place : 13 ,  Cancelled : 1


Absence reasons
===============

In :ref:`avanti` we record and analyze why pupils have been missing.

.. class:: AbsenceReasons

    The table of possible absence reasons.

    Accessible via :menuselection:`Configure --> Calendar --> Absence
    reasons`.

    >>> show_menu_path(cal.AbsenceReasons)
    Configure --> Calendar --> Absence reasons

    >>> rt.show(cal.AbsenceReasons)
    ==== ==================== ========================== ====================
     ID   Designation          Designation (de)           Designation (fr)
    ---- -------------------- -------------------------- --------------------
     1    Sickness             Krankheit                  Sickness
     2    Other valid reason   Sonstiger gültiger Grund   Other valid reason
     3    Unknown              Unbekannt                  Inconnu
     4    Unjustified          Unberechtigt               Unjustified
    ==== ==================== ========================== ====================
    <BLANKLINE>


.. class:: AbsenceReason

   .. attribute:: name


Activities with excuses
=======================

The following snippets show how the checkbox :guilabel:`Allow excuses` on an
activity influences the choices in the :guilabel:`Workflow` field when recording
presences of participants. Participants in state "Invited" have either four
workflow actions or only three because [⚕] is available only when
:guilabel:`Allow excuses` is checked.

>>> ses = rt.login("robin")
>>> obj = cal.Event.objects.get(pk=193)
>>> obj
Event #193 ('Lesson 9 (30.01.2017 18:00)')
>>> old_state = obj.state
>>> old_state
<cal.EntryStates.took_place:50>
>>> obj.state = cal.EntryStates.draft
>>> obj.save()
>>> obj.owner.can_excuse = True
>>> obj.owner.save()
>>> ses.show(cal.GuestsByEvent, master_instance=obj)
================================== ======= ================================= ================ ========
 Participant                        Role    Workflow                          Absence reason   Remark
---------------------------------- ------- --------------------------------- ---------------- --------
 ABAD Aábdeen (15/nathalie)         Pupil   **? Invited** → [☑] [☉] [⚕] [☒]
 ABDALLAH Aáish (28/robin)          Pupil   **☑ Present** → [?]
 ABDELLA Aákif (29/nathalie)        Pupil   **☉ Missing** → [?]
 ABDI Aátifá (37/rolf)              Pupil   **⚕ Excused** → [?]
 ABDOU Abeer (44/nelly)             Pupil   **☒ Cancelled** → [?]
 ABDULLA Abbáás (53/rolf)           Pupil   **? Invited** → [☑] [☉] [⚕] [☒]
 ABDULLAH Afááf (56/robin)          Pupil   **☑ Present** → [?]
 ABEZGAUZ Adrik (13/nelly)          Pupil   **☉ Missing** → [?]
 ABOOD Abdul Fáttááh (64/rolf)      Pupil   **⚕ Excused** → [?]
 ARSHAN Afimiá (33/nelly)           Pupil   **☒ Cancelled** → [?]
 ARTEMIEVA Aloyshá (40/rolf)        Pupil   **? Invited** → [☑] [☉] [⚕] [☒]
 BAH Aráli (20/nelly)               Pupil   **☑ Present** → [?]
 BEK-MURZIN Agápiiá (61/romain)     Pupil   **☉ Missing** → [?]
 DEMEULENAERE Dorothée (22/nelly)   Pupil   **⚕ Excused** → [?]
 FOFANA Denzel (48/romain)          Pupil   **☒ Cancelled** → [?]
================================== ======= ================================= ================ ========
<BLANKLINE>


>>> obj.owner.can_excuse = False
>>> obj.owner.save()
>>> ses.show(cal.GuestsByEvent, master_instance=obj)
================================== ======= ============================= ================ ========
 Participant                        Role    Workflow                      Absence reason   Remark
---------------------------------- ------- ----------------------------- ---------------- --------
 ABAD Aábdeen (15/nathalie)         Pupil   **? Invited** → [☑] [☉] [☒]
 ABDALLAH Aáish (28/robin)          Pupil   **☑ Present** → [?]
 ABDELLA Aákif (29/nathalie)        Pupil   **☉ Missing** → [?]
 ABDI Aátifá (37/rolf)              Pupil   **⚕ Excused** → [?]
 ABDOU Abeer (44/nelly)             Pupil   **☒ Cancelled** → [?]
 ABDULLA Abbáás (53/rolf)           Pupil   **? Invited** → [☑] [☉] [☒]
 ABDULLAH Afááf (56/robin)          Pupil   **☑ Present** → [?]
 ABEZGAUZ Adrik (13/nelly)          Pupil   **☉ Missing** → [?]
 ABOOD Abdul Fáttááh (64/rolf)      Pupil   **⚕ Excused** → [?]
 ARSHAN Afimiá (33/nelly)           Pupil   **☒ Cancelled** → [?]
 ARTEMIEVA Aloyshá (40/rolf)        Pupil   **? Invited** → [☑] [☉] [☒]
 BAH Aráli (20/nelly)               Pupil   **☑ Present** → [?]
 BEK-MURZIN Agápiiá (61/romain)     Pupil   **☉ Missing** → [?]
 DEMEULENAERE Dorothée (22/nelly)   Pupil   **⚕ Excused** → [?]
 FOFANA Denzel (48/romain)          Pupil   **☒ Cancelled** → [?]
================================== ======= ============================= ================ ========
<BLANKLINE>


Restore the database content:

>>> obj.state = old_state
>>> obj.save()

Actually the end users may modify the workflow field of participants even when
the activity has been marked as draft:

>>> ses.show(cal.GuestsByEvent, master_instance=obj)
================================== ======= ============================= ================ ========
 Participant                        Role    Workflow                      Absence reason   Remark
---------------------------------- ------- ----------------------------- ---------------- --------
 ABAD Aábdeen (15/nathalie)         Pupil   **? Invited** → [☑] [☉] [☒]
 ABDALLAH Aáish (28/robin)          Pupil   **☑ Present** → [?]
 ABDELLA Aákif (29/nathalie)        Pupil   **☉ Missing** → [?]
 ABDI Aátifá (37/rolf)              Pupil   **⚕ Excused** → [?]
 ABDOU Abeer (44/nelly)             Pupil   **☒ Cancelled** → [?]
 ABDULLA Abbáás (53/rolf)           Pupil   **? Invited** → [☑] [☉] [☒]
 ABDULLAH Afááf (56/robin)          Pupil   **☑ Present** → [?]
 ABEZGAUZ Adrik (13/nelly)          Pupil   **☉ Missing** → [?]
 ABOOD Abdul Fáttááh (64/rolf)      Pupil   **⚕ Excused** → [?]
 ARSHAN Afimiá (33/nelly)           Pupil   **☒ Cancelled** → [?]
 ARTEMIEVA Aloyshá (40/rolf)        Pupil   **? Invited** → [☑] [☉] [☒]
 BAH Aráli (20/nelly)               Pupil   **☑ Present** → [?]
 BEK-MURZIN Agápiiá (61/romain)     Pupil   **☉ Missing** → [?]
 DEMEULENAERE Dorothée (22/nelly)   Pupil   **⚕ Excused** → [?]
 FOFANA Denzel (48/romain)          Pupil   **☒ Cancelled** → [?]
================================== ======= ============================= ================ ========
<BLANKLINE>


Don't read on
=============

>>> print(cal.Event.objects.get(pk=123))
Ash Wednesday (01.03.2017)

>>> test_client.force_login(rt.login('robin').user)
>>> def mytest(k):
...     url = 'http://127.0.0.1:8000/api/cal/MyEntries/{}'.format(k)
...     # url = 'http://127.0.0.1:8000/#/api/cal/Entries/{}'.format(k)
...     res = test_client.get(url, REMOTE_USER='robin')
...     print(res)
...     # assert res.status_code == 200
...     # print(res.content)

>>> mytest("123")  #doctest: -SKIP +ELLIPSIS +NORMALIZE_WHITESPACE
Error during ApiElement.get(): Invalid request for '123' on cal.MyEntries (Row 123 does not exist on cal.MyEntries)
Row 123 does not exist on cal.MyEntries
Traceback (most recent call last):
...
Not Found: /api/cal/MyEntries/123
<HttpResponseNotFound status_code=404, "text/html; charset=utf-8">

Until 20241004 the result was a traceback::

  Traceback (most recent call last):
  ...
  AttributeError: 'Renderer' object has no attribute 'html_page'


>>> url = '/choices/cal/Events?query=¹'
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> assert res.status_code == 200
>>> res.content
b'{ "count": 0, "rows": [  ] }'
