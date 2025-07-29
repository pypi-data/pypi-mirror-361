==============================
``summaries`` : Summary tables
==============================

.. currentmodule:: lino.modlib.summaries

The :mod:`lino.modlib.summaries` plugin adds a framework for defining
:term:`summary fields <summary field>` and summary tables.

.. glossary::

  summary table

    A :term:`database table` with :term:`summary fields <summary field>`.

  slave summary

    A :term:`summary table` for which the summary rows depend on a "master".

    For example

The plugin has no models on its own, but defines several model mixins to be used
by other plugins.

It then adds the :manage:`checksummaries` command, which updates all summary
data. It also adds a :term:`background task` that does the same.

End users get a button :guilabel:`∑` on each model for which there are
:term:`slave summaries <slave summary>`.

Plugin settings :setting:`summaries.start_year` and
:setting:`summaries.end_year` specify the years to be covered in summary tables.


Usage examples
==============

- :doc:`userstats` adds a summary table with monthly statistic data per
  :term:`site user`.

- :mod:`lino_xl.lib.working` adds two summary tables, one with yearly statistics
  per project and the other with weekly statistics per user.

- `European Social Fund <https://welfare.lino-framework.org/specs/esf.html>`__ :
  The most advanced use of summaries. Is a summary table used to calculate
  yearly and monthly worked time with clients based on meeting type and various
  other rules.

.. _summary_fields:

Summary fields
==============

Application developers can use this plugin to create summary fields.

.. glossary::

  summary field

    A read-only and otherwise regular :term:`database field`, the value
    of which is computed at certain moments as a summary of other tables.  This can
    be used as an alternative for virtual fields that are computed on the fly for
    each request.

Example: Client has two date fields `active_from` and `active_until`, the
values of which are automatically computed based on all contracts with that
client. They are not virtual fields because we want to sort and filter on them,
and because their values aren't very dynamic: they are the start and end date of
the currently active contract.

Also it is likely required to update :meth:`reset_summary_data`
if the field type doesn't support a value of 0.

The application must declare them as summary fields by defining::

  class Client(Summarized, ...):

      def reset_summary_data(self):
          self.active_from = None
          self.active_until = None

      def get_summary_collectors(self):
          yield (self.update_active_from, Contracts.objects.filter(client=self).orderby("start_date")[0:1])
          yield (self.update_active_until, Contracts.objects.filter(client=self).orderby("end_date")[0:1])

      def update_active_from(self, obj):
          self.active_from = obj.start_date

      def update_active_until(self, obj):
          self.active_until = obj.end_date

Note that when a new contract is added, the client's `active_from` and
`active_until` fields are not updated unless you run
:meth:`compute_summary_values`.

The ``Summarized`` model mixin
================================

.. class:: Summarized

    Model mixin for database objects that have summary fields.

    .. attribute:: delete_them_all

        Set this to True if all instances of this model should be considered
        temporary data to be deleted by :manage:`checksummaries`.

    .. attribute:: compute_results

        Update all the summary fields for this database object.

    .. method:: reset_summary_data

        Set all counters and sums to 0.

    .. method:: compute_summary_values

        Compute the values of the summary fields in this :term:`database row`.

        The default implementation (1) calls :meth:`reset_summary_data`, then
        (2) iterates over the collectors and querysets given by
        :meth:`get_summary_collectors` and (3) saves the database row.

    .. method:: update_for_filter

        Runs :meth:`compute_summary_values` on a a filtered queryset
        based on keyword arguments.

    .. method:: get_summary_collectors

        To be implemented by subclasses. This must yield a sequence
        of ``(collector, qs)`` tuples, where `collector` is a callable
        and `qs` a queryset. Lino will call `collector` for each `obj`
        in `qs`. The collector is responsible for updating that
        object.

.. class:: SlaveSummarized

    Mixin for :class:`Summarized` models that are related to a master.

    The master is another database object for which this summary data applies.
    Implementing subclasses must define a field named :attr:`master`, which must
    be a :term:`foreign key` to the master model.

    .. attribute:: master

        The target model of the :attr:`master` will automatically receive an
        action `check_summaries`.

        The mixin also sets :attr:`allow_cascaded_delete
        <lino.core.model.Model.allow_cascaded_delete>` to ``'master'``.


.. class:: DateSummarized

    A :class:`Summarized` that will have more than one entries per master,
    one for each month.

    .. attribute:: summary_period

       Can be ``'yearly'``, ``'monthly'``, ``'weekly'`` or ``'timeless'``.

    .. attribute:: year

      The year

    .. attribute:: month

      The number of the month or the week.



The ``checksummaries`` command
==============================

This plugin adds the following :term:`django-admin command`.

.. management_command:: checksummaries


.. py2rst::

  from lino.modlib.summaries.management.commands.checksummaries \
      import Command
  print(Command.help)




Actions
=======


.. data:: check_summaries

    This plugin installs a :data:`check_summaries` action

    - (instance of :class:`UpdateSummariesByMaster`)
      on every model that is master for at least one :class:`Summary`

    - (instance of :class:`CheckSummaries`)
      on the :class:`lino.modlib.system.SiteConfig` object.


.. function:: get_summary_models

    Return a `dict` mapping each model which has at least one summary
    to a list of these summaries.


.. class:: CheckSummaries

    Web UI version of :manage:`checksummaries`.

.. class:: UpdateSummariesByMaster

    Update summary data for this object.


Plugin configuration
====================

The plugin has the following settings:

.. setting:: summaries.start_year

  The first year for which summaries should be computed.

  Default value is two years before the current year.

.. setting:: summaries.end_year

  The last year for which summaries should be computed.

  Default value is the current year.

.. setting:: summaries.duration_max_length

  The width of duration fields in summary records.

  Default value is 6, which means that maximum value for sums of duration is
  999:59.  If a summary yields a bigger value, Lino will store -1 instead.
