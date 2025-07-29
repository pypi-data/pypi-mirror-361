.. doctest docs/specs/voga/usertypes.rst
.. _voga.specs.profiles:

=============
User types
=============

This page documents the user types available in Lino Voga.
It uses the roger demo, the most complex variant.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.voga2.startup import *


Site manager
==================

Robin is a :term:`site manager`, he has a complete menu:

>>> ses = rt.login('robin')
>>> ses.user.user_type
<users.UserTypes.admin:900>
>>> show_menu('robin')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Contacts : Persons, Organizations, Partner Lists
- Office : Data problem messages assigned to me, My Notes, My Outbox, My Excerpts, My Upload files
- Calendar : My appointments, Overdue appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments, Upcoming events, Bookings, Calendar
- Activities : Participants, Instructors, -, Courses, Hikes, Journeys, -, Topics, Activity lines, -, Pending requested enrolments, Pending confirmed enrolments
- Sales : My invoicing plan, Sales invoices (SLS), Sales credit notes (SLC)
- Publisher : Pages
- Accounting :
  - Purchases : Purchase invoices (PRC)
  - Wages : Paychecks (SAL)
  - Financial : Payment orders Bestbank (PMO), Cash book (CSH), Bestbank (BNK)
  - VAT : VAT declarations (VAT)
  - Miscellaneous transactions : Miscellaneous transactions (MSC), Preliminary transactions (PRE)
- Reports :
  - Activities : Status Report
  - Sales : Due invoices
  - Accounting : Debtors, Creditors
  - VAT : Intra-Community purchases, Intra-Community sales
- Configure :
  - System : Users, Site configuration, System tasks
  - Places : Countries, Places
  - Contacts : Legal forms, Functions, List Types
  - Calendar : Calendars, Rooms, Recurring events, Guest roles, Calendar entry types, Recurrency policies, Remote Calendars, Planner rows
  - Activities : Activity types, Instructor types, Participant types, Timetable Slots
  - Fees : Fees, Fee categories
  - Sales : Paper types, Flatrates, Follow-up rules, Invoicing tasks
  - Office : Note Types, Event Types, Excerpt Types, Library volumes, Upload types
  - Publisher : Special pages
  - Accounting : Fiscal years, Accounting periods, Accounts, Journals, Payment terms
- Explorer :
  - System : Authorities, User types, User roles, Data checkers, Data problem messages, Changes, content types, Background procedures
  - Contacts : Contact persons, Partners, Contact detail types, Contact details, List memberships
  - Calendar : Calendar entries, Tasks, Presences, Subscriptions, Entry states, Presence states, Task states, Planner columns, Display colors
  - Activities : Activities, Enrolments, Enrolment states, Course layouts, Activity states
  - Sales : Price factors, Trading rules, Trading invoices, Trading invoice items, Invoicing plans
  - Financial : Bank statements, Journal entries, Payment orders
  - SEPA : Bank accounts
  - Office : Notes, Outgoing messages, Attachments, Mentions, Excerpts, Upload files, Upload areas
  - Accounting : Common accounts, Match rules, Vouchers, Voucher types, Movements, Trade types, Journal groups
  - VAT : Special Belgian VAT declarations, Declaration fields, VAT areas, VAT regimes, VAT classes, VAT columns, Ledger invoices, VAT rules
- Site : About, User sessions


Monique is a secretary.

>>> print(rt.login('monique').user.user_type)
200 (Secretary)

>>> show_menu('monique')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Contacts : Persons, Organizations, Partner Lists
- Office : Data problem messages assigned to me, My Notes, My Outbox, My Excerpts, My Upload files
- Calendar : My appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments, Upcoming events, Calendar
- Activities : Participants, Instructors, -, Courses, Hikes, Journeys, -, Activity lines, -, Pending requested enrolments, Pending confirmed enrolments
- Sales : My invoicing plan, Sales invoices (SLS), Sales credit notes (SLC)
- Publisher : Pages
- Accounting :
  - Purchases : Purchase invoices (PRC)
  - Wages : Paychecks (SAL)
  - Financial : Payment orders Bestbank (PMO), Cash book (CSH), Bestbank (BNK)
  - VAT : VAT declarations (VAT)
  - Miscellaneous transactions : Miscellaneous transactions (MSC), Preliminary transactions (PRE)
- Reports :
  - Activities : Status Report
  - Sales : Due invoices
  - Accounting : Debtors, Creditors
  - VAT : Intra-Community purchases, Intra-Community sales
- Configure :
  - System : Site configuration, System tasks
  - Places : Countries, Places
  - Contacts : Legal forms, Functions, List Types
  - Calendar : Guest roles
  - Activities : Activity types, Instructor types, Participant types
  - Fees : Fees, Fee categories
  - Sales : Flatrates, Follow-up rules
  - Publisher : Special pages
- Explorer :
  - System : Data checkers, Data problem messages, Changes, content types, Background procedures
  - Contacts : Contact persons, Partners, Contact details, List memberships
  - Calendar : Calendar entries, Presences, Entry states, Presence states, Task states, Planner columns, Display colors
  - Activities : Activities, Enrolments
  - Sales : Price factors, Trading invoices
  - Office : Mentions
  - VAT : Special Belgian VAT declarations, Declaration fields, Ledger invoices, VAT rules
- Site : About


Marianne is a "simple user".

>>> print(rt.login('marianne').user.user_type)
100 (User)

>>> show_menu('marianne')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Contacts : Persons, Organizations, Partner Lists
- Office : Data problem messages assigned to me, My Notes, My Outbox, My Excerpts, My Upload files
- Calendar : My appointments, My unconfirmed appointments, My tasks, My guests, My presences, My overdue appointments, Upcoming events, Calendar
- Activities : Participants, Instructors, -, Courses, Hikes, Journeys, -, Activity lines
- Sales : My invoicing plan, Sales invoices (SLS), Sales credit notes (SLC)
- Publisher : Pages
- Accounting :
  - Purchases : Purchase invoices (PRC)
  - Wages : Paychecks (SAL)
  - Financial : Payment orders Bestbank (PMO), Cash book (CSH), Bestbank (BNK)
  - VAT : VAT declarations (VAT)
  - Miscellaneous transactions : Miscellaneous transactions (MSC), Preliminary transactions (PRE)
- Reports :
  - Activities : Status Report
  - Sales : Due invoices
  - Accounting : Debtors, Creditors
  - VAT : Intra-Community purchases, Intra-Community sales
- Configure :
  - Activities : Activity types, Instructor types, Participant types
  - Sales : Flatrates, Follow-up rules
- Explorer :
  - Contacts : Partners
  - Sales : Price factors, Trading invoices
  - VAT : Special Belgian VAT declarations, Declaration fields, Ledger invoices, VAT rules
- Site : About

>>> show_menu('tom')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Calendar : Upcoming events
- Activities : My courses given
- Site : About
