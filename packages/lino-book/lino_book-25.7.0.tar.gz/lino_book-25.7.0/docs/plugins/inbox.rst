.. doctest docs/plugins/inbox.rst
.. _dg.plugins.inbox:

====================================
``inbox`` : Process incoming emails
====================================

.. module:: lino_xl.lib.inbox

.. currentmodule:: lino_xl.lib.inbox

The :mod:`lino_xl.lib.inbox` plugin adds functionality for processing a mailbox
of incoming emails.

It usually consumes the mailbox, i.e. deletes the messages from the inbox after
processing them.

The :mod:`lino.modlib.notify`


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *

Which means that code snippets in this document are tested using the
:mod:`lino_book.projects.cms1` demo project.


Plugin settings
===============

.. setting:: inbox.subaddress_separator

  The character sequence to use for separating the "local" from the "subaddress"
  part in email addresses. Default value is ``"+"``.  See Subaddressing_ below.

.. setting:: inbox.mailbox_path

  Default value is `None`

.. setting:: inbox.mailbox_type

  .. Default value is ``"mailbox.mbox"``.

  This is any class that implements the :class:`mailbox.Mailbox` interface of
  the `mailbox <https://docs.python.org/3/library/mailbox.html>`__ package.

  - :class:`mailbox.Maildir`

  - :class:`mailbox.mbox` : the classic format for storing mail on Unix systems.
    All messages in an mbox mailbox are stored in a single file with the
    beginning of each message indicated by a line whose first five characters
    are “From “.

.. setting:: inbox.discard_processed_message

  Default value is `False`

.. setting:: inbox.upload_area

  Default value is ``'general'``. If this is `None`, files to attached incoming
  emails will be ignored.

.. setting:: inbox.upload_volume

  Default value is ``'inbox'``. If this is `None`, files to attached incoming
  emails will be ignored.



Subaddressing
=============

Lino uses subadressing `RFC 2533
<https://datatracker.ietf.org/doc/html/rfc5233>`__  (also known as plus
addressing) as follows (the examples assume that :setting:`SERVER_EMAIL` is
``'inbox@example.com'``):

- `inbox+123@example.com` (one separator) means that replying to this email will
  create a comment that replies to the comment 123.

- `inbox+12+34@example.com` (two separators) means that replying to this email
  will create a comment that is owner by the database object with content type
  12 and primary key 34.
