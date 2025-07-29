.. doctest docs/plugins/linod.rst
.. _dg.plugins.linod:

===================================
``linod``: The Lino daemon
===================================

.. currentmodule:: lino.modlib.linod

This page documents the ``linod`` plugin for developers. We assume that you have
read the :ref:`end-user docs <ug.plugins.linod>`.

.. contents::
   :depth: 1
   :local:

This plugin defines the :manage:`linod` admin command, which is responsible for
running the :term:`background tasks <background task>`.

The "d" stands for "daemon", like in :program:`sshd`, :program:`cupsd`,
:program:`systemd` and other background processes on Linuxs systems.

When :data:`use_channels` is `True`, this plugin uses `channels
<https://github.com/django/channels>`__ to provide an ASGI application, and the
:manage:`linod` command then includes Channels' `runworker
<https://github.com/django/channels/blob/main/channels/management/commands/runworker.py>`__
command.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *


Usage
=====

Other plugins can register a :term:`background task` using the
:func:`schedule_often` or :func:`schedule_daily` decorators. For example (taken
from :mod:`lino.modlib.checkdata`)::

  @dd.schedule_daily()
  def checkdata(ar):
      """Run all data checkers."""
      check_data(fix=False)

The code that registers a background task should be in your plugin's
:xfile:`models.py` modules.


.. function:: schedule_daily(**kwargs)

  Shortcut to create a :func:`background_task` that is suggested to run every
  day.

.. function:: schedule_often(**kwargs)

  Shortcut to create a :func:`background_task` that is suggested to run every 10
  seconds.

.. function:: background_task(**kwargs)

    Register the decorated function as a :term:`background task`.

    Keyword arguments are used as default values when Lino creates a
    :class:`SystemTask` instance for this procedure.

    Except for the special keyword ``class_name``, which defaults to
    "linod.SystemTask". It is used by :mod:`lino_xl.lib.invoicing` to register a
    procedure that will create an :term:`invoicing task` instead of a normal
    :term:`background task`. :class:`lino_xl.lib.invoicing.InvoicingTask`
    instead of :class:`SystemTask`.



Plugin configuration
====================

.. data:: use_channels

  Whether to use :mod:`channels` and :mod:`daphne` to run in asynchronous mode.

.. data:: background_sleep_time

  How many seconds the :term:`background task runner` should sleep when there is nothing
  to do.

.. data:: daemon_user

  Name of the :term:`site user` who executes the :term:`background task runner`.


The ``linod`` admin command
===========================

>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

.. management_command:: linod

Use this in a :term:`developer environment` to run a Lino daemon.

How to play with it::

  $ pm prep
  $ pm linod
  Running worker for channels ['linod_settings']
  Start task runner using <Logger lino (INFO)>...
  Run 1 data checkers on 110 Vouchers...
  ...

And there it seems to hang, but actually it is just sleeping: checking every 5
seconds whether there is something to do. You can ask it to be make more noise
when sleeping if you set :envvar:`LINO_LOGLEVEL` to ``DEBUG`` before running it::

  $ LINO_LOGLEVEL=DEBUG pm linod

>>> shell("django-admin linod --help")  #doctest: +NORMALIZE_WHITESPACE
usage: django-admin linod [-h] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                          [--pythonpath PYTHONPATH] [--traceback] [--no-color]
                          [--force-color] [--skip-checks]
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output,
                        3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main".
                        If this isn't provided, the DJANGO_SETTINGS_MODULE environment
                        variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.


Background procedures
=====================

>>> rt.show(linod.Procedures)  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
============================== ============================== ============================== ================== =============================================================
 value                          name                           text                           Task class         Suggested recurrency
------------------------------ ------------------------------ ------------------------------ ------------------ -------------------------------------------------------------
 event_notification_scheduler   event_notification_scheduler   event_notification_scheduler   linod.SystemTask   every=300, every_unit=secondly
 generate_calendar_entries      generate_calendar_entries      generate_calendar_entries      linod.SystemTask   every=1, every_unit=daily
 checksummaries                 checksummaries                 checksummaries                 linod.SystemTask   every=1, every_unit=daily
 checkdata                      checkdata                      checkdata                      linod.SystemTask   every=1, every_unit=daily
 send_weekly_report             send_weekly_report             send_weekly_report             linod.SystemTask   every=1, every_unit=weekly, saturday=True, start_time=04:00
 delete_older_changes           delete_older_changes           delete_older_changes           linod.SystemTask   every=1, every_unit=daily
 send_pending_emails_often      send_pending_emails_often      send_pending_emails_often      linod.SystemTask   every=10, every_unit=secondly
 send_pending_emails_daily      send_pending_emails_daily      send_pending_emails_daily      linod.SystemTask   every=1, every_unit=daily
 clear_seen_messages            clear_seen_messages            clear_seen_messages            linod.SystemTask   every=1, every_unit=daily
 read_inbox                     read_inbox                     read_inbox                     linod.SystemTask   every=300, every_unit=secondly
 run_invoicing_tasks            run_invoicing_tasks            run_invoicing_tasks            invoicing.Task     every=1, every_unit=daily
============================== ============================== ============================== ================== =============================================================
<BLANKLINE>

While the procedures are in a choicelist (i.e. end users cannot edit them), the
list of :term:`system tasks <system task>` is configurable.  The default
situation is that every procedure has created one :term:`system task`:



Logging levels
==============

>>> rt.show(linod.LogLevels)
========== ========== ===============
 value      text       Numeric value
---------- ---------- ---------------
 DEBUG      DEBUG      10
 INFO       INFO       20
 WARNING    WARNING    30
 ERROR      ERROR      40
 CRITICAL   CRITICAL   50
========== ========== ===============
<BLANKLINE>


``DEBUG`` means to include detailed debug messages. You should not set this
for a longer period on a production site because it bloats the log files.

``INFO`` means to show informative messages.

``WARNING`` is the recommended value for most tasks. Only warnings and error
messages are logged.

The levels ``ERROR`` and ``CRITICAL`` (log only errors and critical
messages) exist only for exceptional situations. You should probably not use
them.

System tasks
============

.. Restore database state after incomplete test run:

  >>> for obj in linod.SystemTask.objects.all():
  ...     obj.last_start_time = None
  ...     obj.disabled = False
  ...     obj.save()


>>> rt.show(linod.SystemTasks) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
===== ============================== =============== ========== ======================= ============================== ===
 No.   Name                           Logging level   Disabled   Status                  Background procedure           ⇵
----- ------------------------------ --------------- ---------- ----------------------- ------------------------------ ---
 1     event_notification_scheduler   WARNING         No         Scheduled to run asap   event_notification_scheduler
 2     generate_calendar_entries      INFO            No         Scheduled to run asap   generate_calendar_entries
 3     checksummaries                 INFO            No         Scheduled to run asap   checksummaries
 4     checkdata                      INFO            No         Scheduled to run asap   checkdata
 5     send_weekly_report             INFO            No         Scheduled to run asap   send_weekly_report
 6     delete_older_changes           INFO            No         Scheduled to run asap   delete_older_changes
 7     send_pending_emails_often      WARNING         No         Scheduled to run asap   send_pending_emails_often
 8     send_pending_emails_daily      INFO            No         Scheduled to run asap   send_pending_emails_daily
 9     clear_seen_messages            INFO            No         Scheduled to run asap   clear_seen_messages
 10    read_inbox                     WARNING         No         Scheduled to run asap   read_inbox
===== ============================== =============== ========== ======================= ============================== ===
<BLANKLINE>


>>> rt.show(invoicing.Task) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
===== ================================== ========== =========== =======================...===
 No.   Name                               Disabled   When        Status
----- ---------------------------------- ---------- ----------- -----------------------...---
 1     Make Service reports (SRV)         No         Every day   Scheduled to run at ...
 2     Make Sales invoices (SLS)          No         Every day   Scheduled to run at ...
 3     Make Subscription invoices (SUB)   No         Every day   Scheduled to run at ...
===== ================================== ========== =========== =======================...===
<BLANKLINE>



Dependencies
=============

When :data:`use_channels` is True,  the :mod:`lino.modlib.linod` plugin
requires the `django-channels` and `channels-redis` Python packages to be
installed, as well as a running `redis-server`.

To install redis on a Debian-based Linux distribution, run the following command
as root::

    $ apt update
    $ apt install redis

To install the required Python packages, run the following command after
activating your Python environment::

    $ pm install

>>> list(dd.plugins.linod.get_requirements(settings.SITE))
['channels', 'channels_redis', 'daphne']



Usage for developers
====================

To run the Lino daemon in a development environment, run :command:`pm linod` in
your project directory::

    $ cd ~/lino/lino_local/mysite
    $ pm linod

This process will run as long as you don't kill it, e.g. until you hit
:kbd:`Ctrl-C`.

Another way to kill the ``linod`` process is using the :cmd:`kill` command::

  $ kill -s SIGTERM 123456

If you kill ``linod`` with another signal than SIGTERM,  Lino will not run its
shutdown method, which is responsible e.g. for logging the "Done" message.

You may change the logging level by setting :envvar:`LINO_LOGLEVEL`::

    $ LINO_LOGLEVEL=debug pm linod

Testing instructions for developers
===================================

General remarks:

- The following demo projects are useful when testing linod:

  - :ref:`cms1 <book.projects.cms1>` has some background tasks, but
    :data:`use_channels` set to `False`

  - :ref:`noi1r <dg.projects.noi1r>` has :data:`use_channels` set to
    `True`.

  - :ref:`book.projects.chatter` has no background tasks, but it has
    :data:`use_channels` set to `True`.

- :data:`use_channels` changes the way :command:`pm linod` works.

- For testing logging to a file you can create a :xfile:`log` directory, and
  don't forget to remove it after your tests because a :xfile:`log` directory
  causes different output for certain commands and would cause the unit test
  suite to fail if you forget to delete it.

- When you start :cmd:`pm runserver` before :cmd:`pm linod`, runserver will
  write directly to the :xfile:`lino.log` file because there is no socket file.
  Two processes writing to the same file is likely to cause unpredictable
  results.

- You can set :attr:`Site.log_each_action_request` to `True`

.. rubric:: Example testing session 1

In terminal 1::

  go noi1e
  mkdir settings/log
  LINO_LOGLEVEL=debug pm linod

In terminal 2::

  go noi1r
  pm runserver

In your browser: sign in as robin, go to :menuselection:`Configure --> System
--> System tasks`, click "Run now" on one of them. The linod process in
terminal 1 should run the task.

In terminal 1, hit :kbd:`Ctrl-C` to stop the linod. Then do something in the
browser and verify that runserver no longer writes to the :xfile:`lino.log`.
That's normal because the runserver process believes that a socket server is
running. Now restart the linod process and verify that runserver is again being
logged. The socket file did not exist for some time and now it's a new socket
file, but this doesn't disturb logging.

In terminal 1::

  go noi1e
  rm -rf settings/log

If you remove the log directory before stopping the linod, you will get the
following exception when linod stops::

  FileNotFoundError: [Errno 2] No such file or directory: '.../noi1e/settings/log/lino.log'

.. rubric:: Example testing session 2

In terminal 1::

  go cms1
  LINO_LOGLEVEL=debug pm linod

Expected output::

  actors.discover() : registering 135 actors
  actors.initialize()
  Analyzing Tables...
  Analyze 22 slave tables...
  Discovering choosers for database fields...
  Start task runner using <Logger lino (DEBUG)>...
  Start next task runner loop.
  Too early to start System task #1 (update_publisher_pages)
  Too early to start System task #2 (checkdata)
  Let task runner sleep for 4.996284 seconds.
  ...
  (etc until you hit Ctrl-C)




Class reference
================


.. class:: Procedure

    A callable function designed to run in background at default interval given
    by :attr:`every_unit` and :attr:`every_value`.

    The default interval can be overridden by :class:`SystemTask`.

    .. attribute:: func

        The function to run as a system task.

        :type: Callable[[:class:`BaseRequest <lino.core.requests.BaseRequest>`], None]

    .. attribute:: every_unit

        The default unit of the interval at which the task :attr:`func` will run.

        :type: str

    .. attribute:: every_value

        The default value of the interval at which the task :attr:`func` will run.

        :type: int

    .. attribute:: start_datetime

        The time at which this task should run first.

        :type: datetime.datetime

    .. method:: run(self, ar)

        Calls the function stored in :attr:`func` passing ar as a positional argument.

        :param ar: an instance of :class:`BaseRequest <lino.core.requests.BaseRequest>`


.. class:: Procedures

    The choicelist of :term:`background procedures <background procedure>`
    available in this application.


.. class:: LogLevels

    A choicelist of logging levels available in this application.

    See `Logging levels`_


.. class:: SystemTask

    Django model used to represent a :term:`background task`.

    Specifies how to run a given :class:`Procedure` on this site.

    Inherits from :class:`Sequenced <lino.mixins.sequenced.Sequenced>`,
    :class:`RecurrenceSet <lino.modlib.system.RecurrenceSet>` and
    :class:`Runnable`.

    .. attribute:: start_datetime

        Tells at what time exactly this job started.

        :type: datetime.datetime

    .. method:: run(self, ar, lgr=None) -> Job

        Performs a routine job.

        * Calls :meth:`self.procedure.run <Procedure.run>`.
        * Cancels the rule in case of a failure.
        * Creates an instance of :class:`Job`

        :param ar: An instance of :class:`BaseRequest <lino.core.requests.BaseRequest>`
        :param lgr: Logger obtained by calling logging.getLogger.
        :return: An instance of :class:`Job`.


.. class:: SystemTasks

    The default table for the :class:`SystemTask` model.


.. class:: Runnable

  Model mixin used by :class:`SystemTask` and other models.

  The only known other model that subclasses this mixin is
  :class:`lino_xl.lib.invoicing.Task`.

  It defines two actions:

  .. attribute:: run_now

    Explicitly request to tun this task as soon as possible.

  .. attribute:: cancel_run

    Cancel the explicit request to tun this task as soon as possible.

  It defines the following database fields:

  .. attribute:: procedure

    The :term:`background procedure` to run in this task.

    This points to an instance of :class:`Procedure`.

  .. attribute:: requested_at

    The timestamp when a user has explicitly requested to run this task.

  .. attribute:: last_start_time

      The timestamp when this task has started running in the task runner.

  .. attribute:: last_end_time

      The timestamp when this task has finished running in the task runner.

  .. attribute:: message

      Stores information about the job, mostly logs.

  .. attribute:: disabled

      Tells whether the task should be ignored.

      Lino sets this to `True` when the tasks fails and raises an exception.
      But it can also be checked by an end user in the web interface.

  .. attribute:: log_level

      The logging level to apply when running this task.

      See :class:`LogLevels`.




Don't read me
=============

Exploring :ticket:`6108` (send_pending_emails_often runs only once a day).

>>> obj = linod.SystemTask.objects.get(procedure=linod.Procedures.send_pending_emails_often)
>>> dt = datetime.datetime(2025,5,16,23,59,55)
>>> obj.get_next_suggested_date(dt)
datetime.datetime(2025, 5, 17, 0, 0, 5)


..
  >>> dbhash.check_virgin()
