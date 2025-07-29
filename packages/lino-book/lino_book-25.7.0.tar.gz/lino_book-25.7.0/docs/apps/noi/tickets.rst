.. doctest docs/apps/noi/tickets.rst
.. _noi.specs.tickets:

======================================
``tickets`` in Noi
======================================

The :mod:`lino_noi.lib.tickets` plugin extends :mod:`lino_xl.lib.tickets` to
make it collaborate with :mod:`lino_noi.lib.working`.

In :ref:`noi` the *site* of a *ticket* also indicates "who is going to pay" for
our work. Lino Noi uses this information when generating a service report.


.. currentmodule:: lino_noi.lib.tickets


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


Tickets
=======

Here is a textual description of the fields and their layout used in
the detail window of a ticket.

>>> from lino.utils.diag import py2rst
>>> print(py2rst(tickets.AllTickets.detail_layout, True))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF -SKIP
(main) [visible for all]:
- **General** (general_tab_1):
  - **None** (overview)
  - (general3):
    - (general3_1): **Workflow** (workflow_buttons), **Assign to** (quick_assign_to) [visible for developer admin]
    - **Comments** (comments.CommentsByRFC)
- **Request** (post_tab_1):
  - (post1):
    - (post1_1): **ID** (id), **Author** (user)
    - **Summary** (summary)
    - **Description** (description)
  - (post2):
    - (post2_1): **Subscription** (order), **End user** (end_user)
    - (post2_2): **Confidential** (private), **Urgent** (urgent)
    - **Upload files** (uploads.UploadsByController) [visible for customer contributor developer admin]
- **Triage** (triage_tab_1):
  - (triage1):
    - (triage1_1): **Team** (group), **Ticket type** (ticket_type)
    - **Parent** (parent)
    - **Children** (tickets.TicketsByParent)
  - (triage2): **Assign to** (quick_assign_to) [visible for developer admin], **Add tag** (add_tag), **Tags** (topics.TagsByOwner) [visible for customer contributor developer admin]
- **Work** (work_tab_1):
  - (work1):
    - **Workflow** (workflow_buttons)
    - (work1_2): **Priority** (priority), **My nickname** (my_nickname)
    - **Mentioned in** (comments.CommentsByMentioned)
  - (work2):
    - **Working sessions** (working.SessionsByTicket) [visible for contributor developer admin]
    - (work2_2): **Regular** (regular_hours), **Free** (free_hours)
- **More** (more_tab_1):
  - (more1):
    - (more1_1): **Created** (created), **Modified** (modified)
    - **Reference** (ref)
    - **Resolution** (upgrade_notes)
  - (more2):
    - (more2_1): **State** (state), **Assigned to** (assigned_to)
    - (more2_2): **Planned time** (planned_time), **Deadline** (deadline)
    - **Duplicate of** (duplicate_of)
    - **Duplicates** (DuplicatesByTicket)
<BLANKLINE>


.. class:: Ticket

    The Django model used to represent a *ticket* in Noi. Adds some fields and
    methods.

    .. attribute:: assigned_to

        The user who is working on this ticket.

    .. attribute:: site

        The site this ticket belongs to.
        You can select only sites you are subscribed to.


Screenshots
===========

.. image:: tickets.Ticket.merge.png


The life cycle of a ticket
==========================

In :ref:`noi` we use the default tickets workflow defined  in
:class:`lino_xl.lib.tickets.TicketStates`.


Subscriptions
=============

The :attr:`Ticket.order` field in Noi points to a
:class:`lino_xl.lib.subscriptions.Subscription`.

>>> rt.show(subscriptions.Subscriptions)
==== ============ =========== ===================== ========= ================
 ID   Start date   Reference   Partner               Subject   Workflow
---- ------------ ----------- --------------------- --------- ----------------
 1    07/01/2014   welket      Rumma & Ko OÜ                   **Registered**
 2    27/01/2014   welsch      Bäckerei Ausdemwald             **Registered**
 3    16/02/2014   aab         Bäckerei Mießen                 **Registered**
 4    08/03/2014   bcc         Bäckerei Schmitz                **Registered**
 5    28/03/2014   dde         Garage Mergelsberg              **Registered**
==== ============ =========== ===================== ========= ================
<BLANKLINE>


Ticket types
============

The :fixture:`demo` fixture defines the following ticket types.

>>> rt.show(tickets.TicketTypes)
============= ================== ================== ================
 Designation   Designation (de)   Designation (fr)   Reporting type
------------- ------------------ ------------------ ----------------
 Bugfix        Bugfix             Bugfix             Regular
 Enhancement   Enhancement        Enhancement        Regular
 Upgrade       Upgrade            Upgrade            Regular
 Regression    Regression         Regression         Free
============= ================== ================== ================
<BLANKLINE>

Deciding what to do next
========================

Show all active tickets reported by me.

>>> rt.login('marc').get_user().user_type
<users.UserTypes.customer:100>

Marc is a customer, so he has no permission to modify the workflow state of
tickets owned by other users.
But he can have tickets to do, i.e. that are assiged to him.

>>> rt.login('marc').show(tickets.MyTicketsToWork, max_width=40, display_mode="grid")
... #doctest: -REPORT_UDIFF
+----------+------------------------------------------+---------------+
| Priority | Ticket                                   | Workflow      |
+==========+==========================================+===============+
| 30       | `#103 (Cannot delete foo) <…>`__ (by     | **⚒ Working** |
|          | `Romain Raffault <…>`__ in `Developers   |               |
|          | <…>`__ assigned to `Marc <…>`__)         |               |
+----------+------------------------------------------+---------------+
| 30       | `#85 ('NoneType' object has no attribute | **⚒ Working** |
|          | 'isocode') <…>`__ (by `Jean <…>`__ in    |               |
|          | `Developers <…>`__ assigned to `Marc     |               |
|          | <…>`__)                                  |               |
+----------+------------------------------------------+---------------+
| 30       | `#67 (Cannot delete foo) <…>`__ (by      | **⚒ Working** |
|          | `Mathieu <…>`__ in `Developers <…>`__    |               |
|          | assigned to `Marc <…>`__)                |               |
+----------+------------------------------------------+---------------+
| 30       | `#55 (Cannot delete foo) <…>`__ (by      | **⚹ New**     |
|          | `Rolf Rompen <…>`__ in `Developers       |               |
|          | <…>`__ assigned to `Marc <…>`__)         |               |
+----------+------------------------------------------+---------------+
| 30       | `#37 ('NoneType' object has no attribute | **⚹ New**     |
|          | 'isocode') <…>`__ (by `Luc <…>`__ in     |               |
|          | `Developers <…>`__ assigned to `Marc     |               |
|          | <…>`__)                                  |               |
+----------+------------------------------------------+---------------+
| 30       | `#19 (Cannot delete foo) <…>`__ (by      | **⚹ New**     |
|          | `Romain Raffault <…>`__ in `Developers   |               |
|          | <…>`__ assigned to `Marc <…>`__)         |               |
+----------+------------------------------------------+---------------+
<BLANKLINE>



>>> rt.login('jean').show(tickets.MyTickets, max_width=30, display_mode="grid")
... #doctest: +REPORT_UDIFF
+----------+--------------------------------+-----------------+--------------------------------+
| Priority | Ticket                         | Assigned to     | Workflow                       |
+==========+================================+=================+================================+
| 50       | `#1 (Föö fails to bar when     |                 | [▶] **⚹ New** → [☾] [☎] [☉]    |
|          | baz) <…>`__ ( 50 in            |                 | [⚒] [☐] [☑] [⧖]                |
|          | `Developers <…>`__) [▶] **⚹    |                 |                                |
|          | New** → [☾] [☎] [☉] [⚒] [☐]    |                 |                                |
|          | [☑] [⧖]                        |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 45       | `#15 (Bars have no foo) <…>`__ | Mathieu         | [▶] **☐ Ready** → [⚹] [☾] [☎]  |
|          | ( 45 in `Managers <…>`__       |                 | [⚒] [☑] [☒]                    |
|          | assigned to `Mathieu <…>`__)   |                 |                                |
|          | [▶] **☐ Ready** → [⚹] [☾] [☎]  |                 |                                |
|          | [⚒] [☑] [☒]                    |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 30       | `#92 (Why <p> tags are so bar) |                 | [▶] **☎ Talk** → [⚹] [☾] [☉]   |
|          | <…>`__ [▶] **☎ Talk** → [⚹]    |                 | [☐] [☑] [☒] [⧖]                |
|          | [☾] [☉] [☐] [☑] [☒] [⧖]        |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 30       | `#85 ('NoneType' object has no | Marc            | [▶] **⚒ Working** → [⚹] [☾]    |
|          | attribute 'isocode') <…>`__    |                 | [☎] [☉] [☐] [☑] [☒] [⧖]        |
|          | (in `Developers <…>`__         |                 |                                |
|          | assigned to `Marc <…>`__) [▶]  |                 |                                |
|          | **⚒ Working** → [⚹] [☾] [☎]    |                 |                                |
|          | [☉] [☐] [☑] [☒] [⧖]            |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 30       | `#78 (No more foo when bar is  |                 | [▶] **☐ Ready** → [⚹] [☾] [☎]  |
|          | gone) <…>`__ [▶] **☐ Ready** → |                 | [☑] [☒]                        |
|          | [⚹] [☾] [☎] [☑] [☒]            |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 30       | `#64 (How to get bar from foo) |                 | [▶] **⚹ New** → [☾] [☎] [☉]    |
|          | <…>`__ [▶] **⚹ New** → [☾] [☎] |                 | [☐] [☑] [⧖]                    |
|          | [☉] [☐] [☑] [⧖]                |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 30       | `#57 (Irritating message when  |                 | [■] **☉ Open** → [⚹] [☾] [☎]   |
|          | bar) <…>`__ (in `Managers      |                 | [⚒] [☐] [☑] [☒] [⧖]            |
|          | <…>`__) [■] **☉ Open** → [⚹]   |                 |                                |
|          | [☾] [☎] [⚒] [☐] [☑] [☒] [⧖]    |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 30       | `#29 (Foo never bars) <…>`__   | Romain Raffault | [▶] **☎ Talk** → [⚹] [☾] [☉]   |
|          | (in `Sales team <…>`__         |                 | [⚒] [☐] [☑] [☒] [⧖]            |
|          | assigned to `Romain Raffault   |                 |                                |
|          | <…>`__) [▶] **☎ Talk** → [⚹]   |                 |                                |
|          | [☾] [☉] [⚒] [☐] [☑] [☒] [⧖]    |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
| 30       | `#22 (How can I see where      |                 | [▶] **⚒ Working** → [⚹] [☾]    |
|          | bar?) <…>`__ [▶] **⚒ Working** |                 | [☎] [☉] [☐] [☑] [☒] [⧖]        |
|          | → [⚹] [☾] [☎] [☉] [☐] [☑] [☒]  |                 |                                |
|          | [⧖]                            |                 |                                |
+----------+--------------------------------+-----------------+--------------------------------+
<BLANKLINE>




The backlog
===========

The :class:`TicketsBySite` panel shows all the tickets for a given project. It
is a scrum backlog.

>>> pypi = subscriptions.Subscription.objects.get(ref="welket")
>>> rt.login("robin").show(
...     tickets.TicketsByOrder, pypi, max_width=40, display_mode="grid")
... #doctest: -REPORT_UDIFF -SKIP +ELLIPSIS +NORMALIZE_WHITESPACE
+--------------------+------------------------------------------+--------------+-----------+------+
| Priority           | Ticket                                   | Planned time | Regular   | Free |
+====================+==========================================+==============+===========+======+
| 50                 | `#1 (Föö fails to bar when baz) <…>`__ ( |              |           |      |
|                    | 50 by `Jean <…>`__ in `Developers        |              |           |      |
|                    | <…>`__) [▶] **⚹ New** → [☾] [☎] [☉] [⚒]  |              |           |      |
|                    | [☐] [☑] [⧖]                              |              |           |      |
+--------------------+------------------------------------------+--------------+-----------+------+
| 30                 | `#91 (Cannot delete foo) <…>`__ (by      |              |           |      |
|                    | `Robin Rood <…>`__ in `Developers <…>`__ |              |           |      |
|                    | assigned to `Rolf Rompen <…>`__) [▶] **⚹ |              |           |      |
|                    | New** → [☾] [☎] [☉] [⚒] [☐] [☑] [⧖]      |              |           |      |
+--------------------+------------------------------------------+--------------+-----------+------+
| 30                 | `#83 (Misc optimizations in Baz) <…>`__  |              | 65:18     |      |
|                    | (by `Rolf Rompen <…>`__ in `Sales team   |              |           |      |
|                    | <…>`__ assigned to `Luc <…>`__) [▶] **☎  |              |           |      |
|                    | Talk** → [⚹] [☾] [☉] [⚒] [☐] [☑] [☒] [⧖] |              |           |      |
+--------------------+------------------------------------------+--------------+-----------+------+
| 30                 | `#76 (How to get bar from foo) <…>`__    |              |           |      |
|                    | (by `Rolf Rompen <…>`__) [▶] **⚒         |              |           |      |
|                    | Working** → [⚹] [☾] [☎] [☉] [☐] [☑] [☒]  |              |           |      |
|                    | [⧖]                                      |              |           |      |
+--------------------+------------------------------------------+--------------+-----------+------+
| 30                 | `#46 (How can I see where bar?) <…>`__   |              |           |      |
|                    | (by `Mathieu <…>`__) [▶] **⚹ New** → [☾] |              |           |      |
|                    | [☎] [☉] [☐] [☑] [⧖]                      |              |           |      |
+--------------------+------------------------------------------+--------------+-----------+------+
| 30                 | `#38 (Bar cannot baz) <…>`__ (by `Marc   |              |           |      |
|                    | <…>`__) [▶] **☎ Talk** → [⚹] [☾] [☉] [☐] |              |           |      |
|                    | [☑] [☒] [⧖]                              |              |           |      |
+--------------------+------------------------------------------+--------------+-----------+------+
| 30                 | `#31 (Cannot delete foo) <…>`__ (by      |              |           |      |
|                    | `Marc <…>`__ in `Developers <…>`__       |              |           |      |
|                    | assigned to `Rolf Rompen <…>`__) [▶] **⚒ |              |           |      |
|                    | Working** → [⚹] [☾] [☎] [☉] [☐] [☑] [☒]  |              |           |      |
|                    | [⧖]                                      |              |           |      |
+--------------------+------------------------------------------+--------------+-----------+------+
| **Total (7 rows)** |                                          |              | **65:18** |      |
+--------------------+------------------------------------------+--------------+-----------+------+
<BLANKLINE>



Links between tickets
=====================

A ticket inherits from :class:`Hierarchical`, which means that it has a field
:attr:`parent`, which points to another ticket, which is the "parent" of this
one.

.. class:: TicketsByParent

  Shows the tickets that have this ticket as their immediate parent.

..
  Here are the tickets that are being used as parent by some other ticket in the
  demo database:

  >>> set([o.parent.pk for o in tickets.Ticket.objects.filter(parent__isnull=False)])
  {1, 2, 3, 4, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 27, 28, 30, 31, 32, 33, 34, 36, 37, 38, 40, 42, 43, 44, 45, 46, 48, 49, 50, 51, 54, 55, 56, 57, 58, 60, 61, 62, 63, 64, 66, 67, 68, 69, 70, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 84, 85, 86, 87, 88, 90, 92, 93, 94, 96, 97, 98, 99, 100, 102, 103, 105, 106, 108, 109, 110, 111, 112, 114, 115}

>>> obj = tickets.Ticket.objects.get(id=20)
>>> rt.login("robin").show(tickets.TicketsByParent, obj, display_mode="grid")
... #doctest: +REPORT_UDIFF
========== ==== ============================= ==========================================
 Priority   ID   Summary                       Assign to
---------- ---- ----------------------------- ------------------------------------------
 30         21   Irritating message when bar   **jean**, **mathieu**, robin, **nobody**
========== ==== ============================= ==========================================
<BLANKLINE>


Filtering tickets
=================

:ref:`noi` modifies the list of the parameters you can use for filterings
tickets be setting a custom :attr:`params_layout`.

>>> show_fields(tickets.AllTickets, all=True)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Author (user) : The author or reporter of this ticket. The user who reported this
  ticket to the database and is responsible for managing it.
- End user (end_user) : Only rows concerning this end user.
- Assigned to (assigned_to) : Only tickets with this user assigned.
- Not assigned to (not_assigned_to) : Only that this user is not assigned to.
- Interesting for (interesting_for) : Only tickets interesting for this partner.
- Subscription (order) : The business document used by both partners as reference for invoicing this ticket.
- State (state) : Only rows having this state.
- Assigned (show_assigned) : Show only (or hide) tickets that are assigned to somebody.
- Active (show_active) : Show only (or hide) tickets which are active (i.e. state is Talk
  or ToDo).
- To do (show_todo) : Show only (or hide) tickets that are todo (i.e. state is New
  or ToDo).
- Private (show_private) : Show only (or hide) tickets that are marked private.
- Date from (start_date) : Start of observed date range
- until (end_date) : End of observed date range
- Observed event (observed_event) :
- Has reference (has_ref) :
- Commented Last (last_commenter) : Only tickets that have this use commenting last.
- Not Commented Last (not_last_commenter) : Only tickets where this use is not the last commenter.



Change observers
================

A comment is a :class:`ChangeNotifier` that forwards its owner's change
observers:

>>> ar = rt.login('robin')

>>> from lino.modlib.notify.mixins import ChangeNotifier
>>> obj = comments.Comment.objects.filter(group__isnull=False).first()
>>> obj.owner
Group #3 ('Sales team')
>>> isinstance(obj.owner, ChangeNotifier)
True
>>> list(obj.get_change_observers())
... #doctest: +REPORT_UDIFF -SKIP +ELLIPSIS +NORMALIZE_WHITESPACE
[(User #6 ('Luc'), <notify.MailModes.often:often>), (User #3 ('Romain
Raffault'), <notify.MailModes.often:often>)]

>>> list(obj.get_change_observers()) == list(obj.owner.get_change_observers())
True

When the owner of a comment is not a ChangeNotifier, the comment has no change
observers:

>>> obj = comments.Comment.objects.filter(group__isnull=True).first()
>>> obj.owner
Company #95 ('Number Three')
>>> isinstance(obj.owner, ChangeNotifier)
False
>>> list(obj.get_change_observers())
[]
>>> list(obj.owner.get_change_observers())
Traceback (most recent call last):
...
AttributeError: 'Company' object has no attribute 'get_change_observers'



>>> list(comments.Comment.objects.get(pk=155).get_change_observers())
... #doctest: +REPORT_UDIFF -SKIP +ELLIPSIS +NORMALIZE_WHITESPACE
[]

Don't read on
=============

>>> print(tickets.Ticket.objects.get(pk=45))
#45 (Irritating message when bar)

>>> test_client.force_login(rt.login('robin').user)
>>> def mytest(k):
...     url = '/api/tickets/Tickets/{}?dm=list&fmt=json&lv=1697917143.868&mjsts=1695264043.076&mk=0&pv=1&pv&pv&pv&pv&pv&pv&pv&pv&pv&pv&pv=24.10.2023&pv=24.10.2023&pv=10&pv&pv&pv&rp=weak-key-4&ul=en&wt=d'.format(k)
...     res = test_client.get(url)
...     print(res)

>>> settings.SITE.catch_layout_exceptions = True
>>> mytest("45")  #doctest: -SKIP +NORMALIZE_WHITESPACE +ELLIPSIS
Error during ApiElement.get(): Invalid request for '45' on tickets.Tickets (Unresolved value '10' (<class 'str'>) for tickets.TicketEvents (set Site.strict_choicelist_values to False to ignore this))
Unresolved value '10' (<class 'str'>) for tickets.TicketEvents (set Site.strict_choicelist_values to False to ignore this)
Traceback (most recent call last):
...
lino.core.exceptions.UnresolvedChoice: Unresolved value '10' (<class 'str'>) for tickets.TicketEvents (set Site.strict_choicelist_values to False to ignore this)
Not Found: /api/tickets/Tickets/45
<HttpResponseNotFound status_code=404, "text/html; charset=utf-8">

>>> settings.SITE.catch_layout_exceptions = False


>>> obj = tickets.Ticket.objects.get(pk=115)
>>> obj.state
<tickets.TicketStates.closed:50>

>>> url = f"/api/tickets/ActiveTickets/{obj.pk}?dm=detail&fmt=json"

>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url)
>>> d = json.loads(res.content.decode())
>>> pprint(d)
{'alert': False,
 'message': 'Row 115 is not visible here.<br>But you can see it in <a '
            'href="javascript:Lino.tickets.Tickets.detail.run(null,{ '
            '&quot;base_params&quot;: {  }, &quot;param_values&quot;: { '
            '&quot;assigned_to&quot;: null, &quot;assigned_toHidden&quot;: '
            'null, &quot;end_date&quot;: null, &quot;end_user&quot;: null, '
            '&quot;end_userHidden&quot;: null, &quot;has_ref&quot;: null, '
            '&quot;has_refHidden&quot;: null, &quot;interesting_for&quot;: '
            'null, &quot;interesting_forHidden&quot;: null, '
            '&quot;last_commenter&quot;: null, '
            '&quot;last_commenterHidden&quot;: null, '
            '&quot;not_assigned_to&quot;: null, '
            '&quot;not_assigned_toHidden&quot;: null, '
            '&quot;not_last_commenter&quot;: null, '
            '&quot;not_last_commenterHidden&quot;: null, '
            '&quot;observed_event&quot;: null, '
            '&quot;observed_eventHidden&quot;: null, &quot;order&quot;: null, '
            '&quot;orderHidden&quot;: null, &quot;show_active&quot;: null, '
            '&quot;show_activeHidden&quot;: null, &quot;show_assigned&quot;: '
            'null, &quot;show_assignedHidden&quot;: null, '
            '&quot;show_private&quot;: null, &quot;show_privateHidden&quot;: '
            'null, &quot;show_todo&quot;: null, &quot;show_todoHidden&quot;: '
            'null, &quot;start_date&quot;: null, &quot;state&quot;: null, '
            '&quot;stateHidden&quot;: null, &quot;user&quot;: null, '
            '&quot;userHidden&quot;: null }, &quot;record_id&quot;: 115 })" '
            'style="text-decoration:none">Tickets</a>.',
 'success': False,
 'title': '<a href="javascript:Lino.tickets.ActiveTickets.grid.run(null,{ '
          '&quot;base_params&quot;: {  }, &quot;param_values&quot;: { '
          '&quot;assigned_to&quot;: null, &quot;assigned_toHidden&quot;: null, '
          '&quot;end_date&quot;: null, &quot;end_user&quot;: null, '
          '&quot;end_userHidden&quot;: null, &quot;has_ref&quot;: null, '
          '&quot;has_refHidden&quot;: null, &quot;interesting_for&quot;: null, '
          '&quot;interesting_forHidden&quot;: null, '
          '&quot;last_commenter&quot;: null, &quot;last_commenterHidden&quot;: '
          'null, &quot;not_assigned_to&quot;: null, '
          '&quot;not_assigned_toHidden&quot;: null, '
          '&quot;not_last_commenter&quot;: null, '
          '&quot;not_last_commenterHidden&quot;: null, '
          '&quot;observed_event&quot;: null, &quot;observed_eventHidden&quot;: '
          'null, &quot;order&quot;: null, &quot;orderHidden&quot;: null, '
          '&quot;show_active&quot;: &quot;Yes&quot;, '
          '&quot;show_activeHidden&quot;: &quot;y&quot;, '
          '&quot;show_assigned&quot;: null, &quot;show_assignedHidden&quot;: '
          'null, &quot;show_private&quot;: null, '
          '&quot;show_privateHidden&quot;: null, &quot;show_todo&quot;: null, '
          '&quot;show_todoHidden&quot;: null, &quot;start_date&quot;: null, '
          '&quot;state&quot;: null, &quot;stateHidden&quot;: null, '
          '&quot;user&quot;: null, &quot;userHidden&quot;: null } })" '
          'style="text-decoration:none">Active tickets</a>'}
