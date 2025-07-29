.. doctest docs/specs/voga/courses.rst
.. _voga.specs.courses:

========================
``courses`` in Lino Voga
========================

.. currentmodule:: lino_voga.lib.courses

This document specifies how the :mod:`lino_xl.lib.courses` plugin is
being used in :ref:`voga`.

See also :ref:`ug.plugins.courses`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.voga2.startup import *


Implementation
==============

>>> dd.plugins.courses
<lino_voga.lib.roger.courses.Plugin lino_voga.lib.roger.courses(needs ['lino_xl.lib.cal'])>


>>> dd.plugins.courses.__class__.__bases__
(<class 'lino_voga.lib.courses.Plugin'>,)

>>> settings.SITE.default_ui
'lino_react.react'

>>> pprint(settings.SITE.kernel.web_front_ends)
[<lino_react.react.Plugin lino_react.react(needs ['lino.modlib.jinja'])>]


Activity layouts
================

The :class:`ActivityLayouts` choicelist in :ref:`voga` defines the
following areas:

>>> rt.show(courses.ActivityLayouts)
======= ========== ========== ==================
 value   name       text       Table
------- ---------- ---------- ------------------
 C       default    Courses    courses.Courses
 H       hikes      Hikes      courses.Hikes
 J       journeys   Journeys   courses.Journeys
======= ========== ========== ==================
<BLANKLINE>


The :mod:`lino_xl.lib.courses` plugin has two settings
:attr:`teacher_model <lino_xl.lib.courses.Plugin.teacher_model>` and
:attr:`pupil_model <lino_xl.lib.courses.Plugin.pupil_model>`:


>>> dd.plugins.courses.teacher_model
<class 'lino_voga.lib.courses.models.Teacher'>

>>> dd.plugins.courses.pupil_model
<class 'lino_voga.lib.roger.courses.models.Pupil'>


.. class:: Pupil

  Django model used to represent a :term:`pupil`.

  It defines an additional field :attr:`pupil_type`.

    .. attribute:: pupil_type

        Pointer to :class:`PupilType`.

.. class:: Teacher

  Django model used to represent a :term:`teacher`.

  It has an additional field :attr:`teacher_type`.

    .. attribute:: teacher_type

        Pointer to :class:`TeacherType`.


The demo database has 35 pupils and 9 teachers:

>>> rt.models.courses.Pupil.objects.count()
35
>>> rt.models.courses.Teacher.objects.count()
9


>>> rt.show('courses.Teachers')
==================== =============================== =================
 Name                 Address                         Instructor type
-------------------- ------------------------------- -----------------
 Hans Altenberg       Aachener Straße, 4700 Eupen
 Charlotte Collard    Auf dem Spitzberg, 4700 Eupen
 Daniel Emonts        Bellmerin, 4700 Eupen
 Germaine Gernegroß   Buchenweg, 4700 Eupen
 Josef Jonas          Gülcherstraße, 4700 Eupen
 Marc Malmendier      Heidhöhe, 4700 Eupen
 Edgard Radermacher   4730 Raeren
 Tom Thess            4700 Eupen
 David da Vinci       4730 Raeren
==================== =============================== =================
<BLANKLINE>


>>> ses = rt.login('robin')

.. class:: PupilType

  Django model used to represent a :term:`pupil type`.

  >>> ses.show(rt.models.courses.PupilTypes)
  ==== ============= ================== ================== ===========
   ID   Designation   Designation (de)   Designation (fr)   Reference
  ---- ------------- ------------------ ------------------ -----------
   1    Member        Mitglied           Member             M
   2    Helper        Helfer             Helper             H
   3    Non-member    Nicht-Mitglied     Non-member         N
  ==== ============= ================== ================== ===========
  <BLANKLINE>


.. class:: TeacherType

  Django model used to represent a :term:`teacher type`.

  >>> ses.show(rt.models.courses.TeacherTypes)
  ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
  ==== ================== ======================= ====================== ===========
   ID   Designation        Designation (de)        Designation (fr)       Reference
  ---- ------------------ ----------------------- ---------------------- -----------
   1    Independant        Selbstständig           Indépendant            S
   2    Voluntary (flat)   Ehrenamtlich pauschal   Volontaire (forfait)   EP
   3    Voluntary (real)   Ehrenamtlich real       Volontaire (réel)      ER
   4    LEA                LBA                     ALE                    LBA
  ==== ================== ======================= ====================== ===========
  <BLANKLINE>


See also :doc:`pupils`.


Enrolments
==========

.. class:: Course

    Extends the standard model (:class:`lino_xl.lib.courses.Course`) by adding a
    field :attr:`fee`.

    Also adds a :attr:`ref` field and defines a custom :meth:`__str__`
    method.

    The custom :meth:`__str__` method defines how to textually
    represent a course e.g. in the dropdown list of a combobox or in
    reports. Rules:

    - If :attr:`ref` is given, it is shown, but see also the two
      following cases.

    - If :attr:`name` is given, it is shown (possibly behind the
      :attr:`ref`).

    - If a :attr:`line` (series) is given, it is shown (possibly
      behind the :attr:`ref`).

    - If neither :attr:`ref` nor :attr:`name` nor :attr:`line` are
      given, show a simple "Course #".


    .. attribute:: ref

        An identifying public course number to be used by both
        external and internal partners for easily referring to a given
        course.

    .. attribute:: name

        A short designation for this course. An extension of the
        :attr:`ref`.

    .. attribute:: line

        Pointer to the course series.


    .. attribute:: fee

        The default participation fee to apply for new enrolments.

    .. attribute:: payment_term

        The payment term to use when writing an invoice. If this is
        empty, Lino will use the partner's default payment term.

    .. attribute:: paper_type

        The paper_type to use when writing an invoice. If this is
        empty, Lino will use the site's default paper type.


.. class:: Enrolment

    Adds some fields and inherits from :class:`InvoiceGenerator`.

    .. attribute:: fee

        The participation fee to apply for this enrolment.

    .. attribute:: free_events

        Number of events to add for first invoicing for this
        enrolment.

    .. attribute:: amount

        The total amount to pay for this enrolment. This is
        :attr:`places` * :attr:`fee`.

    .. attribute:: pupil_info

        Show the name and address of the participant.  Overrides
        :attr:`lino_xl.lib.courses.models.Enrolment.pupil_info`
        in order to add (between parentheses after the name) some
        information needed to compute the price.

    .. attribute:: invoicing_info

        A virtual field showing a summary of recent invoicings.

    .. attribute:: payment_info

        A virtual field showing a summary of due accounting movements
        (debts and payments).



>>> rt.show('courses.EnrolmentStates')
======= =========== =========== ============= ============= ==============
 value   name        text        Button text   invoiceable   Uses a place
------- ----------- ----------- ------------- ------------- --------------
 10      requested   Requested                 No            No
 11      trying      Trying                    No            Yes
 20      confirmed   Confirmed                 Yes           Yes
 30      cancelled   Cancelled                 No            No
======= =========== =========== ============= ============= ==============
<BLANKLINE>


>>> rt.show('courses.EnrolmentStates', language="de")
====== =========== =========== ============= ============== =====================
 Wert   name        Text        Button text   Fakturierbar   Besetzt einen Platz
------ ----------- ----------- ------------- -------------- ---------------------
 10     requested   Angefragt                 Nein           Nein
 11     trying      Test                      Nein           Ja
 20     confirmed   Bestätigt                 Ja             Ja
 30     cancelled   Storniert                 Nein           Nein
====== =========== =========== ============= ============== =====================
<BLANKLINE>



The fee of a course
===================

Per course and per enrolment we get a new field :attr:`fee`.

Number of places
================

The :attr:`max_places <lino_xl.lib.courses.Course.max_places>`
(:ddref:`courses.Course.max_places`) field of a *course* contains the
number of available places.

It is a simple integer value and expresses an *absolute* upper limit
which cannot be bypassed. Lino will refuse to confirm an enrolment if
this limit is reached. Here is a user statement about this:

    Also im Prinzip nehmen wir bei den Computerkursen maximal 10 Leute
    an. Da wir aber überall über 12 Geräte verfügen, können wir immer
    im Bedarfsfall um 2 Personen aufstocken. Also bei PC-Kursen setzen
    wir das Maximum immer auf 12. Als Regel gilt dann, dass wir immer nur
    10 annehmen, aber falls unbedingt erforderlich auf 12 gehen
    können.

Every *enrolment* has a field
:attr:`places<lino_xl.lib.courses.models.Enrolment.places>`
(:ddref:`courses.Enrolment.places`) which expresses how many places
this enrolment takes. This is usually 1, but for certain types of
courses, e.g. bus travels, it can happen that one enrolment is for two
or more persons.


Waiting things
==============


The following is waiting for :ticket:`526` before it can work:

>>> # demo_get('robin', 'choices/courses/Courses/city', 'bla', 0)


ActivitiesByLine
================

There are two Yoga courses, i.e. two courses in the Yoga line:

>>> obj = courses.Line.objects.get(pk=10)
>>> obj
Line #10 ('Yoga')

>>> rt.show(rt.models.courses.ActivitiesByLine, obj)
=================== ============== ================= ============= ====================
 Activity            When           Room              Times         Instructor
------------------- -------------- ----------------- ------------- --------------------
 `024C Yoga <…>`__   Every Monday   Conference room   18:00-19:30   Marc Malmendier
 `025C Yoga <…>`__   Every Friday   Conference room   19:00-20:30   Edgard Radermacher
=================== ============== ================= ============= ====================
<BLANKLINE>


>>> ContentType = rt.models.contenttypes.ContentType
>>> json_fields = 'count html_text rows title success no_data_text overridden_column_headers param_values'
>>> kw = dict(fmt='json', limit=10, start=0)
>>> mt = ContentType.objects.get_for_model(courses.Line).pk
>>> demo_get('robin',
...          'api/courses/ActivitiesByLine', json_fields, 3,
...          mt=mt, mk=obj.pk, **kw)


Status report
=============

The status report gives an overview of active courses.

(TODO: demo fixture should avoid negative free places)

>>> rt.show(rt.models.courses.StatusReport)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
~~~~~~~~
Journeys
~~~~~~~~
<BLANKLINE>
========================= ======================= ======= ================== =========== ============= =========== ========
 Activity                  When                    Times   Available places   Confirmed   Free places   Requested   Trying
------------------------- ----------------------- ------- ------------------ ----------- ------------- ----------- --------
 `001 Greece 2014 <…>`__   14/08/2014-20/08/2014                              3                         0           0
 **Total (1 rows)**                                        **0**              **3**       **0**         **0**       **0**
========================= ======================= ======= ================== =========== ============= =========== ========
<BLANKLINE>
~~~~~~~~
Computer
~~~~~~~~
<BLANKLINE>
=========================================== ================= ============= ================== =========== ============= =========== ========
 Activity                                    When              Times         Available places   Confirmed   Free places   Requested   Trying
------------------------------------------- ----------------- ------------- ------------------ ----------- ------------- ----------- --------
 `003 comp (First Steps) <…>`__              Every Monday      13:30-15:00   3                  2           1             0           0
 `004 comp (First Steps) <…>`__              Every Wednesday   17:30-19:00   3                  2           1             1           0
 `005 comp (First Steps) <…>`__              Every Friday      13:30-15:00   3                  2           1             0           0
 `006C WWW (Internet for beginners) <…>`__   Every Monday      13:30-15:00   4                  2           2             1           0
 `007C WWW (Internet for beginners) <…>`__   Every Wednesday   17:30-19:00   4                  2           2             0           0
 `008C WWW (Internet for beginners) <…>`__   Every Friday      13:30-15:00   4                  3           1             0           0
 **Total (6 rows)**                                                          **21**             **13**      **8**         **2**       **0**
=========================================== ================= ============= ================== =========== ============= =========== ========
<BLANKLINE>
~~~~~
Sport
~~~~~
<BLANKLINE>
========================================= ================= ============= ================== =========== ============= =========== ========
 Activity                                  When              Times         Available places   Confirmed   Free places   Requested   Trying
----------------------------------------- ----------------- ------------- ------------------ ----------- ------------- ----------- --------
 `009C BT (Belly dancing) <…>`__           Every Wednesday   19:00-20:00   10                 3           7             0           0
 `010C FG (Functional gymnastics) <…>`__   Every Monday      11:00-12:00   5                  2           3             0           0
 `011C FG (Functional gymnastics) <…>`__   Every Monday      13:30-14:30   5                  2           3             1           0
 `012 Rücken (Swimming) <…>`__             Every Monday      11:00-12:00   20                 3           17            0           0
 `013 Rücken (Swimming) <…>`__             Every Monday      13:30-14:30   20                 3           17            1           0
 `014 Rücken (Swimming) <…>`__             Every Tuesday     11:00-12:00   20                 3           17            0           0
 `015 Rücken (Swimming) <…>`__             Every Tuesday     13:30-14:30   20                 0           20            0           0
 `016 Rücken (Swimming) <…>`__             Every Thursday    11:00-12:00   20                 3           17            0           0
 `017 Rücken (Swimming) <…>`__             Every Thursday    13:30-14:30   20                 3           17            1           0
 `018 SV (Self-defence) <…>`__             Every Friday      18:00-19:00   12                 2           10            0           0
 `019 SV (Self-defence) <…>`__             Every Friday      19:00-20:00   12                 3           9             0           0
 **Total (11 rows)**                                                       **164**            **27**      **137**       **3**       **0**
========================================= ================= ============= ================== =========== ============= =========== ========
<BLANKLINE>
~~~~~~~~~~
Meditation
~~~~~~~~~~
<BLANKLINE>
============================================= ============== ============= ================== =========== ============= =========== ========
 Activity                                      When           Times         Available places   Confirmed   Free places   Requested   Trying
--------------------------------------------- -------------- ------------- ------------------ ----------- ------------- ----------- --------
 `020C GLQ (GuoLin-Qigong) <…>`__              Every Monday   18:00-19:30                      0                         0           0
 `021C GLQ (GuoLin-Qigong) <…>`__              Every Friday   19:00-20:30                      2                         1           0
 `022C MED (Finding your inner peace) <…>`__   Every Monday   18:00-19:30   30                 2           28            0           0
 `023C MED (Finding your inner peace) <…>`__   Every Friday   19:00-20:30   30                 3           27            0           0
 `024C Yoga <…>`__                             Every Monday   18:00-19:30   20                 2           18            0           0
 `025C Yoga <…>`__                             Every Friday   19:00-20:30   20                 2           18            1           0
 **Total (6 rows)**                                                         **100**            **11**      **91**        **2**       **0**
============================================= ============== ============= ================== =========== ============= =========== ========
<BLANKLINE>




Free places
===========

Note the *free places* field, which is not always trivial.  Basicially
it contains `max_places - number of confirmed enrolments`.  But it
also looks at the `end_date` of these enrolments.

List of courses which have a confirmed ended enrolment and a limited
number of places:

>>> qs = courses.Enrolment.objects.filter(end_date__lt=dd.today(),
...     state=courses.EnrolmentStates.confirmed, course__max_places__isnull=False)
>>> for obj in qs:
...     print("{} {} {} {}".format(
...         obj.course.id, obj.course.max_places,
...         obj.course.confirmed,
...         obj.course.get_free_places(dd.today())))
9 10 3 7
19 12 3 9
5 3 2 1
22 30 2 28
25 20 2 18
10 5 2 3
8 4 3 1
3 3 2 1
23 30 3 27
7 4 2 2
18 12 2 10
6 4 2 2
24 20 2 18


In course #5 there are **3** confirmed enrolments, but (on 2015-05-22)
only **2** of them are actually taking a place because one has already
ended.

>>> obj = courses.Course.objects.get(pk=5)
>>> rt.show(courses.EnrolmentsByCourse, obj, column_names="pupil start_date end_date places state")
========================================== ============ ============ ============= ===========
 Participant                                Start date   End date     Places used   State
------------------------------------------ ------------ ------------ ------------- -----------
 Mark Martelaer (ME)                                                  1             Confirmed
 Dorothée Dobbelstein-Demeulenaere (MECS)                22/04/2014   1             Confirmed
 Josefine Leffin (ME)                       02/04/2014                1             Confirmed
 **Total (3 rows)**                                                   **3**
========================================== ============ ============ ============= ===========
<BLANKLINE>



>>> print(obj.max_places)
3
>>> print(obj.get_free_places())
1

Above situation is because we are looking at it on 20150522:

>>> print(dd.today())
2015-05-22

The same request on earlier dates yields different results:

On 20140403 nobody has left yet, all 3 places are taken and therefore
no place is free:

>>> print(obj.get_free_places(i2d(20140403)))
0

On 20140422 is Dorothée's last day, so her place is not yet free:

>>> print(obj.get_free_places(i2d(20140422)))
0

But the next day she is gone and her place available again:

>>> print(obj.get_free_places(i2d(20140423)))
1



Filtering pupils
================

>>> print(rt.models.courses.Pupils.params_layout.main)
course partner_list #aged_from #aged_to gender show_members show_lfv show_ckk show_raviva

There are 36 pupils (21 men and 15 women) in our database:

>>> json_fields = 'count rows html_text title success no_data_text overridden_column_headers param_values'
>>> kwargs = dict(fmt='json', limit=10, start=0)
>>> demo_get('robin', 'api/courses/Pupils', json_fields, 36, **kwargs)

>>> kwargs.update(pv=['', '', 'M', '', '', '', ''])
>>> demo_get('robin', 'api/courses/Pupils', json_fields, 21, **kwargs)

>>> kwargs.update(pv=['', '', 'F', '', '', '', ''])
>>> demo_get('robin', 'api/courses/Pupils', json_fields, 15, **kwargs)


>>> json_fields = 'navinfo disable_delete data id title'
>>> kwargs = dict(fmt='json', an='detail')
>>> demo_get('robin', 'api/courses/Lines/2', json_fields, **kwargs)



.. _voga.presence_sheet:

Presence sheet
==============

The **presence sheet** of a course is a printable document where
course instructors can manually record the presences of the
participants for every event.


Item description
================

.. xfile:: courses/Enrolment/item_description.html

     The template used to fill the items description.


..
  >>> dbhash.check_virgin()
