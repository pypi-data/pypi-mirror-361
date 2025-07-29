.. doctest docs/specs/working.rst
.. include:: /shared/include/defs.rst
.. _specs.clocking:
.. _noi.specs.clocking:

================================
``working`` : Work time tracking
================================

.. currentmodule:: lino_xl.lib.working

The :mod:`lino_xl.lib.working` adds functionality for registering work time and
generating service reports.

See also the end-user docs :ref:`ug.plugins.working`.


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

The demo project is on fictive demo date **May 22, 2015**:

>>> dd.today()
datetime.date(2015, 5, 22)


Plugin settings
===============

.. setting:: working.reports_master

    The model used as the master for service reports.

    This model must have three fields company, start_date and end_date.

    Default value is 'trading.VatProductInvoice'.


.. setting:: working.default_reporting_type

  The reporting type to use when no explicit reporting type has been selected
  for a session.

.. setting:: working.ticket_model

The :term:`database model` to be used as the "ticket".

This must be no longer a subclass of
:class:`lino_xl.lib.working.mixins.Workable`, it must just have a
method `on_worked`.


The :attr:`ticket_model <Plugin.ticket_model>` defines what a ticket actually
is.  In :ref:`noi` this points to :class:`tickets.Ticket
<lino_xl.lib.tickets.Ticket>`. It can be any model that implements
:class:`Workable`.

Working sessions
================

A :term:`site manager` can see all sessions of the demo project:

>>> rt.show(working.Sessions, limit=15)
... #doctest: +REPORT_UDIFF
=================================== ========= ============ ============ ============ ========== ============ =============================== ========== ==================== ============= =====================
 Ticket                              Worker    Start date   Start time   End Date     End Time   Break Time   Summary                         Duration   Duration (decimal)   Ticket #      Subscription
----------------------------------- --------- ------------ ------------ ------------ ---------- ------------ ------------------------------- ---------- -------------------- ------------- ---------------------
 #57 (Irritating message when bar)   Jean      22/05/2015   09:00:00                                          fiddle with get_auth()                                          `#57 <…>`__
 #63 (Bars have no foo)              Jean      22/05/2015   09:00:00                             0:10         jitsi meeting claire and paul                                   `#63 <…>`__
 #59 (Misc optimizations in Baz)     Luc       22/05/2015   09:00:00                             0:10         commit and push                                                 `#59 <…>`__   SLA 5/2014 (dde)
 #65 (Foo never bars)                Luc       22/05/2015   09:00:00                                          empty recycle bin                                               `#65 <…>`__   SLA 4/2014 (bcc)
 #45 (Irritating message when bar)   Mathieu   22/05/2015   09:00:00                             0:10         meeting with john                                               `#45 <…>`__
 #51 (Bars have no foo)              Mathieu   22/05/2015   09:00:00                                          response to email                                               `#51 <…>`__
 #57 (Irritating message when bar)   Mathieu   22/05/2015   09:00:00                                          check for comments                                              `#57 <…>`__
 #63 (Bars have no foo)              Mathieu   22/05/2015   09:00:00                             0:10         keep door open                                                  `#63 <…>`__
 #53 (Foo never bars)                Luc       21/05/2015   12:58:00     21/05/2015   15:00:00   0:10         drive to brussels               1:52       1,87                 `#53 <…>`__   SLA 1/2014 (welket)
 #39 (Bars have no foo)              Mathieu   21/05/2015   12:58:00     21/05/2015   13:10:00                catch the brown fox             0:12       0,20                 `#39 <…>`__
 #33 (Irritating message when bar)   Mathieu   21/05/2015   12:53:00     21/05/2015   12:58:00                brainstorming lou & paul        0:05       0,08                 `#33 <…>`__
 #47 (Misc optimizations in Baz)     Luc       21/05/2015   12:48:00     21/05/2015   12:58:00                keep door open                  0:10       0,17                 `#47 <…>`__   SLA 2/2014 (welsch)
 #51 (Bars have no foo)              Jean      21/05/2015   12:29:00     21/05/2015   13:06:00                peer review with mark           0:37       0,62                 `#51 <…>`__
 #41 (Foo never bars)                Luc       21/05/2015   11:18:00     21/05/2015   12:48:00                check for comments              1:30       1,50                 `#41 <…>`__   SLA 3/2014 (aab)
 #45 (Irritating message when bar)   Jean      21/05/2015   09:00:00     21/05/2015   12:29:00   0:10         empty recycle bin               3:19       3,32                 `#45 <…>`__
 **Total (2384 rows)**                                                                                                                        **7:45**   **7,75**
=================================== ========= ============ ============ ============ ========== ============ =============================== ========== ==================== ============= =====================
<BLANKLINE>


Some sessions are on private tickets:

>>> from django.db.models import Q
>>> rt.show(working.Sessions, column_names="ticket user duration", filter=Q(ticket__private=True))
... #doctest: -REPORT_UDIFF +SKIP
============================== ======== ==========
 Ticket                         Worker   Duration
------------------------------ -------- ----------
 #4 (⚒ Foo and bar don't baz)   Luc      2:18
 #12 (⚒ Foo cannot bar)         Luc      1:30
 **Total (2 rows)**                      **3:48**
============================== ======== ==========
<BLANKLINE>


Worked hours
============

Example of :class:`WorkedHours` table

>>> ses = rt.login('jean')
>>> ses.show(working.WorkedHours)
... #doctest: -REPORT_UDIFF +NORMALIZE_WHITESPACE
================================ ==================================================== =========== ====== ===========
 Description                     Worked tickets                                       Regular     Free   Total
-------------------------------- ---------------------------------------------------- ----------- ------ -----------
 `Friday, 22 May 2015 <…>`__      `#57 <…>`__, `#63 <…>`__                             0:02               0:02
 `Thursday, 21 May 2015 <…>`__    `#51 <…>`__, `#45 <…>`__                             3:56               3:56
 `Wednesday, 20 May 2015 <…>`__   `#33 <…>`__, `#27 <…>`__, `#21 <…>`__, `#39 <…>`__   5:40               5:40
 `Tuesday, 19 May 2015 <…>`__     `#9 <…>`__, `#3 <…>`__, `#15 <…>`__                  4:00               4:00
 `Monday, 18 May 2015 <…>`__      `#105 <…>`__, `#111 <…>`__                           3:51               3:51
 `Sunday, 17 May 2015 <…>`__                                                                              0:00
 `Saturday, 16 May 2015 <…>`__                                                                            0:00
 **Total (7 rows)**                                                                   **17:29**          **17:29**
================================ ==================================================== =========== ====== ===========
<BLANKLINE>

The detail view of :class:`WorkedHours` has a slave panel showing  the
:class:`MySessionsByDay` table, the list of my sessions on this date. When Jean
clicks on the date of the first row ("Friday 22 May 2015"), he sees

>>> ses.show(working.MySessionsByDay, display_mode="summary")
... #doctest: -REPORT_UDIFF +NORMALIZE_WHITESPACE
`09:00 #57 <…>`__, `09:00 #63 <…>`__, **New** **?**

(Yes he started working on two different tickets within the same second.
Generated demo data...)

>>> ses.show(working.MySessionsByDay)
... #doctest: -REPORT_UDIFF +NORMALIZE_WHITESPACE
============ ========== ============ ========== =============================== =================================== ==========
 Start time   End Time   Break Time   Duration   Summary                         Ticket                              Workflow
------------ ---------- ------------ ---------- ------------------------------- ----------------------------------- ----------
 09:00:00                                        fiddle with get_auth()          #57 (Irritating message when bar)   [■]
 09:00:00                0:10                    jitsi meeting claire and paul   #63 (Bars have no foo)              [■]
============ ========== ============ ========== =============================== =================================== ==========
<BLANKLINE>



Service reports
===============

A :term:`service report` is a document used in various discussions with
a stakeholder.
It reports about the working time invested during a given date range.
This report can serve as a base for writing invoices.

It can be addressed to a recipient (a user) and in that case will
consider only the tickets for which this user has specified interest.

A service report currently contains three tables:

- a list of :term:`working sessions <working session>`
- a list of the tickets mentioned in the working sessions and their
  invested time
- a list of sites mentioned in the working sessions and their invested
  time


Reporting type
==============

The columns "Regular", "Free" and "Total" in reports like :class:`WorkedHours`,
:class:`OrderSummaries` and :class:`UserSummaries` are a way to distribute
worktime into basic categories.

These basic categories are defined by the :class:`ReportingTypes` choicelist.

The :attr:`reporting_type <Session.reporting_type>` field of a :term:`working
session` defines where the duration of this session is to appear in these
reports.

The default configuration has two reporting types:

>>> rt.show(working.ReportingTypes)
======= ========= =========
 value   name      text
------- --------- ---------
 10      regular   Regular
 20      free      Free
======= ========= =========
<BLANKLINE>


.. class:: ReportingTypes

  The list of reporting types available on this site.

A :term:`server administrator` can adapt the :class:`ReportingTypes` choicelist
to the site's needs. He may also change the default reporting type by setting
the :setting:`working.default_reporting_type` plugin attribute.

>>> dd.plugins.working.default_reporting_type
<working.ReportingTypes.regular:10>


Reporting rules
===============

The **reporting rules** specify which product to use when reporting a work in a
:term:`service report`.

The choice of the product to be reported was originally directly deduced from
the session's :attr:`Session.reporting_type`, but meanwhile it can also be based
on the value of the :attr:`urgent <Session.urgent>` checkbox. And it is
conceivable to add more selection criteria by extending the plugin.

The default Noi demo fixtures define the following reporting rules:

>>> rt.show(working.ReportingRules)
==== ===== ================ ======== =========================
 ID   No.   Reporting type   urgent   Product
---- ----- ---------------- -------- -------------------------
 1    1     Free                      Not invoiced
 2    2                      No       Hourly rate
 3    3                      Yes      Hourly rate (emergency)
==== ===== ================ ======== =========================
<BLANKLINE>

Which means: sessions with reporting type "Free" will be reported using the "Not
invoiced" product (which has a sales price of 0 and no storage history), and all
other sessions will be reported using either "Hourly rate" or "Hourly rate
(emergency)" depending on whether their ticket is marked "urgent" or not.

Here is the database structure of a reporting rule:

.. class:: ReportingRule

  Django model used to configure reporting rules.

  .. attribute:: seqno

    The sequence number of this rule. Lino looks up reporting rules ordered by
    their sequence number and uses the first rule that applies.

  .. attribute:: reporting_type

    Select the reporting type for which this rule applies.
    Leave blank if this rule applies independently of the session's :attr:`reporting_type <Session.reporting_type>`.

  .. attribute:: urgent

    Select "yes" if this rule applies only to sessions marked as urgent.
    Select "no" if this rule applies only to sessions that are *not* marked as urgent.
    Leave blank if this rule applies independently of the :attr:`urgent` checkbox.

  .. attribute:: product

    The :term:`product` to invoice when this reporting rule applies.

Components
==========

In :ref:`noi`, when a :term:`working session` is invoiced using the "Emergency"
tariff because the ticket is marked as :attr:`urgent
<lino_xl.lib.tickets.Ticket.urgent>`, the Emergency tariff (a product instance)
"knows" that it is actually just a virtual product. Each hour of Emergency
service is equivalent to 1.5 hours of regular service.





Database models
===============

.. class:: SessionType

    Django model representing the type of a :term:`working session`.

.. class:: Session

    Django model representing a :term:`working session`.

    .. attribute:: start_date

        The date when you started to work.

    .. attribute:: start_time

        The time (in `hh:mm`) when you started working on this
        session.

        This is your local time according to the time zone specified
        in your preferences.

    .. attribute:: end_date

        Leave this field blank if it is the same date as start_date.

    .. attribute:: end_time

        The time (in `hh:mm`) when the worker stopped to work.

        An empty :attr:`end_time` means that the user is still busy
        with that session, the session is not yet closed.

        :meth:`end_session` sets this to the current time.

    .. attribute:: break_time

       The time (in `hh:mm`) to remove from the duration resulting
       from the difference between :attr:`start_time` and
       :attr:`end_time`.

    .. attribute:: faculty

      The faculty that has been used during this session. On a new
      session this defaults to the needed faculty currently specified
      on the ticket.

    .. attribute:: duration

        Virtual field returning the :attr:`computed_duration`.

    .. attribute:: computed_duration

        The duration of this session as a :class:`Duration`.

        This is the mathematical difference between :attr:`start_time` and
        :attr:`end_time`, minus the :attr:`break_time` and the durations of
        sub-sessions of this session. (Details see
        :meth:`lino_xl.lib.working.models.Session.compute_duration`).

    .. attribute:: duration_decimal

      The :attr:`computed_duration` expressed as a decimal number rather than a
      :class:`Duration`. This format can be more convenient when processing the
      data in a spreadsheet.

    .. attribute:: reporting_type

      The reporting type to use for this session.

    .. attribute:: ticket

      The ticket that has been worked on during this session.

    .. method:: end_session

        Tell Lino that you stop this session for now.
        This will simply set the :attr:`end_time` to the current time.

        Implemented by :class:`EndThisSession`.


Tables reference
================

.. class:: Sessions

.. class:: SessionsByTicket

    Show the working sessions on this ticket.

    Example:

    >>> ses = rt.login('robin')
    >>> obj = tickets.Ticket.objects.get(pk=59)
    >>> ses.show(working.SessionsByTicket, obj)
    Total 64:54 hours.
    Active sessions: `Luc since 09:00:00 <…>`__ **■**

    The default :term:`display mode` is "summary". Here is how it looks in
    display mode "grid":

    >>> ses.show(working.SessionsByTicket, obj, display_mode=DISPLAY_MODE_GRID)
    ... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ===================== =============================== ============ ========== ============ =========== ======== ======
     Start date            Summary                         Start time   End Time   Break Time   Duration    Worker   ID
    --------------------- ------------------------------- ------------ ---------- ------------ ----------- -------- ------
     22/05/2015            commit and push                 09:00:00                0:10                     Luc      1579
     13/05/2015            catch the brown fox             10:02:00     13:01:00   0:10         2:49        Luc      1560
     04/05/2015            empty recycle bin               12:58:00     13:10:00                0:12        Luc      1541
     23/04/2015            meeting with john               12:48:00     12:58:00                0:10        Luc      1522
     14/04/2015            peer review with mark           12:29:00     13:06:00                0:37        Luc      1503
     ...
     29/05/2014            drive to brussels               12:29:00     13:06:00                0:37        Luc      876
     21/05/2014            brainstorming lou & paul        09:00:00     12:53:00   0:10         3:43        Luc      857
     12/05/2014            commit and push                 09:00:00     11:18:00   0:10         2:08        Luc      838
     30/04/2014            catch the brown fox             12:58:00     15:00:00   0:10         1:52        Luc      819
     22/04/2014            empty recycle bin               09:00:00     10:02:00                1:02        Luc      800
     **Total (42 rows)**                                                                        **64:54**
    ===================== =============================== ============ ========== ============ =========== ======== ======
    <BLANKLINE>


.. class:: MySessions

  Shows all my sessions.

  Use the |filter| button to filter them. You can export them to Excel.

.. class:: MySessionsByDate

  Shows my working sessions of a given day.

  Use this to manually edit your :term:`working sessions <working session>`.

.. class:: TicketsReport
.. class:: SitesByReport

     The list of tickets mentioned in a service report.

.. class:: WorkersByReport


Actions reference
=================

.. class:: StartTicketSession

    The action behind :class:`Workable.start_session`.


.. class:: EndSession

    Common base for :class:`EndThisSession` and :class:`EndTicketSession`.

.. class:: EndTicketSession

    The action behind :class:`Workable.end_session`.

.. class:: EndThisSession

    The action behind :class:`Session.end_session`.


The `Workable` model mixin
==========================

.. class:: Workable

    Base class for things that workers can work on.

    The model specified in :attr:`ticket_model <Plugin.ticket_model>`
    must be a subclass of this.
    For example, in :ref:`noi` tickets are workable.

    .. method:: is_workable_for

        Return True if the given user can start a *working session* on
        this object.

    .. method:: on_worked

        This is automatically called when a *working session* has been
        created or modified.

    .. method:: start_session

        Start a :term:`working session` on this ticket.

        See :class:`StartTicketSession`.

    .. method:: end_session

        Tell Lino that you stop working on this ticket for now.
        This will simply set the :attr:`Session.end_time` to the current time.

        Implemented by :class:`EndTicketSession`.



Actions reference
=================


.. class:: ShowMySessionsByDay

    Shows your :term:`working sessions <working session>` per day.


.. class:: TicketHasSessions

    Select only tickets for which there has been at least one session
    during the given period.

    This is added as item to :class:`lino_xl.lib.tickets.TicketEvents`.


.. class:: ProjectHasSessions

    Select only projects for which there has been at least one session
    during the given period.

    This is added as item to :class:`lino_xl.lib.tickets.ProjectEvents`.

.. class:: Worker

    A user who is candidate for working on a ticket.



Summaries
=========

.. class:: SiteSummary

    An automatically generated record with yearly summary data about a site.

.. class:: SummariesBySite

    Shows the summary records for a given site.

.. class:: UserSummary

    An automatically generated record with monthly summary data about a user.

.. class:: SummariesByUser

    Shows the summary records for a given user.

Summaries by order
==================

.. class:: OrderSummaries

>>> rt.show(working.OrderSummaries, exclude=Q(regular_hours=""))
... #doctest: +REPORT_UDIFF
==== ====== ======= ===================== ================ ================== ========= ======
 ID   Year   Month   Subscription          Active tickets   Inactive tickets   Regular   Free
---- ------ ------- --------------------- ---------------- ------------------ --------- ------
 2    2014           SLA 1/2014 (welket)   0                0                  167:24
 3    2015           SLA 1/2014 (welket)   0                0                  95:22
 5    2014           SLA 2/2014 (welsch)   0                0                  172:29
 6    2015           SLA 2/2014 (welsch)   0                0                  92:40
 8    2014           SLA 3/2014 (aab)      0                0                  170:57
 9    2015           SLA 3/2014 (aab)      0                0                  90:49
 11   2014           SLA 4/2014 (bcc)      0                0                  168:21
 12   2015           SLA 4/2014 (bcc)      0                0                  95:12
 14   2014           SLA 5/2014 (dde)      0                0                  127:31
 15   2015           SLA 5/2014 (dde)      0                0                  67:52
==== ====== ======= ===================== ================ ================== ========= ======
<BLANKLINE>


>>> rt.show(working.OrderSummaries)
... #doctest: -REPORT_UDIFF
==== ====== ======= ===================== ================ ================== ========= ======
 ID   Year   Month   Subscription          Active tickets   Inactive tickets   Regular   Free
---- ------ ------- --------------------- ---------------- ------------------ --------- ------
 1    2013           SLA 1/2014 (welket)   0                0
 2    2014           SLA 1/2014 (welket)   0                0                  167:24
 3    2015           SLA 1/2014 (welket)   0                0                  95:22
 4    2013           SLA 2/2014 (welsch)   0                0
 5    2014           SLA 2/2014 (welsch)   0                0                  172:29
 6    2015           SLA 2/2014 (welsch)   0                0                  92:40
 7    2013           SLA 3/2014 (aab)      0                0
 8    2014           SLA 3/2014 (aab)      0                0                  170:57
 9    2015           SLA 3/2014 (aab)      0                0                  90:49
 10   2013           SLA 4/2014 (bcc)      0                0
 11   2014           SLA 4/2014 (bcc)      0                0                  168:21
 12   2015           SLA 4/2014 (bcc)      0                0                  95:12
 13   2013           SLA 5/2014 (dde)      0                0
 14   2014           SLA 5/2014 (dde)      0                0                  127:31
 15   2015           SLA 5/2014 (dde)      0                0                  67:52
==== ====== ======= ===================== ================ ================== ========= ======
<BLANKLINE>


Summaries by user
=================

.. class:: UserSummaries


>>> rt.show(working.UserSummaries, exclude=Q(regular_hours=""))
... #doctest: -REPORT_UDIFF
===== ====== ====== ========= ========= =========
 ID    Year   Week   User      Regular   Free
----- ------ ------ --------- --------- ---------
 53    2014   1      Jean      13:31
 68    2014   16     Jean      9:11
 69    2014   17     Jean      21:55
 70    2014   18     Jean      21:27
 71    2014   19     Jean      23:07
 72    2014   20     Jean      21:23
 73    2014   21     Jean      21:18
 74    2014   22     Jean      21:27
 75    2014   23     Jean      23:07
 76    2014   24     Jean      21:23
 77    2014   25     Jean      21:18
 78    2014   26     Jean      21:27
 79    2014   27     Jean      23:07
 80    2014   28     Jean      21:23
 81    2014   29     Jean      21:18
 82    2014   30     Jean      21:27
 83    2014   31     Jean      23:07
 84    2014   32     Jean      21:23
 85    2014   33     Jean      21:18
 86    2014   34     Jean      21:27
 87    2014   35     Jean      23:07
 88    2014   36     Jean      21:23
 89    2014   37     Jean      21:18
 90    2014   38     Jean      21:27
 91    2014   39     Jean      23:07
 92    2014   40     Jean      21:23
 93    2014   41     Jean      21:18
 94    2014   42     Jean      21:27
 95    2014   43     Jean      23:07
 96    2014   44     Jean      21:23
 97    2014   45     Jean      21:18
 98    2014   46     Jean      21:27
 99    2014   47     Jean      23:07
 100   2014   48     Jean      21:23
 101   2014   49     Jean      21:18
 102   2014   50     Jean      21:27
 103   2014   51     Jean      23:07
 104   2014   52     Jean      21:23
 105   2015   1      Jean      7:47
 106   2015   2      Jean      21:27
 107   2015   3      Jean      23:52     1202:41
 108   2015   4      Jean      22:08     851:07
 109   2015   5      Jean      21:18
 110   2015   6      Jean      21:27
 111   2015   7      Jean      23:07
 112   2015   8      Jean      21:23
 113   2015   9      Jean      21:18
 114   2015   10     Jean      21:27
 115   2015   11     Jean      23:07
 116   2015   12     Jean      21:23
 117   2015   13     Jean      21:18
 118   2015   14     Jean      21:27
 119   2015   15     Jean      23:07
 120   2015   16     Jean      21:23
 121   2015   17     Jean      21:18
 122   2015   18     Jean      21:27
 123   2015   19     Jean      23:07
 124   2015   20     Jean      21:23
 125   2015   21     Jean      17:27
 209   2014   1      Luc       11:47
 224   2014   16     Luc       9:40
 225   2014   17     Luc       21:23
 226   2014   18     Luc       21:18
 227   2014   19     Luc       21:27
 228   2014   20     Luc       23:07
 229   2014   21     Luc       21:23
 230   2014   22     Luc       21:18
 231   2014   23     Luc       21:27
 232   2014   24     Luc       23:07
 233   2014   25     Luc       21:23
 234   2014   26     Luc       21:18
 235   2014   27     Luc       21:27
 236   2014   28     Luc       23:07
 237   2014   29     Luc       21:23
 238   2014   30     Luc       21:18
 239   2014   31     Luc       21:27
 240   2014   32     Luc       23:07
 241   2014   33     Luc       21:23
 242   2014   34     Luc       21:18
 243   2014   35     Luc       21:27
 244   2014   36     Luc       23:07
 245   2014   37     Luc       21:23
 246   2014   38     Luc       21:18
 247   2014   39     Luc       21:27
 248   2014   40     Luc       23:07
 249   2014   41     Luc       21:23
 250   2014   42     Luc       21:18
 251   2014   43     Luc       21:27
 252   2014   44     Luc       23:07
 253   2014   45     Luc       21:23
 254   2014   46     Luc       21:18
 255   2014   47     Luc       21:27
 256   2014   48     Luc       23:07
 257   2014   49     Luc       21:23
 258   2014   50     Luc       21:18
 259   2014   51     Luc       21:27
 260   2014   52     Luc       23:07
 261   2015   1      Luc       9:36
 262   2015   2      Luc       21:18
 263   2015   3      Luc       21:27
 264   2015   4      Luc       23:07
 265   2015   5      Luc       21:23
 266   2015   6      Luc       21:18
 267   2015   7      Luc       21:27
 268   2015   8      Luc       23:07
 269   2015   9      Luc       21:23
 270   2015   10     Luc       21:18
 271   2015   11     Luc       21:27
 272   2015   12     Luc       23:07
 273   2015   13     Luc       21:23
 274   2015   14     Luc       21:18
 275   2015   15     Luc       21:27
 276   2015   16     Luc       23:07
 277   2015   17     Luc       21:23
 278   2015   18     Luc       21:18
 279   2015   19     Luc       21:27
 280   2015   20     Luc       23:07
 281   2015   21     Luc       17:27
 521   2014   1      Mathieu   13:27
 536   2014   16     Mathieu   7:51
 537   2014   17     Mathieu   23:07
 538   2014   18     Mathieu   21:23
 539   2014   19     Mathieu   21:18
 540   2014   20     Mathieu   21:27
 541   2014   21     Mathieu   23:07
 542   2014   22     Mathieu   21:23
 543   2014   23     Mathieu   21:18
 544   2014   24     Mathieu   21:27
 545   2014   25     Mathieu   23:07
 546   2014   26     Mathieu   21:23
 547   2014   27     Mathieu   21:18
 548   2014   28     Mathieu   21:27
 549   2014   29     Mathieu   23:07
 550   2014   30     Mathieu   21:23
 551   2014   31     Mathieu   21:18
 552   2014   32     Mathieu   21:27
 553   2014   33     Mathieu   23:07
 554   2014   34     Mathieu   21:23
 555   2014   35     Mathieu   21:18
 556   2014   36     Mathieu   21:27
 557   2014   37     Mathieu   23:07
 558   2014   38     Mathieu   21:23
 559   2014   39     Mathieu   21:18
 560   2014   40     Mathieu   21:27
 561   2014   41     Mathieu   23:07
 562   2014   42     Mathieu   21:23
 563   2014   43     Mathieu   21:18
 564   2014   44     Mathieu   21:27
 565   2014   45     Mathieu   23:07
 566   2014   46     Mathieu   21:23
 567   2014   47     Mathieu   21:18
 568   2014   48     Mathieu   21:27
 569   2014   49     Mathieu   23:07
 570   2014   50     Mathieu   21:23
 571   2014   51     Mathieu   21:18
 572   2014   52     Mathieu   21:27
 573   2015   1      Mathieu   9:40
 574   2015   2      Mathieu   21:23
 575   2015   3      Mathieu   21:18
 576   2015   4      Mathieu   21:27
 577   2015   5      Mathieu   23:07
 578   2015   6      Mathieu   21:23
 579   2015   7      Mathieu   21:18
 580   2015   8      Mathieu   21:27
 581   2015   9      Mathieu   23:07
 582   2015   10     Mathieu   21:23
 583   2015   11     Mathieu   21:18
 584   2015   12     Mathieu   21:27
 585   2015   13     Mathieu   23:07
 586   2015   14     Mathieu   21:23
 587   2015   15     Mathieu   21:18
 588   2015   16     Mathieu   21:27
 589   2015   17     Mathieu   23:07
 590   2015   18     Mathieu   21:23
 591   2015   19     Mathieu   21:18
 592   2015   20     Mathieu   21:27
 593   2015   21     Mathieu   17:27
===== ====== ====== ========= ========= =========
<BLANKLINE>


Some projects have more than 999:59 hours per year of work, which would be
indicated by a ``-1:00`` if :setting:`summaries.duration_max_length` was at its
default value of 6. But in :mod:`lino_noi.lib.noi.settings` the default value is
modified to 10.

>>> dd.plugins.summaries.duration_max_length
10
>>> rt.login('jean').show(working.AllSummaries)
... #doctest: -REPORT_UDIFF
==== ====== ======= ===================== ================ ================== ========= ======
 ID   Year   Month   Subscription          Active tickets   Inactive tickets   Regular   Free
---- ------ ------- --------------------- ---------------- ------------------ --------- ------
 1    2013           SLA 1/2014 (welket)   0                0
 2    2014           SLA 1/2014 (welket)   0                0                  167:24
 3    2015           SLA 1/2014 (welket)   0                0                  95:22
 4    2013           SLA 2/2014 (welsch)   0                0
 5    2014           SLA 2/2014 (welsch)   0                0                  172:29
 6    2015           SLA 2/2014 (welsch)   0                0                  92:40
 7    2013           SLA 3/2014 (aab)      0                0
 8    2014           SLA 3/2014 (aab)      0                0                  170:57
 9    2015           SLA 3/2014 (aab)      0                0                  90:49
 10   2013           SLA 4/2014 (bcc)      0                0
 11   2014           SLA 4/2014 (bcc)      0                0                  168:21
 12   2015           SLA 4/2014 (bcc)      0                0                  95:12
 13   2013           SLA 5/2014 (dde)      0                0
 14   2014           SLA 5/2014 (dde)      0                0                  127:31
 15   2015           SLA 5/2014 (dde)      0                0                  67:52
==== ====== ======= ===================== ================ ================== ========= ======
<BLANKLINE>


Sub-sessions
============

To find the primary key of a session with sub-sessions, there is a print
statement in :file:`book/lino_book/projects/noi1e/settings/fixtures/demo.py`. So
if the following snippet fails, run :cmd:`go noi1e` followed by :cmd:`pm prep`
and watch the output for two lines of text similar to the following ones::

  20230117 Session 2373 has a subsession (compare docs/specs/working.rst)
  20230117 Session 2379 has a subsession (compare docs/specs/working.rst)

And then use one of these numbers as the pk in the following snippet.

>>> obj = working.Session.objects.get(pk=2373)
>>> print(obj.break_time)
None
>>> st, et = obj.get_datetime('start'), obj.get_datetime('end')
>>> print("from {} to {}".format(st, et))
from 2015-01-14 09:00:00+00:00 to 2015-01-22 17:00:00+00:00

The session starts on 2015-02-14 at 09:00 and ends on 2015-01-22 at 17:00, so it
lasts exactly 8 days and 8 hours, in other words 200 hours or 12000 minutes.

>>> delta = et - st
>>> print(delta)
8 days, 8:00:00
>>> print(delta.total_seconds()/3600)
200.0

>>> 8*24+8
200

But the :attr:`computed_duration` is less than 200 hours:

>>> obj.computed_duration
Duration('168:17')

This is because there are sub-sessions.  The :meth:`get_sub_sessions` method
iterates over them :

>>> from lino.utils.quantities import Duration
>>> for s in obj.get_sub_sessions():
...    print("- {} {} ({})".format(s.computed_duration, s.break_time, s))
... #doctest: -SKIP
- 1:02 None (14/01/2015 09:00-10:02 Jean #21)
- 2:49 0:10 (14/01/2015 10:02-13:01 Jean #27)
- 2:58 0:10 (15/01/2015 09:00-12:53 Jean #33)
- 0:45 None (15/01/2015 09:30-10:15 Jean #87)
- 0:05 None (15/01/2015 12:53-12:58 Jean #39)
- 0:12 None (15/01/2015 12:58-13:10 Jean #45)
- 2:08 0:10 (16/01/2015 09:00-11:18 Jean #51)
- 1:30 None (16/01/2015 11:18-12:48 Jean #57)
- 0:10 None (16/01/2015 12:48-12:58 Jean #63)
- 1:52 0:10 (16/01/2015 12:58-15:00 Jean #69)
- 3:19 0:10 (19/01/2015 09:00-12:29 Jean #75)
- 0:37 None (19/01/2015 12:29-13:06 Jean #81)
- 1:02 None (20/01/2015 09:00-10:02 Jean #87)
- 0:45 None (20/01/2015 09:30-10:15 Jean #9)
- 2:49 0:10 (20/01/2015 10:02-13:01 Jean #93)
- 3:43 0:10 (21/01/2015 09:00-12:53 Jean #99)
- 0:05 None (21/01/2015 12:53-12:58 Jean #105)
- 0:12 None (21/01/2015 12:58-13:10 Jean #111)
- 2:08 0:10 (22/01/2015 09:00-11:18 Jean #3)
- 1:30 None (22/01/2015 11:18-12:48 Jean #9)
- 0:10 None (22/01/2015 12:48-12:58 Jean #15)
- 1:52 0:10 (22/01/2015 12:58-15:00 Jean #21)



Here is the sum of the durations of these sub-sessions:

>>> duration_of_sub_sessions = sum([s.computed_duration for s in obj.get_sub_sessions()])
>>> duration_of_sub_sessions
Duration('31:43')

And the sum of these two sums is indeed 200:00:

>>> duration_of_sub_sessions + obj.computed_duration
Duration('200:00')

Worker contracts
=================

.. class:: Contract

  Django model used to represent a worker contract.

  .. attribute:: user

    The worker.

  .. attribute:: hours_per_week

    How many hours this worker is expected to provide per week.

.. class:: Contracts

  Shows the list of all worker contracts for managing them.

>>> rt.show(working.Contracts)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==================== ============ ============ ==========
 Worker               Hours/week   Start date   End date
-------------------- ------------ ------------ ----------
 Marc                 2:00
 Mathieu              20:00
 Luc                  30:00
 Jean                 40:00
 **Total (4 rows)**   **92:00**
==================== ============ ============ ==========
<BLANKLINE>


.. class:: ActiveContracts

  Shows the list of all worker contracts with statistic data about their activity.

>>> rt.show(working.ActiveContracts)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
+--------------------+------------+-----------+------------+-----------+------------+
| Worker             | Hours/week | Hours     | Hours      | Comments  | Comments   |
|                    |            | last week | last month | last week | last month |
+====================+============+===========+============+===========+============+
| Marc               | 2:00       | 0:00      | 0:00       | 0         | 61         |
+--------------------+------------+-----------+------------+-----------+------------+
| Mathieu            | 20:00      | 21:27     | 95:06      | 0         | 67         |
+--------------------+------------+-----------+------------+-----------+------------+
| Luc                | 30:00      | 23:07     | 96:55      | 0         | 68         |
+--------------------+------------+-----------+------------+-----------+------------+
| Jean               | 40:00      | 21:23     | 96:51      | 0         | 72         |
+--------------------+------------+-----------+------------+-----------+------------+
| **Total (4 rows)** | **92:00**  | **65:57** | **288:52** | **0**     | **268**    |
+--------------------+------------+-----------+------------+-----------+------------+
<BLANKLINE>

The somewhat unrealistic values for comments in above table are because in our
demo database, all comments get created between 2015-04-22 and 2015-04-24, which
is within the last month but not within the last week:

>>> str(dd.today())
'2015-05-22'

>>> sorted(set([str(c.created.date()) for c in comments.Comment.objects.all()]))
['2015-04-22', '2015-04-23', '2015-04-24']




Weekly report
=============

The plugin defines a system task procedure :func:`send_weekly_report`, which
sends a configurable weekly report to all workers with a contract.

.. function:: send_weekly_report

  The procedure used by a :term:`system task` that sends a report to all workers
  with a contract. The content of the report can be customized by editing the
  :xfile:`working/weekly_report.eml` template.

.. xfile:: working/weekly_report.eml

  The template used to generate the content of the `Weekly report`_.



Don't read me
=============

>>> working.WorkedHours
lino_xl.lib.working.ui.WorkedHours

>>> print(working.WorkedHours.column_names)
detail_link worked_tickets  vc0:5 vc1:5 vc2:5 *

>>> working.WorkedHours.get_data_elem('detail_link')
lino.core.actors.Actor.detail_link

Testing for equality of quantities
----------------------------------

Remind the pitfall described in :ref:`dg.quantities.pitfall`. Here is a list of
sessions where the :attr:`computed_duration` field is not exaclty the same as
the return value of :meth:`compute_duration`. They *look* the same when you
print them, but actually they differ.

>>> [obj.pk for obj in working.Session.objects.all()
...     if obj.computed_duration != obj.compute_duration()]
... #doctest: +ELLIPSIS
[5, 6, 16, 17, ... 2382, 2383, 2384]

We verify this with the first one.

>>> obj = working.Session.objects.get(pk=5)
>>> obj.computed_duration
Duration('1:52')
>>> obj.compute_duration()
Duration('1:52')

But:

>>> obj.computed_duration == obj.compute_duration()
False

That's why the :class:`SessionChecker` must call :func:`str` in order to get the
expected result:

>>> str(obj.computed_duration) == str(obj.compute_duration())
True

'NoneType' object has no attribute 'start_date'
-----------------------------------------------

Occurred when trying to print working.WorkedHours (:ticket:`523`).

In order to reproduce the issue, let's find the users who worked on more
than one subscription and then render this table to HTML.

>>> for u in users.User.objects.all():
...     qs = subscriptions.Subscription.objects.filter(tickets_by_order__sessions_by_ticket__user=u).distinct()
...     if qs.count() > 1:
...         print("{} {} {}".format(str(u.username), "worked on", [o for o in qs]))
... #doctest: +NORMALIZE_WHITESPACE
luc worked on [Subscription #4 ('SLA 4/2014 (bcc)'), Subscription #3 ('SLA
3/2014 (aab)'), Subscription #2 ('SLA 2/2014 (welsch)'), Subscription #1 ('SLA
1/2014 (welket)'), Subscription #5 ('SLA 5/2014 (dde)')]


>>> url = "/api/working/WorkedHours?"
>>> #url += "_dc=1583295523012&cw=398&cw=398&cw=76&cw=76&cw=76&cw=76&cw=281&cw=76&ch=&ch=&ch=&ch=&ch=&ch=&ch=true&ch=true&ci=detail_link&ci=worked_tickets&ci=vc0&ci=vc1&ci=vc2&ci=vc3&ci=description&ci=day_number&name=0&pv=188&pv=&pv=&pv=&lv=1583294270.8095002&an=show_as_html&sr="
>>> url += "an=show_as_html"
>>> test_client.force_login(rt.login('jean').user)
>>> res = test_client.get(url, REMOTE_USER="jean")
>>> json.loads(res.content.decode()) == {'open_url': '/bs3/working/WorkedHours?limit=15', 'success': True}
True

The html version of this table has only 5 rows (4 data rows and the total row)
because valueless rows are not included by default:

>>> ar = rt.login('jean')
>>> u = ar.get_user()
>>> ar = working.WorkedHours.create_request(user=u)
>>> ar = ar.spawn(working.WorkedHours)
>>> lst = list(ar)
>>> len(lst)
7
>>> e = ar.table2xhtml()
>>> len(e.findall('./tbody/tr'))
8
