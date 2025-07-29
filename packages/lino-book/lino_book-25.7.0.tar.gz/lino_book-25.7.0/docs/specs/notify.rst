.. doctest docs/specs/notify.rst
.. _book.specs.notify:

==================================
``notify``: Notification framework
==================================

The :mod:`lino.modlib.notify` plugin adds a notification framework to your
:term:`Lino application`.

We assume that you have read the end-user documentation in
:ref:`ug.plugins.notify`.

.. currentmodule:: lino_book.projects

You can play with notifications in the demo projects :mod:`chatter`,
:mod:`noi1e` and :mod:`noi1r`. Open two browsers windows (one of them private)
and sign in as two different users. Then write a comment in one window and note
the desktop notification received by the other user.


.. currentmodule:: lino.modlib.notify

Code snippets on this page are tested in the :ref:`chatter
<book.projects.chatter>` demo project.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.chatter.settings')
>>> from lino.api.doctest import *


Concepts
========

This page will introduce the following new concepts:

.. glossary::

  notification message

    Stored in :class:`Message`.

  push notification

    A technology used to implement :term:`desktop notifications`.

    https://rossta.net/blog/using-the-web-push-api-with-vapid.html

  push subscription

    The fact that a :term:`site user` has given permission to some of their
    browsers to show :term:`desktop notifications` for this site.

Usage
=====

Add :mod:`lino.modlib.notify` to your
:meth:`lino.core.site.Site.get_installed_plugins`.

To emit a :term:`notification message` from your application code, you can

- call :meth:`Message.emit_notification`
- call :meth:`Message.emit_broadcast_notification`.
- have your model(s) inherit from :class:`ChangeNotifier`.
- add actions that inherit from :class:`NotifyingAction`.

You can use this plugin without enabling :term:`desktop notifications`. In that
case the :term:`site users <site user>` will receive only email notifications
and/or dashboard notifications.

How to activate desktop notifications
=====================================

To enable desktop notifications, there are some requirements:

- Set :attr:`use_linod <lino.core.site.Site.use_linod>` to `True` to enable
  desktop notification that is done through websockets or the push-api.
  **use_linod** will enable websockets notifications by default but to have
  notifications through push-api
  set :data:`use_push_api <lino.modlib.notify.use_push_api>` to `True`.
  See: :mod:`lino.modlib.linod`.

- Run :cmd:`pm install` in order to install additional Python modules
  (`pywebpush <https://pypi.org/project/pywebpush/>`__ and/or `django-channels
  <https://pypi.org/project/django-channels/>`__ and `channels-redis
  <https://pypi.org/project/channels-redis/>`_).

- To test push notifications on a development server, you must
  `Set up a public URL for your development server`_.

- To enable push notifications on a :term:`production site`, the :term:`server
  administrator` must also `Configure VAPID credentials`_.


Set up a public URL for your development server
===============================================

The :term:`Push API` requires your web server to be publicly reachable via
https.  One method to do this for a development server is to use ngrok.

Install ngrok: https://ngrok.com/download

Run ngrok::

  $ ngrok http 8000

  ngrok by @inconshreveable                                                                                                                                     (Ctrl+C to quit)

  Session Status                online
  Account                       joe@example.com (Plan: Free)
  Version                       2.3.40
  Region                        United States (us)
  Web Interface                 http://127.0.0.1:4040
  Forwarding                    http://b3735559b89b.ngrok.io -> http://localhost:8000
  Forwarding                    https://b3735559b89b.ngrok.io -> http://localhost:8000

  Connections                   ttl     opn     rt1     rt5     p50     p90
                                268     0       0.00    0.00    0.50    1.39

In most terminals you can then Ctrl-click on the https://b3735559b89b.ngrok.io
URL to open your browser on it.


Configure VAPID credentials
===========================

See https://github.com/web-push-libs/vapid/tree/main/python


More about the Push API
=======================

.. glossary::

  Push API

    A technology for delivering :term:`desktop notifications`.

    Currently a `Working Draft published by the W3C Web
    Applications Working Group <https://www.w3.org/TR/push-api/>`__, and intended to
    become a W3C Recommendation.

Unlike alternative technologies like `WebSockets
<https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API>`__ or
`server-sent events
<https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events>`__,
the :term:`Push API` uses a third-party push server.


Subject and body of a notification message
==========================================

As an :term:`application developer` you should understand the different
meanings of "subject" and "body":

- The body is expected to be a self-sufficient and complete description of the event.
  If a message has a *body*, then the *subject* is **not** being displayed
  in the MyMessages summary.

- The subject might contain limited rich text (text formatting, links) but be
  aware that this formatting may get lost when the message is sent as an email
  or as a desktop notification.


Notification messages
=====================

You can use :menuselection:`Explorer --> System --> Notification messages` to
see all notification messages.

>>> dd.today()
datetime.date(2024, 4, 6)


>>> # run_menu_command("Explorer --> System --> Notification messages")
>>> rt.show('notify.AllMessages')  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
============================ ============================================================== ================ ============= ====== ===============...===
 Created                      Subject                                                        Recipient        Reply to      seen   sent
---------------------------- -------------------------------------------------------------- ---------------- ------------- ------ ---------------...---
 2024-04-05 05:48:00          Broadcast message                                                                                    2024-04-05 ...
 2024-04-05 05:48:00          Welcome on board, Andreas.                                     Andy                                  2024-04-05 05:48:00
 2024-04-05 05:48:00          Welcome on board, Albert.                                      Bert                                  2024-04-05 05:48:00
 2024-04-05 05:48:00          Welcome on board, Chloe.                                       Chloe Cleoment                        2024-04-05 05:48:00
 2024-04-05 05:48:00          Welcome on board, Robin.                                       Robin Rood                            2024-04-05 05:48:00
 2024-04-06 ...               Andy commented on Harry Potter                                 Bert             Comment #7
 2024-04-06 ...               Bert commented on Harry Potter                                 Andy             Comment #8
 2024-04-06 ...               Chloe Cleoment commented on Harry Potter                       Andy             Comment #9
 ...                          Chloe Cleoment commented on Harry Potter                       Bert             Comment #9
 ...                          Robin Rood commented on Harry Potter                           Andy             Comment #10
 ...                          Robin Rood commented on Harry Potter                           Bert             Comment #10
 ...                          Andy commented on Harry Potter                                 Bert             Comment #11
 ...                          Bert commented on Harry Potter                                 Andy             Comment #12
 ...                          Chloe Cleoment commented on Harry Potter                       Andy             Comment #13
 ...                          Chloe Cleoment commented on Harry Potter                       Bert             Comment #13
 ...                          Robin Rood commented on Star Trek                              Chloe Cleoment   Comment #14
 ...                          Andy commented on Star Trek                                    Chloe Cleoment   Comment #15
 ...                          Andy commented on Star Trek                                    Robin Rood       Comment #15
 ...                          Bert commented on Star Trek                                    Chloe Cleoment   Comment #16
 ...                          Bert commented on Star Trek                                    Robin Rood       Comment #16
 ...                          Chloe Cleoment commented on Star Trek                          Robin Rood       Comment #17
 ...                          Robin Rood commented on Star Trek                              Chloe Cleoment   Comment #18
 ...                          Andy commented on Star Trek                                    Chloe Cleoment   Comment #19
 ...                          Andy commented on Star Trek                                    Robin Rood       Comment #19
 ...                          Bert commented on Star Trek                                    Chloe Cleoment   Comment #20
 ...                          Bert commented on Star Trek                                    Robin Rood       Comment #20
 ...                          Chloe Cleoment commented on Hitchhiker's Guide to the Galaxy   Andy             Comment #21
 ...                          Chloe Cleoment commented on Hitchhiker's Guide to the Galaxy   Bert             Comment #21
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Andy             Comment #22
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Bert             Comment #22
 ...                          Andy commented on Hitchhiker's Guide to the Galaxy             Bert             Comment #23
 ...                          Bert commented on Hitchhiker's Guide to the Galaxy             Andy             Comment #24
 ...                          Chloe Cleoment commented on Hitchhiker's Guide to the Galaxy   Andy             Comment #25
 ...                          Chloe Cleoment commented on Hitchhiker's Guide to the Galaxy   Bert             Comment #25
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Andy             Comment #26
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Bert             Comment #26
 ...                          Andy commented on Hitchhiker's Guide to the Galaxy             Bert             Comment #27
 ...                          Bert commented on Harry Potter                                 Andy             Comment #28
 ...                          Chloe Cleoment commented on Harry Potter                       Andy             Comment #29
 ...                          Chloe Cleoment commented on Harry Potter                       Bert             Comment #29
 ...                          Robin Rood commented on Harry Potter                           Andy             Comment #30
 ...                          Robin Rood commented on Harry Potter                           Bert             Comment #30
 ...                          Andy commented on Harry Potter                                 Bert             Comment #31
 ...                          Bert commented on Harry Potter                                 Andy             Comment #32
 ...                          Chloe Cleoment commented on Harry Potter                       Andy             Comment #33
 ...                          Chloe Cleoment commented on Harry Potter                       Bert             Comment #33
 ...                          Robin Rood commented on Harry Potter                           Andy             Comment #34
 ...                          Robin Rood commented on Harry Potter                           Bert             Comment #34
 ...                          Andy commented on Star Trek                                    Chloe Cleoment   Comment #35
 ...                          Andy commented on Star Trek                                    Robin Rood       Comment #35
 ...                          Bert commented on Star Trek                                    Chloe Cleoment   Comment #36
 ...                          Bert commented on Star Trek                                    Robin Rood       Comment #36
 ...                          Chloe Cleoment commented on Star Trek                          Robin Rood       Comment #37
 ...                          Robin Rood commented on Star Trek                              Chloe Cleoment   Comment #38
 ...                          Andy commented on Star Trek                                    Chloe Cleoment   Comment #39
 ...                          Andy commented on Star Trek                                    Robin Rood       Comment #39
 ...                          Bert commented on Star Trek                                    Chloe Cleoment   Comment #40
 ...                          Bert commented on Star Trek                                    Robin Rood       Comment #40
 ...                          Chloe Cleoment commented on Star Trek                          Robin Rood       Comment #41
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Andy             Comment #42
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Bert             Comment #42
 ...                          Andy commented on Hitchhiker's Guide to the Galaxy             Bert             Comment #43
 ...                          Bert commented on Hitchhiker's Guide to the Galaxy             Andy             Comment #44
 ...                          Chloe Cleoment commented on Hitchhiker's Guide to the Galaxy   Andy             Comment #45
 ...                          Chloe Cleoment commented on Hitchhiker's Guide to the Galaxy   Bert             Comment #45
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Andy             Comment #46
 ...                          Robin Rood commented on Hitchhiker's Guide to the Galaxy       Bert             Comment #46
 ...                          Andy commented on Hitchhiker's Guide to the Galaxy             Bert             Comment #47
 ...                          Bert commented on Hitchhiker's Guide to the Galaxy             Andy             Comment #48
 ...                          Chloe Cleoment commented on Harry Potter                       Andy             Comment #49
 ...                          Chloe Cleoment commented on Harry Potter                       Bert             Comment #49
 ...                          Robin Rood commented on Harry Potter                           Andy             Comment #50
 ...                          Robin Rood commented on Harry Potter                           Bert             Comment #50
 ...                          Andy commented on Harry Potter                                 Bert             Comment #51
 ...                          Bert commented on Harry Potter                                 Andy             Comment #52
 ...                          Chloe Cleoment commented on Harry Potter                       Andy             Comment #53
 ...                          Chloe Cleoment commented on Harry Potter                       Bert             Comment #53
 ...                          Robin Rood commented on Harry Potter                           Andy             Comment #54
 ...                          Robin Rood commented on Harry Potter                           Bert             Comment #54
============================ ============================================================== ================ ============= ====== ===============...===
<BLANKLINE>


Class reference
===============

.. class:: Message

  The Django model that represents a :term:`notification message`.

  .. attribute:: subject

    The subject of this message. See `Subject and body of a notification
    message`_.

  .. attribute:: body

    The body of this message. See `Subject and body of a notification
    message`_.

  .. attribute:: user

    The recipient of this message. The :term:`site user` to whom this
    message is to be delivered.

    If this is empty, then it is a :term:`broadcast notification`.

  .. attribute:: owner

    The owner of this message.  Expresses what this message is about.

    See :ref:`ug.notify.Message.owner`.

    This is a :term:`generic foreign key`.
    If this is empty, the message is said to have no owner.

  .. attribute:: message_type

    The :term:`notification message type`.

  .. attribute:: reply_to

    The comment to which a reply to this message would reply.

    An email notification for this message will have this information in its
    reply-to header.

    This is a dummy field unless the :mod:`lino.modlib.comments` plugin is
    installed.

  .. attribute:: created

    Timestamp of when this message has been emitted.

  .. attribute:: sent

    Timestamp of when this message has been sent via email to its recipient.

  .. attribute:: seen

    Timestamp of when the recipient of this message has marked it as seen.

  .. method:: emit_notification(cls, ar, owner, message_type, msg_func, recipients)

      Emit a :term:`notification message` to each of the given recipients,
      respecting their individual :term:`user settings`.

      This is a class method that creates zero, one or several :term:`database
      rows <database row>`.

      `recipients` is an iterable of `(user, mail_mode)` tuples. Duplicate
      items, items with user being `None` and items having :attr:`mail_mode
      <lino.modlib.users.User.mail_mode>` set to :attr:`silent
      <MailModes.silent>` are removed.

      `msg_func` is a callable expected to return either `None` or a tuple
      `(subject, body)`. It is called for each recipient after having activated
      the recipient's language, so that any translatable text will be translated
      to the user's language.

      The emitting user does not get notified unless they have
      :attr:`User.notify_myself` is set.

  .. method:: create_message(cls, user, owner=None, **kwargs)

      Create a message unless that user has already been notified
      about that object.

  .. method:: send_summary_emails(cls, mm)

      Send summary emails for all pending notifications with the
      given mail_mode `mm`.

  .. method:: send_browser_message_for_all_users(self, user)

      Send_message to all connected users

  .. method:: send_browser_message(self, user)

      Send_message to the user's browser


.. class:: Messages

    Base for all tables of messages.

.. class:: AllMessages(Messages)

    The gobal list of all messages.

.. class:: MyMessages(Messages)

    Shows messages emitted to me.


Parsing email notification

>>> msg = notify.Message.objects.last()
>>> ar = notify.Messages.request()
>>> context = ar.get_printable_context()
>>> template = rt.get_template("notify/summary.eml")
>>> user = msg.user
>>> msg.created = msg.created.replace(year=2024, month=6, day=1, hour=12, minute=0)
>>> context.update(user=user, messages=[msg])
>>> template.render(**context)  #doctest: +ELLIPSIS
'<html><head><base href="http://127.0.0.1:8000" target="_blank"></head><body>\n\n\n\n\n(01/06/2024 12:00 UTC)\n\nRobin Rood commented on <a href="/#/api/groups/Groups/3">Harry Potter</a>:<br><p></p>\n<p>Hello</p>\n\n</body></html>'

>>> context.update(messages=[m for m in notify.Message.objects.filter(user=user)][:3])
>>> template.render(**context)  #doctest: +ELLIPSIS
'<html><head><base href="http://127.0.0.1:8000" target="_blank"></head><body>\n\nHi Bert,\nYou have 3 unseen notifications\n\n<div>\n\n<H3>... UTC</H3>\n\n\n</div>\n\n<div>\n\n<H3>... UTC</H3>\n\nAndy commented on <a href="/#/api/groups/MyGroups/3">Harry Potter</a>:<br><p>This is a comment about [group 1] and [group 2].</p>\n</div>\n\n<div>\n\n<H3>... UTC</H3>\n\nChloe Cleoment commented on <a href="/#/api/groups/MyGroups/3">Harry Potter</a>:<br><span>Styled comment <span style="color: #2b2301;">pasted from word!</span> </span>\n</div>\n\n\n</body></html>'

>>> dhaka = about.TimeZones.add_item("02", "Asia/Dhaka", "dhaka")
>>> user.time_zone = dhaka
>>> context.update(messages=[msg])
>>> template.render(**context)  #doctest: +ELLIPSIS
'<html><head><base href="http://127.0.0.1:8000" target="_blank"></head><body>\n\n\n\n\n(01/06/2024 18:00 +06)\n\nRobin Rood commented on <a href="/#/api/groups/Groups/3">Harry Potter</a>:<br><p></p>\n<p>Hello</p>\n\n</body></html>'

>>> context.update(messages=[m for m in notify.Message.objects.filter(user=user)][:3])
>>> template.render(**context)  #doctest: +ELLIPSIS
'<html><head><base href="http://127.0.0.1:8000" target="_blank"></head><body>\n\nHi Bert,\nYou have 3 unseen notifications\n\n<div>\n\n<H3>... +06</H3>\n\n\n</div>\n\n<div>\n\n<H3>... +06</H3>\n\nAndy commented on <a href="/#/api/groups/MyGroups/3">Harry Potter</a>:<br><p>This is a comment about [group 1] and [group 2].</p>\n</div>\n\n<div>\n\n<H3>... +06</H3>\n\nChloe Cleoment commented on <a href="/#/api/groups/MyGroups/3">Harry Potter</a>:<br><span>Styled comment <span style="color: #2b2301;">pasted from word!</span> </span>\n</div>\n\n\n</body></html>'


Push subscriptions
==================

.. class:: Subscription

    The Django model that represents a :term:`push subscription`.

    Loosely inspired by `django-webpush
    <https://github.com/safwanrahman/django-webpush>`__.


    .. attribute:: user
    .. attribute:: lang
    .. attribute:: userAgent
    .. attribute:: endpoint
    .. attribute:: p256dh
    .. attribute:: auth


Change notifiers
================

.. class:: ChangeNotifier

    Model mixin for things that emit notifications to a list of observers (or
    "watchers") when an instance is modified.

    .. method:: add_change_watcher(self, user)

        Parameters:

        :user: The user that will be linked to this object as a change watcher.

    .. method:: get_change_subject(self, ar, cw)

        Returns the subject text of the notification message to emit.

        The default implementation returns a message of style
        "{user} modified|created {object}" .

        Returning None or an empty string means to suppress
        notification.

    .. method:: get_change_body(self, ar, cw)

        Return the body text of the notification message to emit.

        The default implementation returns a message
        "{user} created {what}" or
        "{user} modified {what}" followed by a summary of the changes.

        For tested code snippets see See :doc:`/topics/get_change_body`.


    .. method:: get_change_info(self, ar, cw)

        Return a list of HTML elements to be inserted into the body.

        Removed since 20230822.

        This is called by :meth:`get_change_body`.
        Subclasses can override this. Usage example
        :class:`lino_xl.lib.notes.models.Note`

    .. method:: get_change_owner(self)

        Return the owner of the notification to emit.

        The "owner" is "the database object we are talking about"
        and decides who is observing this object.


Notifying actions
=================

A notifying action is an action that pops up a dialog window with at least three
fields "Summary", "Description" and a checkbox "Don't notify others" to
optionally suppress notification.

Screenshot of a notifying action:

.. image:: /images/screenshots/reception.CheckinVisitor.png
    :scale: 50


.. class:: NotifyingAction

    Mixin for notifying actions.

    Dialog fields:

    .. attribute:: notify_subject
    .. attribute:: notify_body
    .. attribute:: notify_silent

    .. method:: get_notify_subject(self, ar, obj)

        Return the default value of the `notify_subject` field.

    .. method:: get_notify_body(self, ar, obj)

        Return the default value of the `notify_body` field.

    .. method:: get_notify_owner(self, ar, obj)

        Expected to return the :attr:`owner
        lino.modlib.notify.Message.owner>` of the message.

        The default returns `None`.

        `ar` is the action request, `obj` the object on which the
        action is running,

    .. method:: get_notify_recipients(self, ar, obj)

        Yield a list of users to be notified.

        `ar` is the action request, `obj` the object on which the
        action is running,


A :class:`NotifyingAction` is a dialog action that potentially sends a
notification.  It has three dialog fields ("subject", "body" and a checkbox
"silent").  You can have non-dialog actions (or actions with some other dialog
than a simple subject and body) which build a custom subject and body and emit a
notification.  If the emitting object also has a method
:meth:`emit_system_note`, then this is being called as well.


Plugin settings
===============

This plugin adds the following settings, which a :term:`server administrator` can
configure in the :xfile:`settings.py`.

.. setting:: notify.remove_after

    Automatically remove notification messages after x days.

    Default value is 14 days. Set this to `None` or 0 to deactivate cleanup and
    keep messages forever.

.. setting:: notify.keep_unseen

    Whether to keep unseen messages when removing old messages
    according to :data:`remove_after`.

    In normal operation this should be True, but e.g. after a flood
    of messages during experimental phases we might want to get rid of
    them automatically.

.. setting:: notify.mark_seen_when_sent

    When this is True, Lino marks notification messages as `seen` when they have
    been sent via email.


.. setting:: notify.use_push_api

    Whether to enable :term:`desktop notifications` using webpush.

    In a production server it is mandatory to set your own vapid credentials:

.. setting:: notify.vapid_private_key

    The private VAPID key of this site.

.. setting:: notify.vapid_public_key

    The public VAPID key of this site.

.. setting:: notify.vapid_admin_email

    The VAPID contact address of this site.


>>> from django.conf import settings
>>> from lino.core.utils import is_devserver
>>> # import sys ; sys.argv
>>> is_devserver()
True

..
  >> settings.CHANNEL_LAYERS['default']['BACKEND'] in ['asgiref.inmemory.ChannelLayer','channels_redis.core.RedisChannelLayer']
  True
  >> settings.CHANNEL_LAYERS['default'].get('ROUTING','') in ['lino.modlib.notify.routing.channel_routing','']
  True


Utility functions
=================

.. function:: send_pending_emails_often()
.. function:: send_pending_emails_daily()

.. function:: clear_seen_messages

    Daily task which deletes messages older than :attr:`remove_after`
    hours.

Choicelists
===========

.. class:: MessageTypes

    The list of possible choices for the `message_type` field
    of a :class:`Message`.

.. class:: MailModes

    How the system should send email notifications to a user.

    .. attribute:: silent

        Disable notifications for this user.

    .. attribute:: never

        Notify in Lino but never send email.


Actions
=======

.. class:: MarkSeen

   Mark this message as seen.

.. class:: MarkAllSeen

   Mark all messages as seen.

.. class:: ClearSeen

   Mark this message as not yet seen.


Templates used by this plugin
=============================

.. xfile:: notify/body.eml

    A Jinja template used for generating the body of the email when
    sending a message per email to its recipient.

    Available context variables:

    - ``obj`` -- The :class:`Message` instance being sent.

    - ``E`` -- The html namespace :mod:`etgen.html`

    - ``rt`` -- The runtime API :mod:`lino.api.rt`

    - ``ar`` -- The action request which caused the message. a
      :class:`BaseRequest <lino.core.requests.BaseRequest>` instance.



Credits
=======

- https://rossta.net/blog/using-the-web-push-api-with-vapid.html
