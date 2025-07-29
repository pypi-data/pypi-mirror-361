.. doctest docs/plugins/checkdata.rst
.. _book.specs.checkdata:

======================================================
``checkdata`` : Application-level data integrity tests
======================================================

.. currentmodule:: lino.modlib.checkdata

The :mod:`lino.modlib.checkdata` plugin adds support for defining
application-level data integrity tests. For the :term:`application developer` it
provides a method to define :term:`data checkers <data checker>` for their
models. For the :term:`server administrator` it adds the :manage:`checkdata`
:term:`django-admin command`. For the :term:`end user` it adds a set of
`automatic actions`_.

We assume that you have read the :ref:`end-user documentation
<ug.plugins.checkdata>`.


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.voga2.startup import *
>>> from django.core.management import call_command
>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)


The application developer can decide to add a :class:`MessagesByOwner` table to
the :term:`detail layout` of any model.  This enables the end users to focus on
the data problems related to a given database object.


Data checkers
=============

In the web interface you can select :menuselection:`Explorer --> System --> Data
checkers` to see a table of all available checkers.

..
    >>> show_menu_path(checkdata.Checkers, language="en")
    Explorer --> System --> Data checkers

>>> rt.show(checkdata.Checkers, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
=================================== ========================================================
 value                               text
----------------------------------- --------------------------------------------------------
 accounting.VoucherChecker           Check integrity of numbered vouchers
 beid.SSINChecker                    Check for invalid SSINs
 cal.ConflictingEventsChecker        Check for conflicting calendar entries
 cal.EventGuestChecker               Entries without participants
 cal.LongEntryChecker                Too long-lasting calendar entries
 cal.ObsoleteEventTypeChecker        Obsolete generated calendar entries
 countries.PlaceChecker              Check data of geographical places
 courses.MemberChecker               Check membership payments
 finan.FinancialVoucherItemChecker   Check for invalid account/partner combination
 memo.PreviewableChecker             Check for previewables needing update
 phones.ContactDetailsOwnerChecker   Check for mismatches between contact details and owner
 printing.CachedPrintableChecker     Check for missing target files
 sepa.BankAccountChecker             Check for partner mismatches in bank accounts
 system.BleachChecker                Find unbleached html content
 uploads.UploadChecker               Check metadata of upload files
 uploads.UploadsFolderChecker        Find orphaned files in uploads folder
 vat.VatColumnsChecker               Check VAT columns configuration
 vat.VatIdChecker                    Validate VAT id from online registry
=================================== ========================================================
<BLANKLINE>


The :class:`lino_xl.lib.countries.PlaceChecker` class is a simple example of how
to write a data checker::

  from lino.api import _
  from lino.modlib.checkdata.choicelists import Checker

  class PlaceChecker(Checker):
      model = 'countries.Place'
      verbose_name = _("Check data of geographical places.")

      def get_checkdata_problems(self, ar, obj, fix=False):
          if obj.name.isdigit():
              yield (False, _("Name contains only digits."))

  PlaceChecker.activate()

..
  >>> print(rt.models.countries.PlaceChecker.verbose_name)
  Check data of geographical places


More examples of data checkers we recommend to explore:

- :class:`lino_xl.lib.countries.PlaceChecker`
- :class:`lino_xl.lib.beid.mixins.BeIdCardHolderChecker`
- :class:`lino_xl.lib.addresses.AddressOwnerChecker`
- :class:`lino_xl.lib.vat.VatIdChecker`
- :class:`lino.mixins.dupable.DupableChecker`
- :class:`lino.modlib.uploads.UploadChecker`
- :class:`lino.modlib.uploads.UploadsFolderChecker`
- :class:`lino_welfare.modlib.pcsw.models.SSINChecker`
- :class:`lino_welfare.modlib.pcsw.models.ClientCoachingsChecker`
- :class:`lino_welfare.modlib.isip.mixins.OverlappingContractsChecker`
- :class:`lino_welfare.modlib.dupable_clients.models.SimilarClientsChecker`


Showing all data problem messages
=================================

In the web interface you can select :menuselection:`Explorer -->
System --> Data problem messages` to see all problems.

..
    >>> show_menu_path(checkdata.AllMessages, language="en")
    Explorer --> System --> Data problem messages

The demo database deliberately contains some data problems.

>>> rt.login("robin").show(checkdata.AllMessages, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
============= ================================================= ============================================================== ==============================
 Responsible   Database object                                   Message text                                                   Checker
------------- ------------------------------------------------- -------------------------------------------------------------- ------------------------------
 Robin Rood    `Recurring event #4 Assumption of Mary <…>`__     Event conflicts with Activity #1 001  1.                       cal.ConflictingEventsChecker
 Robin Rood    `Recurring event #11 Ascension of Jesus <…>`__    Event conflicts with Mittagessen (14.05.2015 11:10).           cal.ConflictingEventsChecker
 Robin Rood    `Recurring event #12 Pentecost <…>`__             Event conflicts with 4 other events.                           cal.ConflictingEventsChecker
 Rolf Rompen   `Mittagessen (14.05.2015 11:10) <…>`__            Event conflicts with Recurring event #11 Ascension of Jesus.   cal.ConflictingEventsChecker
 Robin Rood    `First meeting (25.05.2015 13:30) <…>`__          Event conflicts with Recurring event #12 Pentecost.            cal.ConflictingEventsChecker
 Robin Rood    `Absent for private reasons (25.05.2015) <…>`__   Event conflicts with Recurring event #12 Pentecost.            cal.ConflictingEventsChecker
 Robin Rood    `Karl Kaivers (MEC) <…>`__                        Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Josefine Leffin (ME) <…>`__                      Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Erna Emonts-Gast (ME) <…>`__                     Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Alfons Radermacher (MEC) <…>`__                  Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Edgard Radermacher (ME) <…>`__                   Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Hedi Radermacher (ME) <…>`__                     Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Didier di Rupo (MEL) <…>`__                      Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Otto Östges (ME) <…>`__                          Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Mark Martelaer (ME) <…>`__                       Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Marie-Louise Vandenmeulenbos (MEL) <…>`__        Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Lisa Lahm (ME) <…>`__                            Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Bernd Brecht (MEC) <…>`__                        Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Jérôme Jeanémart (ME) <…>`__                     Member until 2015-12-31, but no payment.                       courses.MemberChecker
 Robin Rood    `Source document PRC_29_2015.pdf <…>`__           Upload entry uploads/2015/05/PRC_29_2015.pdf has no file       uploads.UploadChecker
============= ================================================= ============================================================== ==============================
<BLANKLINE>





Filtering data problem messages
===============================

The user can set the table parameters e.g. to see only messages of a given type
("checker"). The following snippet simulates the situation of selecting the
:class:`courses.MemberChecker <lino_xl.lib.courses.MemberChecker>`.

>>> chk = checkdata.Checkers.get_by_value('courses.MemberChecker')
>>> rt.show(checkdata.MessagesByChecker, chk)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
============= ============================================ ==========================================
 Responsible   Database object                              Message text
------------- -------------------------------------------- ------------------------------------------
 Robin Rood    `Karl Kaivers (MEC) <…>`__                   Member until 2015-12-31, but no payment.
 Robin Rood    `Josefine Leffin (ME) <…>`__                 Member until 2015-12-31, but no payment.
 Robin Rood    `Erna Emonts-Gast (ME) <…>`__                Member until 2015-12-31, but no payment.
 Robin Rood    `Alfons Radermacher (MEC) <…>`__             Member until 2015-12-31, but no payment.
 Robin Rood    `Edgard Radermacher (ME) <…>`__              Member until 2015-12-31, but no payment.
 Robin Rood    `Hedi Radermacher (ME) <…>`__                Member until 2015-12-31, but no payment.
 Robin Rood    `Didier di Rupo (MEL) <…>`__                 Member until 2015-12-31, but no payment.
 Robin Rood    `Otto Östges (ME) <…>`__                     Member until 2015-12-31, but no payment.
 Robin Rood    `Mark Martelaer (ME) <…>`__                  Member until 2015-12-31, but no payment.
 Robin Rood    `Marie-Louise Vandenmeulenbos (MEL) <…>`__   Member until 2015-12-31, but no payment.
 Robin Rood    `Lisa Lahm (ME) <…>`__                       Member until 2015-12-31, but no payment.
 Robin Rood    `Bernd Brecht (MEC) <…>`__                   Member until 2015-12-31, but no payment.
 Robin Rood    `Jérôme Jeanémart (ME) <…>`__                Member until 2015-12-31, but no payment.
============= ============================================ ==========================================
<BLANKLINE>


See also :doc:`cal` and :doc:`/specs/holidays`.

Running the :command:`checkdata` command
========================================


>>> set_log_level(logging.WARNING)
>>> call_command('checkdata')

You can see the list of all available checkers also from the command
line using::

    $ python manage.py checkdata --list

>>> call_command('checkdata', list=True)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=================================== ========================================================
 value                               text
----------------------------------- --------------------------------------------------------
 accounting.VoucherChecker           Check integrity of numbered vouchers
 beid.SSINChecker                    Check for invalid SSINs
 cal.ConflictingEventsChecker        Check for conflicting calendar entries
 cal.EventGuestChecker               Entries without participants
 cal.LongEntryChecker                Too long-lasting calendar entries
 cal.ObsoleteEventTypeChecker        Obsolete generated calendar entries
 countries.PlaceChecker              Check data of geographical places
 courses.MemberChecker               Check membership payments
 finan.FinancialVoucherItemChecker   Check for invalid account/partner combination
 memo.PreviewableChecker             Check for previewables needing update
 phones.ContactDetailsOwnerChecker   Check for mismatches between contact details and owner
 printing.CachedPrintableChecker     Check for missing target files
 sepa.BankAccountChecker             Check for partner mismatches in bank accounts
 system.BleachChecker                Find unbleached html content
 uploads.UploadChecker               Check metadata of upload files
 uploads.UploadsFolderChecker        Find orphaned files in uploads folder
 vat.VatColumnsChecker               Check VAT columns configuration
 vat.VatIdChecker                    Validate VAT id from online registry
=================================== ========================================================
<BLANKLINE>


>>> set_log_level(logging.INFO)
>>> call_command('checkdata', 'cal.')
Run 4 data checkers on 1171 Calendar entries...
...
Found 6 and fixed 0 problems in Calendar entries.
1 check have been run. Found 6 and fixed 0 problems.

>>> call_command('checkdata', 'foo')
Traceback (most recent call last):
...
Exception: No checker matches ('foo',)

The ``--prune`` option instructs checkdata to remove all existing error messages
before running the tests.  This makes the operation quicker on sites with many
existing data problem messages. Don't use this in combination with a filter
because `--prune` removes *all* messages, not only those that you ask to
rebuild.

>>> set_log_level(logging.WARNING)
>>> shell("python manage.py checkdata --prune")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
Prune 20 existing messages...
...
Run 1 data checkers on 72 Persons...
Run 6 data checkers on 1171 Calendar entries...
...
35 checks have been run. Found 20 and fixed 0 problems.


NB the above example uses :mod:`atelier.sheller` instead of :mod:`call_command
<django.core.management.call_command>`.  Both methods are functionally
equivalent.


Language of checkdata messages
==============================

Every detected checkdata problem is stored in the database in the language of
the responsible user. A possible pitfall with this is the following example.

The checkdata message "Similar clients" appeared in English and not in the
language of the responsible user. That was because the checker did this::

  msg = _("Similar clients: {clients}").format(
      clients=', '.join([str(i) for i in lst]))
  yield (False, msg)

The correct way is like this::

  msg = format_lazy(_("Similar clients: {clients}"),
      clients=', '.join([str(i) for i in lst]))
  yield (False, msg)

See :doc:`/dev/i18n` for details.

Database models
===============

.. class:: Problem

  Django model used to store a :term:`data problem message`.

  .. attribute:: checker

     The :class:`Checker <lino.modlib.checkdata.Checker>` that reported this
     problem.

  .. attribute:: message

     The message text. This is a concatenation of all messages that
     were yielded by the :attr:`checker`.

  .. attribute:: user

     The :class:`user <lino.modlib.users.User>` responsible for fixing this
     problem.

     This field is being filled by the :meth:`get_responsible_user
     <lino.modlib.checkdata.Checker.get_responsible_user>`
     method of the :attr:`checker`.


.. class:: Problems

    The base table for :term:`data problem messages <data problem message>`.

.. class:: MyMessages

    Shows the :term:`data problem messages <data problem message>` assigned to me.


.. class:: Checkers

    The list of data checkers known by this application.

    This was the first use case of a :class:`ChoiceList
    <lino.core.choicelists.ChoiceList>` with a :attr:`detail_layout
    <lino.core.actors.Actor.detail_layout>`.


.. class:: Checker

  Base class for all :term:`data checkers <data checker>`.

  .. attribute:: model

    The model to be checked.  If this is a string, Lino will resolve it at startup.

    If this is an abstract model, :meth:`get_checkable_models` will
    yield all models that inherit from it.

    If this is `None`, the checker is unbound, i.e. the problem messages will
    not be bound to a particular database object.  This is used to detect
    *missing* database objects.   For example :class:`vat.VatColumnsChecker
    <lino_xl.lib.vat.VatColumnsChecker>` is unbound.

    Instead of setting :attr:`model` you might want to define your own
    :meth:`get_checkable_models` method. For example,
    :class:`accounting.VoucherChecker <lino_xl.lib.accounting.VoucherChecker>` does this
    because it wants to get all MTI children (not only top-level models).
    See :ref:`tested.core_utils` for more explanations.


  .. attribute:: no_auto

    Whether this checker should be ignored by :manage:`checkdata`.

    Default value is `False`. Setting this to `True` turns this checker into a
    "manual checker", which means that it runs only when a user requests it
    (e.g. by clicking on the :attr:`Model.fix_problems` action).

    As an application developer you set this when you call
    :meth:`Checker.activate`. Usage example is
    :class:`lino_xl.lib.peppol.SupplierChecker`.

  .. classmethod:: check_instance(cls, *args, **kwargs)

    Run :meth:`get_checkdata_problems` on this checker for the given database
    object.

  .. method:: get_checkable_models(self)

    Return a list of the models to check.

    The default implementation returns all top-level models that inherit from
    :attr:`model` (or `[None]` when :attr:`model` is `None`).

  .. classmethod:: activate(cls)

    Creates an instance of this class and adds it as a choice to the
    :class:`Checkers` choicelist.

    The :term:`application developer` must call this on their subclass in order
    to "register" or "activate" the checker.

  .. method:: update_problems(self, obj=None, delete=True, fix=False)

    Update the :term:`problem messages <data problem message>` of this checker
    for the specified object.

    ``obj`` is `None` on unbound checkers.

    When `delete` is False, the caller is responsible for deleting any existing
    objects.

  .. method:: get_checkdata_problems(self, ar, obj, fix=False)

    Return or yield a series of `(fixable, message)` tuples, each describing a
    data problem. `fixable` is a boolean saying whether this problem can be
    automatically fixed. And if `fix` is `True`, this method is also responsible
    for fixing it.

  .. method:: get_responsible_user(self, obj)

    The site user to be considered responsible for problems detected by this
    checker on the given database object `obj`. This will be stored in
    :attr:`user <lino.modlib.checkdata.Message.user>`.

    The given `obj` is an instance of :attr:`model`, unless for unbound
    checkers (i.e. whose :attr:`model` is `None`).

    The default implementation returns the *main checkdata
    responsible* defined for this site (see
    :attr:`responsible_user
    <lino.modlib.checkdata.Plugin.responsible_user>`).


.. function:: check_instance(ar, obj)

  Run all checkers on the given :term:`database row` `obj`.  The problem
  messages aren't stored but simply printed to `stdout`.



Automatic actions
=================

This plugin automatically installs two actions on every model that has at least
one active :term:`data checker`:

.. currentmodule:: lino.core.model


.. class:: Model
  :noindex:

  .. attribute:: fix_problems

    Update data problem messages and repair those which are automatically fixable.

    Implementing class: :class:`lino.modlib.checkdata.FixProblemsByController`.

  .. attribute:: check_data

    Update data problem messages for this database object,
    also removing messages that no longer exist.
    This action does not change anything else in the database.

    Implementing class: :class:`lino.modlib.checkdata.UpdateMessagesByController`.

.. currentmodule:: lino.modlib.checkdata

Internal utilities
==================

.. function:: get_checkable_models(*args)

    Return an `OrderedDict` mapping each model which has at least one
    checker to a list of these checkers.

    The dict is ordered to avoid that checkers run in a random order.

..
  The only change in the database are the checkdata messages, which have been
  pruned and then re-created, so they have different ids. But we can ignore
  this, so we mark the database as virgin.

  >>> dbhash.check_virgin()
  Database ... isn't virgin:
  - checkdata.Message: 20 rows added, 20 rows deleted
  Cannot restore database because some rows have been deleted
  >>> dbhash.mark_virgin()
