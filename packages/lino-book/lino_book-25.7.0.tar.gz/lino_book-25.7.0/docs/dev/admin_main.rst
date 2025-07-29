.. doctest docs/dev/admin_main.rst
.. _dev.admin_main:

========================
More about the main page
========================

This page explains how to customize the elements of the :term:`main page` of a
Lino application.

.. contents::
  :local:


Vocabulary
==========

.. glossary::

  dashboard item

    An individual item of the :term:`dashboard`, rendered directly (inline) into
    the main page because it is considered an important entry point.

.. include:: /../docs/shared/include/tested.rst

Code snippets in this document are tested using the
:mod:`lino_book.projects.noi1e` demo project.

>>> from lino_book.projects.noi1e.startup import *


Quick links
===========

As the :term:`application developer` you define quick links by overriding the
:meth:`setup_quicklinks <lino.core.site.Site.setup_quicklinks>` methods of your
:class:`Site <lino.core.site.Site>` class.

For example the :mod:`lino.modlib.about` plugin says::

  class Plugin(Plugin):

      def get_quicklinks(site):
          yield 'about.SiteSearch'

Or the :mod:`lino_noi.lib.noi.settings` module says::

  class Site(Site):
      ...
      def setup_quicklinks(self, user, tb):
          super().setup_quicklinks(user, tb)
          tb.add_action(self.models.tickets.RefTickets)
          ...
          tb.add_action(
              self.models.tickets.AllTickets.insert_action,
              label=_("Submit a ticket"))
          ...
          a = self.models.users.MySettings.default_action
          tb.add_instance_action(user, action=a, label=_("My settings"))



>>> pprint(settings.SITE.quicklinks.items)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[<lino.core.actions.WrappedAction users_Me_detail ('My settings')>,
 <lino.core.actions.WrappedAction calview_WeeklyView_detail ('Calendar')>,
 <lino.core.actions.WrappedAction tickets_UnassignedTickets_grid>,
 <lino.core.actions.WrappedAction tickets_ActiveTickets_grid>,
 <lino.core.actions.WrappedAction tickets_AllTickets_grid>,
 <lino.core.actions.WrappedAction tickets_AllTickets_insert ('Submit new ticket')>,
 <lino.core.actions.WrappedAction search_SiteSearch_grid>]

The :xfile:`admin_main.html` template calls
:meth:`lino.core.Site.get_quicklink_items` to retrieve and then render this
information.

>>> ar = rt.login("robin")
>>> user = ar.get_user()
>>> for ql in settings.SITE.get_quicklink_items(user.user_type):
...     print(tostring(ar.menu_item_button(ql)))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
<a href="…" title="Edit your user preferences.">My settings</a>
<a href="…" title="Open a detail window on records of calview.">Calendar</a>
<a href="…" title="Base class for all tables of tickets.">Unassigned Tickets</a>
<a href="…" title="Show all tickets that are in an active state.">Active tickets</a>
<a href="…" title="Shows all tickets.">All tickets</a>
<a href="…" title="Insert a new Ticket.">Submit new ticket</a>
<a href="…" title="A virtual table that searches in all database tables.">Search</a>


Welcome messages
================

As the application developer you have several methods to define :term:`welcome
messages <welcome message>`:

- Set :attr:`welcome_message_when_count
  <lino.core.actors.Actor.welcome_message_when_count>` of some table
  to some value (usually ``0``).

  For example the :mod:`lino_xl.lib.tickets.TicketsToTriage` plugin uses this to
  define the "You have X items in Tickets to triage" message.

- Define a **custom welcome message** by overwriting  :meth:`add_welcome_handler
  <lino.core.site.Site.add_welcome_handler>` in the :class:`Site` class of your
  application.

  For example the "You are busy with..." message in :ref:`noi` is
  :mod:`lino_xl.lib.working`.  Or :mod:`lino_xl.lib.stars` defines the "Your
  stars are" message.

The :xfile:`admin_main.html` calls :meth:`get_welcome_messages
<lino.core.site.Site.get_welcome_messages>`.  This code inserts the "welcome
messages" for this user on this site. :meth:`get_welcome_messages
<lino.core.site.Site.get_welcome_messages>` returns an etree element (see
:mod:`etgen.html`).

>>> ar = rt.login("robin")
>>> print(tostring(settings.SITE.get_welcome_messages(ar)))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
<span>Your nicknamed Tickets are <a href="…">daily</a>, <a href="…">friday</a>,
<a href="…">inbox</a>.</span><p><span><a href="…">Jean</a> is working on: <a
href="…" title="Irritating message when bar">#57 (Irritating message when
bar)</a>, <a href="…" title="Bars have no foo">#63 (Bars have no
foo)</a>.</span><br/><span><a href="…">Luc</a> is working on: <a href="…"
title="Misc optimizations in Baz">#59 (Misc optimizations in Baz)</a>, <a
href="…" title="Foo never bars">#65 (Foo never bars)</a>.</span><br/><span><a
href="…">Mathieu</a> is working on: <a href="…" title="Irritating message when
bar">#45 (Irritating message when bar)</a>, <a href="…" title="Bars have no
foo">#51 (Bars have no foo)</a>, <a href="…" title="Irritating message when
bar">#57 (Irritating message when bar)</a>, <a href="…" title="Bars have no
foo">#63 (Bars have no foo)</a>.</span></p><span>You have <b>13 items in Tickets
to triage</b>.</span>

.. _dev.dasboard:

The dashboard
=============

As the :term:`application developer` you define which actors are available as
:term:`dashboard item` for your application.  You can do this in two different
ways:

- override the :meth:`get_dashboard_items
  <lino.core.plugin.Plugin.get_dashboard_items>` of your :class:`Plugin
  <lino.core.plugin.Plugin>` classes.

- override the
  :meth:`get_dashboard_items
  <lino.core.site.Site.get_dashboard_items>`
  of your :class:`Site <lino.core.site.Site>` class.

This list is *hard-coded* per application and *applies to all users*. But Lino
respects view permissions, i.e. an item will appear only if the user has
permission to see it. For each dashboard item you can specify certain options to
influence how Lino renders them. For example they usually don't appear if the
table contains no data.

Independently of how you define the dashboard items for your application, you
can additionally opt to install the :mod:`lino.modlib.dashboard` plugin.


List of available dashboard items
=================================

The list of available dashboard items exists also without this plugin.

>>> ar = rt.login("robin")
>>> user = ar.get_user()
>>> pprint(list(settings.SITE.get_dashboard_items(user)))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[lino_xl.lib.cal.ui.MyTasks,
 lino.core.dashboard.ActorItem(cal.MyEntries,header_level=2,min_count=None),
 lino_xl.lib.cal.ui.MyOverdueAppointments,
 lino_xl.lib.cal.ui.MyUnconfirmedAppointments,
 lino_xl.lib.cal.ui.MyPresences,
 lino_xl.lib.cal.ui.UpcomingEvents,
 lino_xl.lib.calview.ui.DailyPlanner,
 lino.modlib.comments.ui.RecentComments,
 lino_xl.lib.tickets.ui.MyTickets,
 lino_xl.lib.tickets.ui.TicketsToTriage,
 lino_xl.lib.tickets.ui.MyTicketsToWork,
 lino_xl.lib.working.ui.WorkedHours,
 lino_xl.lib.groups.models.MyGroups,
 lino_xl.lib.accounting.ui.MyMovements,
 lino_xl.lib.accounting.ui.JournalsOverview]


Note that in practice you would probably prefer to not use above list directly,
but rather its "processed" form, stored in the user's preferences:

>>> pprint(user.get_preferences().dashboard_items)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[lino.core.dashboard.ActorItem(cal.MyTasks,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(cal.MyEntries,header_level=2,min_count=None),
 lino.core.dashboard.ActorItem(cal.MyOverdueAppointments,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(cal.MyUnconfirmedAppointments,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(cal.MyPresences,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(calview.DailyPlanner,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(comments.RecentComments,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(tickets.MyTickets,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(tickets.TicketsToTriage,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(tickets.MyTicketsToWork,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(working.WorkedHours,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(groups.MyGroups,header_level=2,min_count=1),
 lino.core.dashboard.ActorItem(accounting.JournalsOverview,header_level=2,min_count=1)]


See :doc:`/specs/dashboard`.



Behind the scenes
=================

The content of the main page is generated from the :xfile:`admin_main.html`
template.

.. xfile:: admin_main_base.html
.. xfile:: admin_main.html

This is the template used to generate the content of the main page.
It is split into two files :srcref:`admin_main.html
<lino/config/admin_main.html>` and :srcref:`admin_main_base.html
<lino/config/admin_main_base.html>`.

For illustration compare the content of the latter template with its
result in the following screenshots (taken from the :mod:`noi1e
<lino_book.projects.noi1e>` demo project which runs :ref:`noi`).

.. figure:: /apps/noi/admin_main_000.png
   :width: 80 %

   Main page for AnonymousUser.

.. figure:: /apps/noi/admin_main_900.png
   :width: 80 %

   Main page for user ``robin``.

Customizing the main page
===========================

You may define a custom :xfile:`admin_main.html` template, as we did
in :doc:`/dev/polls/index`. But this was rather an exercise for pedagogical
reasons than something we would recommend to do for application developers.

You may even go further and override the :meth:`get_main_html
<lino.core.site.Site.get_main_html>` method of your :class:`Site
<lino.core.site.Site>` class to return your own html.


..
  >>> dbhash.check_virgin()
