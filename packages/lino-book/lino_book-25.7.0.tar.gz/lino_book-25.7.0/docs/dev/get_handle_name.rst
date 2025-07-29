.. _get_handle_name:

================================
Table views with dynamic columns
================================

You can define a :term:`data table` with "dynamic" columns, where the initial
set of columns of the table depends on certain conditions.

To see this feature in action, invoke :manage:`runserver` in the
:mod:`lino_book.projects.events` demo project.
See :ref:`book.specs.events` for details.

Another example, which is used in production, is
:class:`lino_welfare.modlib.debts.PrintEntriesByBudget`

This feature is implemented by defining different "column sets".  You must
define a `get_handle_name` method that returns a "handle name" for each incoming
request. Each handle name will will identify the table handle to be created,
each of which has its own column set.

For example if you want a column set per user, you would add the user name to
the default name::

    from lino.core.constants import _handle_attr_name

    class MyTable(...):

        @classmethod
        def get_handle_name(self, ar):
            hname = _handle_attr_name
            hname += ar.get_user().username
            return hname

        @classmethod
        def get_column_names(self, ar):
            if ar is None:
                return 'foo bar baz'
            return ar.get_user().column_names

The handle does not yet say which columns to use. This is given by the
:meth:`get_column_names` method, which is called for each table handle. The
:attr:`column_names` returned by this method should of course depend on the same
variables as those that are used to determine the handle name.

TODO: more explanations....
