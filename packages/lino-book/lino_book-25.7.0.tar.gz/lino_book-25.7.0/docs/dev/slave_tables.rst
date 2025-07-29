=======================
More about slave tables
=======================

We have been introduced to :ref:`slave tables <slave_tables>`, but there is more
to say about them.

.. contents::
    :depth: 1
    :local:

Slave tables with special masters
=================================

The master of a :term:`slave table` can be something else than a :term:`database
row`.  For example

- in :class:`lino_xl.lib.accounting.MovementsByMatch` the master is a :class:`str`
- in :class:`lino_xl.lib.calview.DailyPlanner` the master is a :class:`lino_xl.lib.calview.Day` instance
- in :class:`lino_welfare.modlib.debts.PrintEntriesByBudget` the master is an :class:`EntryGroup`

If the master instance is not a subclass of :class:`lino.core.fields.TableRow`,
it must be JSON serializable.

.. _remote_master:

Slave tables with remote master
===============================

The :attr:`master_key` of a :ref:`slave table <slave_tables>` can be a remote
field.

.. graphviz::

   digraph foo  {
       A -> B
       B -> C
  }

When you have three models A, B and C with A.b being a pointer to B
and B.c being a pointer to C, then you can design a table `CsByA`
which shows the C instances of a given A instance by saying::

    class CsByA(Cs):
        master_key = "c__b"

For example :class:`lino_xl.lib.courses.ActivitiesByTopic` shows all activities
about a given topic. But an :term:`activity` has no foreign key ``topic``, so
you cannot say ``master_key = 'topic'``. But a course does know its topic
indirectly because it knows its :term:`activity line`, and the activity line
knows its topic. So you can specify a remote field::

    class ActivitiesByTopic(Courses):
        master_key = 'line__topic'

        allow_create = False

A slave table with a remote master should have :attr:`allow_create
<lino.core.actors.Actor.allow_create>` set to `False` because we cannot set a
line for a new course.

Other examples

- :class:`lino_avanti.lib.courses.RemindersByPupil`

.. :class:`lino_xl.lib.courses.EntriesByTeacher`


.. _related_master:

Slave tables with related master
================================

Another special case is when you have the following structure where both orders
and invoices are related to a partner, but the invoices don't know their order.

.. graphviz::

   digraph foo  {
       Order -> Partner
       Invoice -> Partner
  }

The :class:`lino_xl.lib.orders.InvoicesByOrder` table can be used in the detail
of an order to show the invoices *of the partner of that order*.  Here is how to
define this case::

    class InvoicesByOrder(InvoicesByPartner):

        label = _("Sales invoices (of client)")

        @classmethod
        def get_master_instance(cls, ar, model, pk):
            # the master instance of InvoicesByPartner must be a Partner, but since
            # we use this on an order, we get the pk of an order
            assert model is rt.models.contacts.Partner
            order = rt.models.orders.Order.objects.get(pk=pk)
            return order.get_invoiceable_partner()


Similar examples:

- :class:`lino_xl.lib.storage.MovementsByFiller`


Multiple master fields
======================

In Lino Prima, a cast is when a given teacher gives a given subject to a given
group of pupils. And similarly, an exam is usually (but not always) done by a
given teacher about a given subject in a given group.

.. graphviz::

  digraph foo  {
       Cast -> Subject
       Cast -> Teacher
       Cast -> Group
       Exam -> Subject
       Exam -> Teacher
       Exam -> Group
  }

But there is no direct pointer from exam to cast because not every exam requires
a cast. When we open the detail view of a cast, we want to see a list of all
exams for this cast. Here is how to declare the
:class:`lino_prima.lib.ratings.ExamsByCast` table::

  class ExamsByCast(Exams):
      required_roles = dd.login_required(PrimaTeacher)
      master = "school.Cast"
      column_names = "seqno designation period *"

      @classmethod
      def get_request_queryset(self, ar, **filter):
          mi = ar.master_instance
          assert isinstance(mi, rt.models.school.Cast)
          qs = super().get_request_queryset(ar, **filter)
          # When there are two teachers for a same subject, they can optionally
          # manage exams together.
          if manage_exams_separately:
              qs = qs.filter(subject=mi.subject, group=mi.group, user=mi.user)
          else:
              qs = qs.filter(subject=mi.subject, group=mi.group)
          return qs
