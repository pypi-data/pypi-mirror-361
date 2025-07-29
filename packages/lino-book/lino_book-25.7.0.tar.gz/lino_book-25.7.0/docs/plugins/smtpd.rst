.. doctest docs/plugins/smtpd.rst
.. _dg.plugins.smtpd:

====================================
``smtpd`` : Add an SMTP daemon
====================================

.. currentmodule:: lino.modlib.smtpd

The :mod:`lino.modlib.smtpd` plugin adds functionality for receiving emails.

It defines a :mod:`recmail` command, which starts an SMTP server.



.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


.. management_command:: recmail

``recmail`` stands for "receive mail". Starts a configurable SMTP
server which forwards incoming mails to your Lino application. For
every incoming mail it sends a `mail_received` signal.  It is up to
your application to decide what to with these mails.

If you want to run this as a daemon, you must do::

  $ pip install python-daemon
