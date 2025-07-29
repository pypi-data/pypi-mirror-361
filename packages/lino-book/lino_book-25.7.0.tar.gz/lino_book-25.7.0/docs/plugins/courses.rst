.. doctest docs/plugins/courses.rst
.. _specs.courses:

==============================
``courses`` : Managing courses
==============================

.. currentmodule:: lino_xl.lib.courses

The :mod:`courses <lino_xl.lib.courses>` plugin adds functionality for managing
"activities".

The internal name "courses" is for historic reasons.  We should one day rename
the plugin to "activities". We didn't yet do this because we are so used with
the old name and because a rename will require extra attention with database
migrations.

See also :ref:`ug.plugins.courses`.
See also
:doc:`/specs/voga/courses`,
:doc:`/specs/avanti/courses`,
:doc:`/specs/tera/courses`
and :ref:`welfare`.



.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.min9.settings')
>>> from lino.api.doctest import *

Plugin configuration
====================

The :term:`activity leader` can be any database model. This is configured in
:attr:`Plugin.teacher_model`, for which the default value is :class:`contacts.Person
<lino_xl.lib.contacts.Person>`.

The :term:`participants of an activity <activity participant>` can be any
database model. This is configured in :attr:`Plugin.pupil_model`, for which the
default value is :class:`contacts.Person <lino_xl.lib.contacts.Person>`.


The ``Course`` model
====================

.. class:: Course

    Django database model to represent an :term:`activity`.

    Database fields:

    .. attribute:: max_date

        Don't generate meeting having their start date beyond this
        date.

    .. attribute:: enrolments_until

        Until when new enrolments are accepted.

    .. attribute:: max_places

        Available places. The maximum number of participants to allow
        in this activity.

    .. attribute:: free_places

        Number of free places.

    .. attribute:: requested

        Number of requested places.

    .. attribute:: trying

        Number of trying places.

    .. attribute:: confirmed

        Number of confirmed places.

    Inherited database fields:
    :attr:`RecurrenceSet.start_date <lino.modlib.system.RecurrenceSet.start_date>`
    :attr:`RecurrenceSet. <lino.modlib.system.RecurrenceSet.end_date>`
    :attr:`RecurrenceSet.positions <lino.modlib.system.RecurrenceSet.positions>`
    :attr:`RecurrenceSet.every <lino.modlib.system.RecurrenceSet.every>`
    :attr:`RecurrenceSet.every_unit <lino.modlib.system.RecurrenceSet.every_unit>`

    .. method:: get_detail_action(self, ar)

      Custom :meth:`get_detail_action
      <lino.core.model.Model.get_detail_action>` because the
      detail_layout to use depends on the
      :term:`activity layout`, which is given by the
      :attr:`Line.course_area` field of the activity's line.





.. class:: Courses

    Base table for all activities.

    Filter parameters:

    .. attribute:: show_exposed

        Whether to show or to hide courses in an exposed state.

        That is, all courses in a state that has
        :attr:`CourseState.is_exposed` set to True.

        This parameter is ignored if the :attr:`state` parameter is also
        specified.

    .. attribute:: state



.. class:: MyActivities

    Show the courses authored by me (i.e. where I am the responsible
    manager).  Compare :class:`MyCoursesGiven`.

.. class:: MyCoursesGiven

    Show the courses given by me (i.e. where I am the teacher).
    Compare :class:`MyActivities`.

    This requires the :attr:`partner` field in my user settings to
    point to me as a teacher.

    For users whose :attr:`partner` field is empty, this list shows
    all courses without teacher.

.. class:: ActivitiesByLine

    Show the courses per course line.

.. class:: ActivitiesByTopic

    Shows the courses of a given topic.


The ``Enrolment`` model
=======================

.. class:: Enrolment

    Django database model to represent an :term:`activity enrolment`.

    .. attribute:: course_area
    .. attribute:: course
    .. attribute:: pupil
    .. attribute:: request_date
    .. attribute:: start_date
    .. attribute:: end_date
    .. attribute:: state

        One of :class:`lino_xl.lib.courses.EnrolmentStates`.

    .. attribute:: places
    .. attribute:: option
    .. attribute:: remark
    .. attribute:: confirmation_details
    .. attribute:: pupil_info

        Virtual HtmlBox field showing the name and address of the
        participant.

.. class:: Enrolments

    Base class for all tables that show :class:`Enrolment`.

.. class:: AllEnrolments

    Show global list of all enrolments.

.. class:: PendingRequestedEnrolments

    Show all requested enrolments.

.. class:: PendingConfirmedEnrolments

    Show all confirmed enrolments.

.. class:: EnrolmentsByPupil

    Show all enrolments of a given pupil.

.. class:: EnrolmentsByCourse

    Show the enrolments of a course.



Enrolment workflow
==================

The state of an enrolment can be one of the following:

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


.. class:: EnrolmentStates

    The list of possible states of an enrolment.

    The default implementation has the following values:

    .. attribute:: requested
    .. attribute:: confirmed
    .. attribute:: cancelled

        The enrolment was cancelled before it even started.

    .. attribute:: ended

        The enrolment was was successfully ended.

    .. attribute:: abandoned

        The enrolment was abandoned.




The ``Slot`` model
==================

.. class:: Slot

The ``Line`` model
==================

.. class:: Line

    Django database model to represent an :term:`activity line`.

    .. attribute:: name

        The designation of this activity line as seen by the user
        e.g. when selecting the line.

        One field for every :attr:`language <lino.core.site.Site.language>`.

    .. attribute:: excerpt_title

        The text to print as title in enrolments.

        See also
        :attr:`lino_xl.lib.excerpts.mixins.ExcerptTitle.excerpt_title`.

    .. attribute:: body_template

        The body template to use when printing an activity of this
        line.  Leave empty to use the site's default (defined by
        `body_template` on the
        :class:`lino_xl.lib.excerpts.models.ExcerptType` for
        :class:`Course`)

    .. attribute:: course_area

        Pointer to :class:`ActivityLayouts`.  This is used only when an
        application defines several variants of
        :class:`EnrolmentsByPupil`.



Activity layouts
================

The :class:`ActivityLayouts` choicelist is where the :term:`application
developer` can define the available :term:`activity layouts <activity layout>`.

The default configuration contains only one choice:

>>> rt.show(courses.ActivityLayouts)
======= ========= ============ ============================
 value   name      text         Table
------- --------- ------------ ----------------------------
 C       default   Activities   courses.ActivitiesByLayout
======= ========= ============ ============================
<BLANKLINE>

Usage examples see :doc:`/specs/voga/courses` and :doc:`/specs/tera/courses`.

The layout of an activity can customize how data fields and related data are to
be laid out on screen. This is done by defining a subclass of
:class:`ActivitiesByLayout` and referring to it in the
:attr:`ActivityLayout.courses_table`.


.. class:: ActivityLayouts

    The global choicelist of :term:`activity layouts <activity layout>`.  Every
    choice is an instance of :class:`ActivityLayout`.

.. class:: ActivityLayout

    .. attribute:: text

      The translatable designation used as menu label.

    .. attribute:: courses_table

      Which table to use for showing activities having this layout.


The state of an activity
========================

>>> rt.show(courses.CourseStates)
======= ========== ========== ========= ========== ============= =================
 value   name       text       Exposed   Editable   Invoiceable   Update calendar
------- ---------- ---------- --------- ---------- ------------- -----------------
 10      draft      Draft      Yes       Yes        No            No
 20      active     Started    Yes       No         Yes           No
 30      inactive   Inactive   No        No         No            No
 40      closed     Closed     No        No         No            No
======= ========== ========== ========= ========== ============= =================
<BLANKLINE>


.. class:: CourseStates

   .. attribute:: draft
   .. attribute:: active
   .. attribute:: inactive
   .. attribute:: closed


Every course state has itself some additional attributes that are used
to group them at certain places.

.. class:: CourseState

   .. attribute:: is_editable
   .. attribute:: is_exposed
   .. attribute:: is_invoiceable
   .. attribute:: auto_update_calendar

For example you can retrieve a list of course states that are to be
considered "exposed" (:attr:`Courses.show_exposed`):

>>> courses.CourseStates.filter(is_exposed=True)
[<courses.CourseStates.draft:10>, <courses.CourseStates.active:20>]

>>> courses.CourseStates.filter(is_exposed=False)
[<courses.CourseStates.inactive:30>, <courses.CourseStates.closed:40>]

As an application developer you can redefine the items of
:class:`CourseStates` in order to adapt it to the needs of your
application.

TODO: Write a tutorial about redefining choicelists.


Actions
=======

.. class:: ConfirmAllEnrolments




Plugin configuration
====================

.. class:: Plugin

    .. attribute:: teacher_model = 'contacts.Person'
    .. attribute:: pupil_model = 'contacts.Person'

    .. attribute:: pupil_name_fields = "pupil__name"

    The value to use as :attr:`quick_search_fields
    <lino.core.model.Model.quick_search_fields>` for
    :class:`Enrolment`.

    Note that this remains a text string while
    :attr:`quick_search_fields
    <lino.core.model.Model.quick_search_fields>` is resolved into a
    tuple of data elements at site startup.

Presence sheet
==============

The **presence sheet** of a course is a printable document
For example :ref:`voga.presence_sheet`.


.. xfile:: presence_sheet.weasy.html

    The template used for printing a presence sheet of an activity
    (both versions pdf and html)
