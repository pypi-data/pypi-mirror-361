.. doctest docs/plugins/cal.rst
.. _book.specs.cal:

================================
``cal`` : Calendar functionality
================================

.. currentmodule:: lino_xl.lib.cal

This page gives developer information about the :mod:`lino_xl.lib.cal` plugin,
which adds general calendar functionality to your :term:`Lino application`.

We assume that you have read the User Guide: :ref:`ug.plugins.cal`.
See also :ref:`xl.specs.holidays`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *

Plugin settings
===============

The ``cal`` plugin adds the following settings, which a :term:`server
administrator` can configure in the :xfile:`settings.py`.

.. data:: calendar_fieldnames

    A sequence of "django query style qualified names" separated by '|' (pipe character)
    which must attribute to the :class:`Event` model.

    :type: typing.Union[str, list]
    :value: []

The ``cal`` plugin is often used together with :mod:`lino_xl.lib.calview`, which
defines :term:`calendar views <calendar view>`.


Calendar entries
================


.. class:: Event

    The Django model that represents a :term:`calendar entry`.

    The internal model name is :class:`Event` for historical reasons. Users see
    it as :term:`calendar entry`:

    >>> print(rt.models.cal.Event._meta.verbose_name)
    Calendar entry

    .. attribute:: start_date

        The starting date of this calendar entry.  May not be empty.

    .. attribute:: end_date

        The ending date of this calendar entry.
        Leave empty for :term:`same-day` entries.

    .. attribute:: start_time

        The starting time.  If this is empty, the entry is considered an
        :term:`all-day` entry.

        Changing this field will change the :attr:`end_time` field as well if
        the entry's :term:`type <calendar entry type>` has a default duration
        (:attr:`EventType.default_duration`).

    .. attribute:: end_time

        The ending time.  If this is before the starting time, and no ending
        date is given, Lino considers the entry to end the day after.

    .. attribute:: summary

         A one-line descriptive text.

    .. attribute:: description

         A longer descriptive text.

    .. attribute:: user

         The responsible user.

    .. attribute:: assigned_to

        Another user who is expected to take responsibility for this
        entry.

        See :attr:`lino.modlib.users.Assignable.assigned_to`.

    .. attribute:: event_type

        The type of this calendar entry.

        Every calendar entry should have this
        field pointing to a given :class:`EventType`, which holds
        extended configurable information about this entry.

    .. attribute:: state

        The state of this entry. The state can change according to
        rules defined by the workflow.

    .. attribute:: owner

        The :term:`event generator` that generated and controls this
        :term:`calendar entry`.

        See :ref:`ug.plugins.cal.automatic_events`.

    .. attribute:: transparent

        Whether this entry should allow other entries at the same time.

    .. attribute:: guests_edited

        Whether the guests list of this event has been modified by an end user.

        Once an end user has modified something in the list of guests, Lino will
        no longer touch the list during :meth:`update_guests`.

    .. attribute:: when_text

         Shows the start date and time of the :term:`calendar entry`.

         See :func:`lino_xl.lib.cal.utils.when_text` for details.

    .. attribute:: when_html

         Shows the date and time of the :term:`calendar entry` with a link that
         opens all entries on that day.

         Deprecated because it is usually irritating. It's better to use
         :attr:`when_text`, and users open the :term:`detail window` as usually
         by double-clicking on the row. And then they have an action on each
         entry for opening :class:`EntriesByDay` if they want.

    .. attribute:: show_conflicting

         A :class:`ShowSlaveTable <lino.core.actions.ShowSlaveTable>`
         button which opens the :class:`ConflictingEvents
         <lino_xl.lib.cal.ConflictingEvents>` table for this event.

    .. attribute:: notify_before

        The multiples of a time unit (:attr:`notify_unit`) before which to send
        a notification to the corresponding user.

    .. attribute:: notify_unit

        The unit of time to compute before sending a notification. Example
        values are: minute, hour, day, week et cetera.

        A pointer to :class:`NotifyBeforeUnits`.

    .. attribute:: notified

        Stores a boolean value as an indication of whether the user has been
        notified or NOT.

    .. method:: update_guests

        Populate or update the list of participants for this calendar
        entry according to the suggestions.

        Calls :meth:`suggest_guests` to instantiate them.

        - No guests are added when loading from dump

        - The entry must be in a state which allows editing the guests

        - Deletes existing guests in state invited that are no longer
          suggested

    .. method:: update_events

        Create or update all other automatic calendar entries of this
        series.

    .. method:: show_today

      Show all calendar entries today.

      See :class:`ShowEntriesByDay`.

    .. method:: get_conflicting_events(self)

        Return a QuerySet of calendar entries that conflict with this one.
        Must work also when called on an unsaved instance.
        May return None to indicate an empty queryset.
        Applications may override this to add specific conditions.

    .. method:: has_conflicting_events(self)

        Whether this entry has any conflicting entries.

        This is roughly equivalent to asking whether
        :meth:`get_conflicting_events()` returns more than 0 events.

        Except when this event's type tolerates more than one events
        at the same time.

    .. method:: suggest_guests(self)

        Yield the list of unsaved :class:`Guest` instances to be added
        to this calendar entry.

        This method is called from :meth:`update_guests`.

    .. method:: get_event_summary(self, ar)

        How this event should be summarized in contexts where possibly
        another user is looking (i.e. currently in invitations of
        guests, or in the extensible calendar panel).

    .. method:: before_ui_save(self, ar)

        Mark the entry as "user modified" by setting a default state.
        This is important because EventGenerators may not modify any
        user-modified Events.

    .. method:: auto_type_changed(self, ar)

        Called when the number of this automatically generated entry
        (:attr:`auto_type` ) has changed.

        The default updates the summary.


    .. method:: _get_calendar(self)

        Returns the :class:`Calendar` which contains this entry, or
        None if no subscription is found.

        The :class:`Calendar` is resolved from the setting given by :data:`calendar_fieldnames`.

        Needed for ext.ensible calendar panel.

        It is advised to never override this method. Instead,
        configure the related :class:`Calendar` using,
        :data:`calendar_fieldnames`.

    When the :mod:`lino_xl.lib.google` is installed. It inserts some other fields
    into this model.
    See: :class:`GoogleCalendarEventSynchronized <lino_xl.lib.google.GoogleCalendarEventSynchronized>`

>>> show_fields(rt.models.cal.Event,
...     'start_date start_time end_date end_time user summary description event_type state')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Start date (start_date) : The starting date of this calendar entry.  May not be empty.
- Start time (start_time) : The starting time.  If this is empty, the entry is considered an
  all-day entry.
- End Date (end_date) : The ending date of this calendar entry.
  Leave empty for same-day entries.
- End Time (end_time) : The ending time.  If this is before the starting time, and no ending
  date is given, Lino considers the entry to end the day after.
- Responsible user (user) : The responsible user.
- Short description (summary) : A one-line descriptive text.
- Description (description) : A longer descriptive text.
- Calendar entry type (event_type) : The type of this calendar entry.
- State (state) : The state of this entry. The state can change according to
  rules defined by the workflow.

Repeaters
=========

.. class:: EntryRepeater

  .. attribute:: repeater

    The :term:`calendar entry` from which this repeater has been created.


Event Notification
==================

Sending an event notification is handled by :func:`get_notification_queryset`
and :func:`send_event_notifications` functions in the cal module.

Below is an example query generated by :func:`get_notification_queryset`.

PS: The three dots (...) at the end of the query is a replacement for
approximately the current time, which changes each time this document is tested
and would otherwise cause doctet to report a failure.

>>> qs = rt.models.cal.get_notification_queryset()
>>> print(qs.query)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
SELECT "cal_event"."id", "cal_event"."start_date", "cal_event"."start_time",
"cal_event"."end_date", "cal_event"."end_time", "cal_event"."modified",
"cal_event"."created", "cal_event"."project_id", "cal_event"."build_time",
"cal_event"."build_method", "cal_event"."user_id", "cal_event"."assigned_to_id",
"cal_event"."owner_type_id", "cal_event"."owner_id", "cal_event"."summary",
"cal_event"."description", "cal_event"."auto_type", "cal_event"."priority",
"cal_event"."event_type_id", "cal_event"."transparent",
"cal_event"."guests_edited", "cal_event"."room_id", "cal_event"."state",
"cal_event"."notify_before", "cal_event"."notify_unit", "cal_event"."notified",
CASE WHEN "cal_event"."start_time" IS NULL THEN 07:00:00 ELSE
"cal_event"."start_time" END AS "start_timed",
(COALESCE("cal_event"."start_date", ) || COALESCE((COALESCE( , ) ||
COALESCE(CASE WHEN "cal_event"."start_time" IS NULL THEN 07:00:00 ELSE
"cal_event"."start_time" END, )), )) AS "start_datetime", CASE WHEN
"cal_event"."notify_unit" = 10 THEN (("cal_event"."notify_before" * 60) *
1000000) WHEN "cal_event"."notify_unit" = 20 THEN ((("cal_event"."notify_before"
* 60) * 1000000) * 60) WHEN "cal_event"."notify_unit" = 30 THEN
(((("cal_event"."notify_before" * 60) * 1000000) * 60) * 24) WHEN
"cal_event"."notify_unit" = 40 THEN ((((("cal_event"."notify_before" * 60) *
1000000) * 60) * 24) * 7) ELSE NULL END AS "notify_before_duration",
strftime(%Y-%m-%d %H:%M:%f, (django_format_dtdelta('-',
(COALESCE("cal_event"."start_date", ) || COALESCE((COALESCE( , ) ||
COALESCE(CASE WHEN "cal_event"."start_time" IS NULL THEN 07:00:00 ELSE
"cal_event"."start_time" END, )), )), CASE WHEN "cal_event"."notify_unit" = 10
THEN (("cal_event"."notify_before" * 60) * 1000000) WHEN
"cal_event"."notify_unit" = 20 THEN ((("cal_event"."notify_before" * 60) *
1000000) * 60) WHEN "cal_event"."notify_unit" = 30 THEN
(((("cal_event"."notify_before" * 60) * 1000000) * 60) * 24) WHEN
"cal_event"."notify_unit" = 40 THEN ((((("cal_event"."notify_before" * 60) *
1000000) * 60) * 24) * 7) ELSE NULL END))) AS "schedule" FROM "cal_event" WHERE
(NOT "cal_event"."notified" AND "cal_event"."notify_before" IS NOT NULL AND
"cal_event"."start_date" IS NOT NULL AND strftime(%Y-%m-%d %H:%M:%f,
(django_format_dtdelta('-', (COALESCE("cal_event"."start_date", ) ||
COALESCE((COALESCE( , ) || COALESCE(CASE WHEN ("cal_event"."start_time" IS NULL)
THEN 07:00:00 ELSE "cal_event"."start_time" END, )), )), CASE WHEN
("cal_event"."notify_unit" = 10) THEN (("cal_event"."notify_before" * 60) *
1000000) WHEN ("cal_event"."notify_unit" = 20) THEN
((("cal_event"."notify_before" * 60) * 1000000) * 60) WHEN
("cal_event"."notify_unit" = 30) THEN (((("cal_event"."notify_before" * 60) *
1000000) * 60) * 24) WHEN ("cal_event"."notify_unit" = 40) THEN
((((("cal_event"."notify_before" * 60) * 1000000) * 60) * 24) * 7) ELSE NULL
END))) <= 2017-02-15 ...)


A dummy event for the demonstration purposes:

>>> import datetime as dt
>>> event = rt.models.cal.Event(summary="Kong's Birthday",
...     start_date=dt.date(2021, 12, 12), start_time=dt.time(0,0),
...     user=rt.models.users.User.objects.get(username='robin'))
>>> event.full_clean()
>>> event.save()

Sending an event notification also stores the message in the database. Below on
the third line of the code we used :func:`send_event_notifications` to simulate
sending of an event notification where we passed the `event` from the previous
code block into an array. For consistency the argument passed onto the
:func:`send_event_notifications` method should be a queryset that is retrieved
from the database using :func:`get_notification_queryset`.

>>> now = dd.now()
>>> rt.models.cal.send_event_notifications([event])
>>> messages = rt.models.notify.Message.objects.filter(created__gte=now)
>>> assert messages.count() == 1

An inspection of the message content:

>>> messages[0].subject
'Upcoming calendar event at 2021-12-12T00:00:00'

>>> messages[0].body
... #doctest: +ELLIPSIS
'<div class="row-fluid">\n<h1>[cal_entry ... Kong\'s Birthday]</h1>\n\n<p style="background-color:#eeeeee; padding:6pt;">\n\n<b>Date :</b> 2021-12-12\n\n\n<br/><b>Time : 00:00:00-None\n\n\n\n\n</p>\n<div>\n\n</div>\n\n</div>'

Cleaning up:

>>> messages[0].delete()
>>> event.delete()


.. function:: event_notification_scheduler

  A hook for :mod:`schedule` that makes :manage:`linod` send out notifications
  for upcoming calendar events every 5 minutes.

.. function:: get_notification_queryset

  Returns notifiable :term:`calendar entries <calendar entry>` computing the
  attributes :attr:`Event.notify_before`, :attr:`Event.notify_unit` and
  :attr:`Event.notified`.

.. function:: send_event_notifications

  Send out notifications to the :term:`site users <site user>` interested in
  this :term:`calendar entry`.


Lifecycle of a calendar entry
=============================

Every calendar entry has a given **state**, which can change according to rules
defined by the application.

The default list of choices for this field contains the following values.

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


.. class:: EntryStates

    The list of possible states of a calendar entry.

.. class:: EntryState

    Every calendar entry state is an instance of this and has some attributes.

    .. attribute:: fill_guests

        Whether the presences of an entry in this state are filled in
        automatically.  If this is True (and if the entry type's
        :attr:`fill_presences` is True as well), the presences cannot be
        modified manually by the used.

        TODO: rename this to fill_presences

    .. attribute:: guest_state

        Force the given guest state for all guests when an entry is
        set to this state and when
        :attr:`EventType.force_guest_states` is True.

    .. attribute:: transparent

        Whether an entry in this state is considered transparent, i.e. dos not
        conflict with other entries at the same moment.

    .. attribute:: fixed

        Whether an entry in this state is considered "stable" when
        differentiating between "stable" and "pending" entries.

        This does not influence editability of the entry.

        See :attr:`EventEvents.stable` and :attr:`EventEvents.pending`.

    .. attribute:: noauto

        Whether switching to this state will clear the entry's :attr:`auto_type`
        field, i.e. it is no longer considered an automatically generated entry,
        IOW it "escapes" from its entry generator.

    .. attribute:: edit_guests

        Old name for :attr:`fill_guests`.

Calendar entry types
====================

Every calendar entry has a field :attr:`Event.event_type` that points to its
:term:`calendar entry type`.


.. class:: EventType

    Django model representing a :term:`calendar entry type`.

    The possible value of the :attr:`Event.event_type` field.

    .. attribute:: default_duration

        An optional default duration for calendar entries of this type.

        If this field is set, Lino will help with entering
        :attr:`Event.end_time` and :attr:`Event.start_date` of an calendar
        entries by changing the :attr:`end_time` of an entry when the
        :attr:`start_date` is changed (and the :attr:`start_time` when the
        :attr:`end_date`)

    .. attribute:: event_label

        Default text for summary of new entries.

    .. attribute:: is_appointment

        Whether entries of this type are considered "appointments" (i.e. whose
        time and place have been agreed upon with other users or external
        parties).

        Certain tables show only entries whose type has the
        `is_appointment` field checked.  See :attr:`show_appointments
        <Entries.show_appointments>`.

    .. attribute:: max_days

        The maximal number of days allowed as duration. 0 means no limit.

        If this is 1, Lino will set :attr:`end_date` to `None`.

        See also :class:`LongEntryChecker`

    .. attribute:: locks_user

        Whether calendar entries of this type make the user
        unavailable for other locking events at the same time.

    .. attribute:: max_conflicting

        How many conflicting events should be tolerated.

    .. attribute:: transparent

        Allow entries of this type to conflict with other events.

    .. attribute:: force_guest_states

        Whether presence states should be forced to those defined by the
        entry state.

        This will have an effect only if the :term:`application developer`
        has defined a mapping from entry state to the guest state by
        setting :attr:`EntryState.guest_state` for at least one entry
        state.

        :ref:`tera` uses this for individual and family therapies
        where they don't want to manage presences of every
        participant.  When an appointment is set to "Took place", Lino
        sets all guests to "Present".  See :doc:`/specs/tera/cal` for a usage
        example.

    .. attribute:: fill_presences

        Whether guests should be automatically filled for calendar entries of
        this type.

    .. attribute:: fill_guests

        Planned name for :attr:`fill_presences`.


.. class:: EventTypes

    The list of entry types defined on this site.

    This is usually filled in the ``std`` demo fixture of the application.

    >>> rt.show(cal.EventTypes)
    =========== =============== ================== ================== ================ ============= ===================== =================
     Reference   Designation     Designation (de)   Designation (fr)   Planner column   Appointment   Automatic presences   Locks all rooms
    ----------- --------------- ------------------ ------------------ ---------------- ------------- --------------------- -----------------
                 Absences        Abwesenheiten      Absences           External         Yes           No                    No
                 First contact   First contact      First contact                       Yes           No                    No
                 Holidays        Feiertage          Jours fériés       External         No            No                    Yes
                 Internal        Intern             Interne            Internal         No            No                    No
                 Lesson          Lesson             Lesson                              Yes           No                    No
                 Meeting         Versammlung        Réunion            External         Yes           No                    No
    =========== =============== ================== ================== ================ ============= ===================== =================
    <BLANKLINE>



Calendars
=========

Calendar entries can be grouped into "calendars".

.. class:: Calendar

    The django model representing a *calendar*.

    .. attribute:: name

        A babel field containing the designation of the calendar.

    .. attribute:: description

        A multi-line description of the calendar.

    .. attribute:: color

        The color to use for entries of this calendar (in
        :mod:`lino_xl.lib.extensible`).

    When the :mod:`lino_xl.lib.google` is installed. It inserts some other fields
    into this model.
    See: :class:`GoogleSynchronized<lino_xl.lib.google.GoogleCalendarSynchronized>`.


.. class:: Calendars

>>> rt.show(cal.Calendars)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
==== ============= ================== ================== ============= =======
 ID   Designation   Designation (de)   Designation (fr)   Description   color
---- ------------- ------------------ ------------------ ------------- -------
 1    General       Allgemein          Général                          1
                                                                        **1**
==== ============= ================== ================== ============= =======
<BLANKLINE>


Note that the default implementation has no "Calendar" field per
calendar entry.  The `Event` model instead has a :meth:`Event._get_calendar` which
internally uses the following settings :data:`calendar_fieldnames`.

You might extend :class:`Event` and the cal plugin as follows::

    # .../cal/models.py
    from lino_xl.lib.cal.models import *
    class Event(Event):

        calendar = dd.ForeignKey('cal.Calendar')

    # .../cal/__init__.py
    ...
    class Plugin(...):
        ...
        calendar_fieldnames = "calendar"
        ...

But in other cases it would create unnecessary complexity to add such
a field. For example in :ref:`welfare` there is one calendar per :term:`site user`
and uses the setting::

    # .../lino_welfare/modlib/cal/__init__.py

    ...
    class Plugin(...):
        ...
        calendar_fieldnames = "assigned_to__calendar|user__calendar"
        ...

Or in :ref:`voga` there is one calendar per Room, and uses the following setting::

    # .../lino_voga/lib/cal/__init__.py

    ...
    class Plugin(...):
        ...
        calendar_fieldnames = "room__calendar"
        ...


.. _specs.cal.automatic_events:

Event generators
================

An :term:`event generator` is something that can generate
automatic calendar entries.  Examples of event generators include

- :doc:`Holidays </specs/holidays>`

- A *course*, *workshop* or *activity* as used by Welfare, Voga and
  Avanti (subclasses of :class:`lino_xl.lib.courses.Course`).

- A reservation of a room in :ref:`voga`
  (:class:`lino_xl.lib.rooms.Reservation`).

- A coaching contract with a client in :ref:`welfare`
  (:class:`lino_welfare.modlib.isip.Contract` and
  :class:`lino_welfare.modlib.jobs.Contract`)

The main effect of the :class:`EventGenerator`
mixin is to add the :class:`UpdateEntries` action.
The generated calendar entries are "controlled" by their generator
(their :attr:`owner <Event.owner>` field points to the generator) and
have a non-empty :attr:`Event.auto_type` field.


The :term:`event generator` itself does not necessarily contain all fields
needed for specifying **which** events should be generated. These fields are
implemented by another model mixin named :class:`RecurrenceSet <lino.modlib.system.RecurrenceSet>`.
A recurrence set is something that specifies which calendar events should get generated.



.. class:: EventGenerator

    Base class for things that generate a series of events.

    See :ref:`specs.cal.automatic_events`.


    .. method:: update_all_guests

        Update the presence lists of all calendar events generated by
        this.

    .. method:: do_update_events

        Create or update the automatic calendar entries controlled by
        this generator.

        This is the :guilabel:` ⚡ ` button.

        See :class:`UpdateEntries`.

    .. method:: get_wanted_auto_events(self, ar)

        Return a tuple of `(wanted, unwanted)`, where
        ``wanted`` is a `list` of calendar entries to be saved,
        and `unwanted` a `list` of events to be deleted.

    .. method:: care_about_conflicts(self, we)

        Whether this event generator should try to resolve conflicts
        for the given calendar entry ``we`` (in :meth:`resolve_conflicts`)

    .. method:: resolve_conflicts(self, we, ar, rset, until)

        Check whether given entry `we` conflicts with other entries
        and move it to a new date if necessary. Returns (a) the
        entry's :attr:`start_date` if there is no conflict, (b) the
        next available alternative date if the entry conflicts with
        other existing entries and should be moved, or (c) None if
        there are conflicts but no alternative date could be found.

        `ar` is the action request who asks for this. `rset` is the
        :class:`lino.modlib.system.RecurrenceSet`.




.. class:: UpdateEntries

    Generate or update the automatic events controlled by this object.

    This action is installed as :attr:`EventGenerator.do_update_events`.

    See also :ref:`ug.plugins.cal.automatic_events`.

.. class:: UpdateEntriesByEvent

    Update all events of this series.

    This is installed as
    :attr:`update_events <Event.update_events>` on :class:`Event`.


Miscellaneous
=============

.. class:: NotifyBeforeUnits

  The list of choices for :attr:`Event.notify_unit`.


Recurrences
============

The **recurrence** expresses how often something is to be repeated.
For example when generating automatic :term:`calendar entries <calendar entry>`,
or when scheduling :term:`background task <background task>`.

Lino supports the following recurrences:

>>> rt.show(cal.Recurrences)
======= ============= ====================
 value   name          text
------- ------------- --------------------
 O       once          once
 N       never         never
 s       secondly      secondly
 m       minutely      minutely
 h       hourly        hourly
 D       daily         daily
 W       weekly        weekly
 M       monthly       monthly
 Y       yearly        yearly
 P       per_weekday   per weekday
 E       easter        Relative to Easter
======= ============= ====================
<BLANKLINE>

Note: ``per_weekday`` exists only for background compatibility. It is an alias
for ``weekly``.

Adding a duration unit

>>> start_date = i2d(20160327)
>>> cal.Recurrences.never.add_duration(start_date, 1)

>>> cal.Recurrences.once.add_duration(start_date, 1)
Traceback (most recent call last):
...
Exception: Invalid DurationUnit once

>>> cal.Recurrences.daily.add_duration(start_date, 1)
datetime.date(2016, 3, 28)

>>> cal.Recurrences.weekly.add_duration(start_date, 1)
datetime.date(2016, 4, 3)

>>> cal.Recurrences.monthly.add_duration(start_date, 1)
datetime.date(2016, 4, 27)

>>> cal.Recurrences.yearly.add_duration(start_date, 1)
datetime.date(2017, 3, 27)

>>> cal.Recurrences.easter.add_duration(start_date, 1)
datetime.date(2017, 4, 16)


Recurrent events
================

This plugin defines a database model :class:`RecurrentEvent` used for example to
generate holidays.  See also :ref:`xl.specs.holidays`.

We are going to use this model for demonstrating some more features (which it
inherits from :class:`lino.modlib.system.RecurrenceSet` and :class:`EventGenerator`).

>>> def demo(every_unit, **kwargs):
...     kwargs.setdefault('start_date', i2d(20160628))
...     kwargs.update(every_unit=cal.Recurrences.get_by_name(every_unit))
...     obj = cal.RecurrentEvent(**kwargs)
...     for lng in 'en', 'de', 'fr':
...         with translation.override(lng):
...             print(obj.weekdays_text)


>>> demo('weekly', tuesday=True)  #doctest: +NORMALIZE_WHITESPACE
Every Tuesday
Jeden Dienstag
Chaque Mardi

>>> demo('weekly', tuesday=True, every=2)
Every second Tuesday
Jeden zweiten Dienstag
Chaque deuxième Mardi

>>> demo('weekly', tuesday=True, every=9)
Every ninth Tuesday
Jeden neunten Dienstag
Chaque neuvième Mardi

>>> demo('monthly', every=2)
Every 2 months
Alle 2 Monate
Tous les 2 mois


>>> rt.show(cal.EventTypes, column_names="id name")
==== =============== ================== ==================
 ID   Designation     Designation (de)   Designation (fr)
---- --------------- ------------------ ------------------
 1    Absences        Abwesenheiten      Absences
 5    First contact   First contact      First contact
 2    Holidays        Feiertage          Jours fériés
 4    Internal        Intern             Interne
 6    Lesson          Lesson             Lesson
 3    Meeting         Versammlung        Réunion
==== =============== ================== ==================
<BLANKLINE>


>>> obj = cal.RecurrentEvent(start_date=i2d(20160628))
>>> isinstance(obj, cal.RecurrenceSet)
True
>>> isinstance(obj, cal.EventGenerator)
True

>>> obj.tuesday = True
>>> obj.every = 2
>>> obj.every_unit = cal.Recurrences.monthly
>>> obj.event_type = cal.EventType.objects.get(id=1)
>>> obj.max_events = 5

>>> ses = rt.login('robin')
>>> wanted, unwanted = obj.get_wanted_auto_events(ses)
>>> for e in wanted:
...     print(dd.fds(e.start_date))
28/06/2016
30/08/2016
01/11/2016
03/01/2017
07/03/2017

Note that above dates are not exactly every 2 months because

- they are only on Tuesdays
- Lino also avoids conflicts with existing events

>>> cal.Event.objects.order_by('start_date')[0]
Event #1 ("New Year's Day (01.01.2013)")

>>> obj.monday = True
>>> obj.wednesday = True
>>> obj.thursday = True
>>> obj.friday = True
>>> obj.saturday = True
>>> obj.sunday = True
>>> obj.start_date=i2d(20120628)
>>> wanted, unwanted = obj.get_wanted_auto_events(ses)
>>> for e in wanted:
...     print(dd.fds(e.start_date))
28/06/2012
28/08/2012
28/10/2012
28/12/2012
28/02/2013



Conflicting events
==================

The demo database contains two appointments on Ash Wednesday and two on Rose
Monday. These conflicting calendar events are visible as checkdata messages (see
:doc:`checkdata`).

>>> chk = checkdata.Checkers.get_by_value('cal.ConflictingEventsChecker')
>>> rt.show(checkdata.MessagesByChecker, chk)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
================= ======================================= ==================================================
 Responsible       Database object                         Message text
----------------- --------------------------------------- --------------------------------------------------
 Robin Rood        `Ash Wednesday (01.03.2017) <…>`__      Event conflicts with 2 other events.
 Robin Rood        `Rosenmontag (27.02.2017) <…>`__        Event conflicts with 2 other events.
 Robin Rood        `Breakfast (27.02.2017 10:20) <…>`__    Event conflicts with Rosenmontag (27.02.2017).
 Romain Raffault   `Réunion (27.02.2017 11:10) <…>`__      Event conflicts with Rosenmontag (27.02.2017).
 Robin Rood        `Seminar (01.03.2017 08:30) <…>`__      Event conflicts with Ash Wednesday (01.03.2017).
 Romain Raffault   `Evaluation (01.03.2017 09:40) <…>`__   Event conflicts with Ash Wednesday (01.03.2017).
================= ======================================= ==================================================
<BLANKLINE>




>>> obj = cal.Event.objects.get(id=123)
>>> print(obj)
Ash Wednesday (01.03.2017)

>>> rt.show(cal.ConflictingEvents, obj)
============ ============ ========== ======== ====== ==================
 Start date   Start time   End Time   Client   Room   Responsible user
------------ ------------ ---------- -------- ------ ------------------
 01/03/2017   08:30:00     09:45:00                   Robin Rood
 01/03/2017   09:40:00     11:10:00                   Romain Raffault
============ ============ ========== ======== ====== ==================
<BLANKLINE>


Calendar entries by day
=======================

The :attr:`Event.show_today` action of a calendar entry  opens a window showing
all calendar entries on the same day as this entry. It is implemented as a
custom action class :class:`ShowEntriesByDay`.

.. class:: ShowEntriesByDay

    Show all calendar events of the same day.

>>> obj = cal.Event.objects.get(id=123)
>>> ar = rt.login("robin", renderer=settings.SITE.kernel.default_renderer)
>>> obj.show_today.run_from_ui(ar)
>>> ar.response  #doctest: +NORMALIZE_WHITESPACE
{'eval_js': 'window.App.runAction({ "action_full_name": "users.AllUsers.grid",
"actorId": "cal.EntriesByDay", "rp": null, "status": { "base_params": {  },
"param_values": { "end_date": "01.03.2017", "event_type": null, "event_typeHidden": null,
"presence_guest": null, "presence_guestHidden": null, "project": null,
"projectHidden": null, "room": null, "roomHidden": null, "start_date": "01.03.2017",
"user": null, "userHidden": null } } })'}


Transparent calendar entries
============================

The entry type "Internal" is marked "transparent".

>>> obj = cal.EventType.objects.get(id=4)
>>> obj
EventType #4 ('Internal')
>>> obj.transparent
True


The guests of a calendar entry
==============================

A calendar entry can have a list of **guests** (also called presences or
participants depending on the context). A guest is the fact that a given person
is *expected to attend* or *has been present* at a given calendar entry.
Depending on the context the guests of a calendar entry may be labelled
"guests", "participants", "presences", ...


.. class:: Guest

    The Django model representing a guest.

    .. attribute:: event

        The calendar event to which this presence applies.

    .. attribute:: partner

        The partner to which this presence applies.

    .. attribute:: role

        The role of this partner in this presence.

    .. attribute:: state

        The state of this presence.  See :class:`GuestStates`.


    The following three fields are injected by the
    :mod:`reception <lino_xl.lib.reception>` plugin:

    .. attribute:: waiting_since

        Time when the visitor arrived (checked in).

    .. attribute:: busy_since

        Time when the visitor was received by agent.

    .. attribute:: gone_since

        Time when the visitor left (checked out).


Every participant of a calendar entry can have a "role". For example
in a class meeting you might want to differentiate between the teacher
and the pupils.

.. class:: GuestRole

    The role of a guest expresses what the partner is going to do there.

.. class:: GuestRoles

    Global table of guest roles.

.. class:: GuestState

    The current state of a guest.

.. class:: GuestStates

    Global choicelist of possible guest states.

    Possible values for the state of a participation. The list of
    choices for the :attr:`Guest.state` field.

    The actual content can be redefined by other plugins, e.g.
    :mod:`lino_xl.lib.reception`.


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


.. class:: UpdateGuests

    See :meth:`Event.update_guests`.


.. class:: UpdateAllGuests

    See :meth:`EventGenerator.update_all_guests`.


Presence lists
==============

To introduce the problem:

- :manage:`runserver` in :mod:`lino_book.projects.avanti1` and sign in as robin.
- create a calendar entry, leave it in draft mode
- Note that you cannot manually enter a guest in the presences list.

This is a situation where we want Lino to automatically keep the list of guests
synchronized with the "suggested guests" for this meeting.  For example in
:ref:`avanti` when we have a course with participants (enrolments), and we have
generated a series of calendar entries having their suggested guests filled
already, and now one participant cancels their enrolment.  We want Lino to
update all participants of meetings that are still in draft state.  The issue is
that Lino doesn't correctly differentiate between those two situations:

- manually enter and manage the list of guests

- fill guests automatically and keep it synchronized with the guests suggested
  by the entry generator.

Lino should not let me manually create a guest when the entry is in "fill
guests" mode.

The :attr:`Event.update_guests` action is always called in the
:meth:`Event.after_ui_save` method.  That's okay, but in our case the action
obviously comes to the conclusion that we do want to update our guests. More
precisely the event state obviously has :attr:`EntryState.edit_guests` set to
False, and the entry type has :attr:`fill_presences` set to True.  The solution
is to simply set

- The :meth:`Event.can_edit_guests_manually` method which encapsulates this
  condition.
- That method is now also used to decide whether the presences lists can be
  modified manually.

Note the difference between "guest" and "presence". The model name is currently
still :class:`cal.Guest`, but this should be renamed to :class:`cal.Presence`.
Because the "guest" is actually the field of a presence which points to the
person who is the guest.


Remote calendars
================

A **remote calendar** is a set of calendar entries stored on another server.
Lino periodically synchronized the local data from the remote server, and local
modifications will be sent back to the remote calendar.

The feature is not currently being used anywhere.

See also :mod:`lino_xl.lib.cal.management.commands.watch_calendars`.


.. class:: RemoteCalendar

    Django model for representing a remote calendar.


Rooms
=====

A **room** is location where calendar entries can happen.  For a given room you
can see the :class:`EntriesByRoom` that happened (or will happen) there.  A
room has a multilingual name which can be used in printouts.

Applications might change the user label for this model e.g. to "Team" (as done
in :ref:`presto`) if the application is not interested in physical rooms.



.. class:: Room

    Django model for representing a room.

    .. attribute:: name

        The designation of the room. This is not required to be unique.

    .. attribute:: display_color

        The color to use when displaying entries in this room in the calendar
        view.

        See :class:`lino.modlib.system.DisplayColors`.


.. class:: Rooms

    Base class for all list of rooms.


.. class:: AllRooms

    Show a list of all rooms.


.. class:: RoomDetail

    The detail layout for :class:`Rooms` and subclasses.

Subscriptions
=============

A **suscription** is when a user subscribes to a calendar.
It corresponds to what the extensible CalendarPanel calls "Calendars"

.. class:: BaseSubscription

    :user: points to the author (recipient) of this subscription

    .. attribute:: calendar

        Pointer to the :class:`Calendar` for the :class:`BaseSubscription`.

    .. attribute:: is_hidden

        Whether this subscription should initially be displayed as a hidden calendar.

.. class:: Subscription

    Django model for representing a subscription.

    A subclass of :class:`BaseSubscription`

.. class:: Subscriptions
.. class:: SubscriptionsByUser
.. class:: SubscriptionsByCalendar

Tasks
=====

A task is when a user plans to do something (and optionally wants to get
reminded about it).


.. class:: Task

    Django model for representing a subscription.

    .. attribute:: priority

        How urgent this task is.

        Choicelist field pointing to :class:`lino_xl.lib.xl.Priorities`.

    .. attribute:: state

        The state of this Task. one of :class:`TaskStates`.

.. class:: TaskStates

    Possible values for the state of a :class:`Task`. The list of
    choices for the :attr:`Task.state` field.


.. class:: Tasks

    Global table of all tasks for all users.

.. class:: TasksByUser

    Shows the list of tasks for this user.

.. class:: MyTasks

    Shows my tasks whose start date is today or in the future.

Recurrent calendar entries
==========================

.. class:: EventPolicy

    Django model used to store a :term:`recurrency policy`.

    .. attribute:: event_type

        Generated calendar entries will have this type.

.. class:: EventPolicies

    Global table of all possible recurrency policies.

.. class:: RecurrentEvent

    Django model used to store a :term:`recurrent event`.

    .. attribute:: name

        See :attr:`lino.utils.mldbc.mixins.BabelNamed.name`.

    .. attribute:: every_unit

        Inherited from :attr:`RecurrenceSet.every_unit
        <lino.modlib.system.RecurrenceSet.every_unit>`.

    .. attribute:: event_type


    .. attribute:: description

    .. method:: care_about_conflicts(self, we)

        Recurrent events don't care about conflicts. A holiday won't move
        just because some other event has been created before on that date.

.. class:: RecurrentEvents

    The list of all recurrent events (:class:`RecurrentEvent`).


Miscellaneous
==============

.. class:: Events

    Table which shows all calendar events.

    Filter parameters:

    .. attribute:: show_appointments

        Whether only *appointments* should be shown.  "Yes" means only
        appointments, "No" means no appointments and leaving it to
        blank shows both types of events.

        An appointment is an event whose *event type* has
        :attr:`appointment <EventType.appointment>` checked.

    .. attribute:: presence_guest

        Show only entries that have a presence for the specified guest.

    .. attribute:: project

        Show only entries assigned to this project, where project is defined by
        :attr:`lino.core.site.Site.project_model`.

    .. attribute:: assigned_to

        Show only entries assigned to this user.

    .. attribute:: observed_event

    .. attribute:: event_type

        Show only entries having this type.

    .. attribute:: state

        Show only entries having this state.

    .. attribute:: user

        Show only entries having this user as author.

.. class:: ConflictingEvents

    Shows events conflicting with this one (the master).

.. class:: EntriesByDay

    This table is usually labelled "Appointments today". It has no
    "date" column because it shows events of a given date.It is ordred
    with increasing times.

    The default filter parameters are set to show only *appointments*.

.. class:: EntriesByRoom

    Displays the calendar entries at a given :class:`Room`.

.. class:: EntriesByController

    Shows the calendar entries controlled by this database object.

    If the master is an :class:`EventGenerator
    <lino_xl.lib.cal.EventGenerator>`, then this includes
    especially the entries which were automatically generated.

.. class:: EntriesByProject

.. class:: OneEvent

    Show a single calendar event.

.. class:: MyEntries

    Shows the :term:`appointments <appointment>` for which I am responsible.

    This :term:`data table` shows today's and all future appointments of the
    requesting user.  The default filter parameters are set to show only
    :term:`appointments <appointment>` (:attr:`show_appointments` is set to
    "Yes").

.. class:: MyEntriesToday

    Like :class:`MyEntries`, but only today.

.. class:: MyAssignedEvents

    Shows the calendar entries that are *assigned* to me.

    That is, having :attr:`Event.assigned_to` field refers to the requesting
    user.

    This :term:`data table` also generates a :term:`welcome message` "X events
    have been assigned to you" when it is not empty.

.. class:: OverdueAppointments

    Shows **overdue appointments**, i.e. appointments that happened before today
    and are still in a nonstable state.

    :attr:`show_appointments` is set to "Yes", :attr:`observed_event`
    is set to "Unstable", :attr:`end_date` is set to today.

.. class:: MyOverdueAppointments

    Like OverdueAppointments, but only for myself.


.. class:: MyUnconfirmedAppointments

    Shows my appointments in the near future which are in suggested or
    draft state.

    Appointments before today are not shown.  The parameters
    :attr:`end_date` and :attr:`start_date` can manually be modified
    in the parameters panel.

    The state filter (draft or suggested) cannot be removed.


.. class:: Guests

    The default table of presences.

.. class:: GuestsByEvent

.. class:: GuestsByRole
.. class:: MyPresences

    Shows all my presences in calendar events, independently of their
    state.

.. class:: MyPendingPresences

    Received invitations waiting for my feedback (accept or reject).


.. class:: GuestsByPartner

    Show the calendar entries having this partner as a guest.

    This might get deprecated some day.  You probably prefer :class:`EntriesByGuest`.


.. class:: EntriesByGuest

    Show the calendar entries having this partner as a guest.

    Similar to :class:`GuestsByPartner`, but EntriesByGuest can be used to
    create a new calendar entry.  It also makes sure that the new entry has at
    least one guest, namely the partner who is the master. Because otherwise,
    if the user creates an entry and forgets to manually add our master as a
    guest, they would not see the new entry.



.. class:: Reservation

    Base class for :class:`lino_xl.lib.rooms.models.Booking` and
    :class:`lino.modlib.courses.models.Course`.

    Inherits from both :class:`EventGenerator` and :class:`lino.modlib.system.RecurrenceSet`.

    .. attribute:: room

    .. attribute:: max_date

        Don't generate calendar entries beyond this date.

Miscellaneous
=============

.. class:: AccessClasses

    The sitewide list of access classes.

.. class:: Component

    Model mixin inherited by both :class:`Event` and :class:`Task`.

    .. attribute:: auto_type

        Contains the sequence number if this is an automatically
        generated component. Otherwise this field is empty.

        Automatically generated components behave differently at
        certain levels.


Plugin configuration
====================

See :class:`Plugin`.


Data checkers
=============

.. class:: ConflictingEventsChecker

    Check whether this entry conflicts with other events.

.. class:: ObsoleteEventTypeChecker

    Check whether the type of this calendar entry should be updated.

    This can happen when the configuration has changed and there are
    automatic entries which had been generated using the old
    configuration.

.. class:: LongEntryChecker

    Check for entries which last longer than the maximum number of
    days allowed by their type.

.. class:: EventGuestChecker

    Check for calendar entries without participants.

    :message:`No participants although N suggestions exist.` --
    This is probably due to some problem in the past, so we repair
    this by adding the suggested guests.





.. function:: check_subscription(user, calendar)

    Check whether the given subscription exists. If not, create it.


Default duration and start time
===============================

Note the difference between a DurationField and a TimeField:

>>> fld = cal.EventType._meta.get_field('default_duration')
>>> fld.__class__
<class 'lino.core.fields.DurationField'>
>>> fld.to_python("1:00")
Duration('1:00')

>>> fld = cal.Event._meta.get_field('start_time')
>>> fld.__class__
<class 'lino.core.fields.TimeField'>
>>> fld.to_python("1:00")
datetime.time(1, 0)

>>> et = cal.EventType.objects.get(planner_column=cal.PlannerColumns.internal)
>>> et.default_duration
Duration('0:30')

So when we create an entry which starts at 8:00, Lino will automaticallt set
end_time to 8:30

>>> entry = cal.Event(start_date=dd.today(), start_time="8:00", event_type=et)
>>> entry.full_clean()
>>> entry.end_time
datetime.time(8, 30)

It works also across midnight:

>>> entry = cal.Event(start_date=dd.today(), start_time="23:55", event_type=et)
>>> entry.full_clean()
>>> entry.start_time
datetime.time(23, 55)
>>> entry.end_time
datetime.time(0, 25)
>>> entry.start_date
datetime.date(2017, 2, 15)
>>> entry.end_date


User roles
==========

Besides the user roles defined in :mod:`lino.modlib.office` this plugins also
defines two specific roles.

.. class:: CalendarReader

    Can read public calendar entries. This is a kind of minimal
    calendar functionality that can be given to anonymous users,
    as done e.g. by :ref:`vilma`.

.. class:: GuestOperator

    Can see presences and guests of a calendar entry.

.. class:: GuestUser

    Can manage :term:`presences <presence>`.

    Usage example in :ref:`voga` where users of type `pupil` cannot create or
    edit calendar entries, but can manage their participation in existing
    entries.

Most calendar functionality requires
:class:`lino.modlib.office.OfficeUser`



Positions
=========

The :attr:`lino.modlib.system.RecurrenceSet.positions` field allows to specify rules like "every
last Friday of the month".

If given, it must be a space-separated list of positive or negative integers.
Each given integer *N* means the *N*\ th occurrence inside the frequency period.

The positions field makes sense only when frequency
(:attr:`lino.modlib.system.RecurrenceSet.every_unit`) is yearly, monthly, weekly or daily. It is
silently ignored with other frequencies. When this field is set, the value of
:attr:`lino.modlib.system.RecurrenceSet.every` is ignored.

Lino uses `dateutil.rrule
<https://dateutil.readthedocs.io/en/stable/rrule.html>`_
when positions are used, so the edge cases described there might apply.

The following examples use a utility function:

>>> settings.SITE.verbose_client_info_message = True
>>> def show(obj, today):
...     obj.name = "test"
...     obj.full_clean()
...     for lng in ('en', 'de', 'fr'):
...         with translation.override(lng):
...             print(obj.weekdays_text)
...     ses = rt.login("robin")
...     for i in range(5):
...         today = obj.get_next_suggested_date(today, ses.logger)
...         if today is None:
...             break
...         print(dd.fdf(today))
...     if len(ses.response):
...         print(ses.response)

Every last Friday of the month:

>>> obj = cal.RecurrentEvent()
>>> obj.friday = True
>>> obj.positions = "-1"
>>> obj.every_unit = cal.Recurrences.monthly
>>> show(obj, i2d(20191001))
Every last Friday of the month
Jeden letzten Freitag des Monats
Chaque dernier Vendredi du mois
Friday, 25 October 2019
Friday, 29 November 2019
Friday, 27 December 2019
Friday, 31 January 2020
Friday, 28 February 2020

Every last working day of the month:

>>> obj.monday = True
>>> obj.tuesday = True
>>> obj.wednesday = True
>>> obj.thursday = True
>>> show(obj, i2d(20191001))
Every last working day of the month
Jeden letzten Arbeitstag des Monats
Chaque dernier jour ouvrable du mois
Thursday, 31 October 2019
Friday, 29 November 2019
Tuesday, 31 December 2019
Friday, 31 January 2020
Friday, 28 February 2020

The first and third Wednesday of every month:

>>> obj = cal.RecurrentEvent()
>>> obj.wednesday = True
>>> obj.positions = "1 3"
>>> obj.every_unit = cal.Recurrences.monthly
>>> show(obj, i2d(20191001))
Every first and third Wednesday of the month
Jeden ersten und dritten Mittwoch des Monats
Chaque premier et troisième Mercredi du mois
Wednesday, 2 October 2019
Wednesday, 16 October 2019
Wednesday, 6 November 2019
Wednesday, 20 November 2019
Wednesday, 4 December 2019

>>> obj = cal.RecurrentEvent()
>>> obj.friday = True
>>> obj.monday = True
>>> obj.positions = "2"
>>> obj.every_unit = cal.Recurrences.monthly
>>> show(obj, i2d(20191213))
Every second Monday and Friday of the month
Jeden zweiten Montag und Freitag des Monats
Chaque deuxième Lundi et Vendredi du mois
Monday, 6 January 2020
Friday, 7 February 2020
Friday, 6 March 2020
Monday, 6 April 2020
Monday, 4 May 2020

>>> obj.positions = "-2"
>>> obj.monday = False
>>> show(obj, i2d(20191213))
Every second last Friday of the month
Jeden zweitletzten Freitag des Monats
Chaque avant-dernier Vendredi du mois
Friday, 20 December 2019
Friday, 24 January 2020
Friday, 21 February 2020
Friday, 20 March 2020
Friday, 17 April 2020

>>> obj = cal.RecurrentEvent()
>>> obj.positions = "2"
>>> obj.every_unit = cal.Recurrences.once
>>> show(obj, i2d(20191213))
On Wednesday, 15 February 2017
Am Mittwoch, 15. Februar 2017
Le mercredi 15 février 2017

Every 3 years (with Easter):

>>> obj = cal.RecurrentEvent()
>>> obj.every_unit = cal.Recurrences.easter
>>> obj.positions = "2"  # silently ignored
>>> obj.every = 3
>>> show(obj, i2d(20191213))
Every 3 years (with Easter)
Alle 3 Jahre (mit Ostern)
Tous les 3 ans (avec Pâques)
Friday, 9 December 2022
Friday, 12 December 2025
Friday, 8 December 2028
Friday, 5 December 2031
Friday, 1 December 2034

A rule that yields no date at all

>>> obj = cal.RecurrentEvent()
>>> obj.every_unit = cal.Recurrences.daily
>>> obj.positions = "7"
>>> show(obj, i2d(20191213))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
Every day
Jeden Tag
Chaque jour

For example, a bysetpos of -1 if combined with a MONTHLY frequency, and a
byweekday of (MO, TU, WE, TH, FR), will result in the last work day of every
month.

Utilities
=========

.. currentmodule:: lino_xl.lib.cal.utils

>>> import datetime
>>> from lino_xl.lib.cal.utils import dt2kw, when_text, parse_rrule


:func:`dt2kw` examples:

>>> dt = datetime.datetime(2013, 12, 25, 17, 15, 0)
>>> dt2kw(dt,'foo') == {'foo_date': datetime.date(2013, 12, 25), 'foo_time': datetime.time(17, 15)}
True


:func:`when_text`  examples:

>>> print(when_text(datetime.date(2013,12,25)))
Wed 25/12/2013

>>> print(when_text(
...     datetime.date(2013,12,25), datetime.time(17,15,00)))
Wed 25/12/2013 (17:15)

>>> print(when_text(None))
<BLANKLINE>


Recurrence rules
================

.. glossary::

  recurrence rule

    A text that describes a "recurrence rule" according to the syntax defined in
    `RFC 5545 <https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10>`__.

Examples for the :func:`parse_rrule` function.

Every last Friday of the month:

>>> parse_rrule("RRULE:FREQ=MONTHLY;BYDAY=-1FR")
(<system.Recurrences.monthly:M>, 1, None, {'BYDAY': [(-1, 'FR')]})

Every year ((from start date):

>>> parse_rrule("RRULE:FREQ=YEARLY")
(<system.Recurrences.yearly:Y>, 1, None, {})
