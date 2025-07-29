.. doctest docs/specs/voga/voga3.rst
.. _voga.specs.voga3:

==================================
``voga3`` : A Lino Voga in Estonia
==================================

The :mod:`lino_book.projects.voga3` demo project uses :ref:`voga` for managing a
dance school.  The dance school organizes group trainings and individual
trainings. Teachers are either engaged employees or freelancers paid per hour by
the participants.  Scheduling individual lessons is a very dynamic process where
the participants decide individually whether the can come to a suggested
:term:`appointment`, often very short-term.


.. contents::
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.voga3.settings')
>>> from lino.api.doctest import *

>>> dd.demo_date()
... #doctest: +ELLIPSIS +REPORT_UDIFF
datetime.date(2020, 5, 22)


>>> mary = users.User.objects.get(username="mary")
>>> print(mary.user_type)
400 (Pupil)
>>> print(courses.Pupil.objects.get(id=mary.partner.id))
Mary Morgan (N)


>>> course = rt.models.courses.Course.objects.get(id=11)
>>> print(course)
011C FG (Functional gymnastics)
>>> event = course.get_existing_auto_events().first()
>>> print(list(course.suggest_cal_guests(event)))
[Guest(event=574,partner=54,role=1,state=<cal.GuestStates.invited:10>), Guest(event=574,partner=56,role=1,state=<cal.GuestStates.invited:10>)]


>>> rt.models.cal.Event.get_default_table()
lino_xl.lib.cal.ui.Events
