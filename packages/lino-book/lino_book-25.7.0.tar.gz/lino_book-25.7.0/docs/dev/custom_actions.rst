.. doctest docs/dev/custom_actions.rst
.. _dev.custom_actions:

======================
Write custom actions
======================

A custom action is an action written by the :term:`application developer`.

Examples of custom actions defined by certain libraries:

- The :class:`MoveUp <lino.mixins.sequenced.MoveUp>` and
  :class:`MoveDown <lino.mixins.sequenced.MoveDown>` actions of a
  :class:`Sequenced <lino.mixins.sequenced.Sequenced>`.

- The :class:`Duplicate <lino.mixins.duplicable.Duplicate>` action for
  creating a copy of the current row.

- In :mod:`lino.mixins.printable`:
  :class:`DirectPrintAction <lino.mixins.printable.DirectPrintAction>`,
  :class:`CachedPrintAction <lino.mixins.printable.CachedPrintAction>`,
  :class:`ClearCacheAction <lino.mixins.printable.ClearCacheAction>`

- The :class:`ToggleChoice <lino_xl.lib.polls.ToggleChoice>`

You can define actions

- either on the :term:`database model` or on the :term:`data table`

- either using the `dd.action` decorator on a method
  or by defining a custom subclass of :class:`Action <lino.core.actions.Action>`
  (and adding an instance of this class to the :term:`database model` or the :term:`data table`)


Defining custom actions
=======================

Application developers can define new custom actions by

- applying the
  :func:`action` decorator to a method of a :term:`database model` or a
  :term:`data table`, or by

- subclassing the :class:`Action` class and instantiating them as an attribute
  of the model or :term:`database model` or :term:`data table`.

The :ref:`Polls tutorial <lino.tutorial.polls>` has a usage example of
the first approach:

.. code-block:: python

    @dd.action(help_text="Click here to vote this.")
    def vote(self, ar):
        def yes(ar):
            self.votes += 1
            self.save()
            return ar.success(
                "Thank you for voting %s" % self,
                "Voted!", refresh=True)
        if self.votes > 0:
            msg = "%s has already %d votes!" % (self, self.votes)
            msg += "\nDo you still want to vote for it?"
            return ar.confirm(yes, msg)
        return yes(ar)

The :func:`@dd.action <dd.action>` decorator can have keyword
parameters to specify information about the action, e.g. :attr:`label
<Action.label>`, :attr:`help_text <Action.help_text>` and
:attr:`required <Action.required_roles>`.

The action method itself must have the following signature::

    def vote(self, ar, **kwargs):
        ...
        return ar.success(kwargs)

Where ``ar`` is an :class:`ActionRequest <lino.core.requests.ActionRequest>`
instance that holds information about the web request that called the action.

- :meth:`callback <lino.core.requests.BaseRequest.callback>`
  and :meth:`confirm <lino.core.requests.BaseRequest.callback>`
  lets you define a dialog with the user using callbacks.

- :meth:`success <lino.core.requests.BaseRequest.success>` and
  :meth:`error <lino.core.requests.BaseRequest.error>` are possible
  return values where you can ask the client to do certain things.



The :func:`action` decorator
============================

.. currentmodule:: lino.core.actions

You can use the :func:`action` decorator to to define custom actions.

Any arguments you pass to the decorator are forwarded to
:meth:`Action.__init__`. In practice you'll possibly use: :attr:`label
<Action.label>`, :attr:`help_text <Action.help_text>` and :attr:`required_roles
<lino.core.permissions.Permittable.required_roles>`.

The :ref:`Lino Polls tutorial <lino.tutorial.polls>` shows the simplest form of
defining an action by adding the :func:`action <lino.core.actions.action>`
decorator to a method.

The following two approaches are equivalent. Using a custom class::

  class MyAction(dd.Action):

      def run_from_ui(self, ar):
          # do something...

  class MyModel(dd.Model):
      my_action = MyAction()

Using a decorator::

  class MyModel(dd.Model):

      @dd.action()
      def my_action(self, ar):
          # do something...


In above case (and in some real cases) it might look tedious and redundant to
define an action class and then instantiate it on the model. But in general we
recommend this more verbose approach.  We use the primitive approach (just a
method on the model) only in very simple cases.

The advantages become visible e.g. when you have several similar actions and
want them to inherit from a common base class. Or we can reuse a same action
class on different models (most standard actions like
:class:`lino.core.actions.ShowInsert` do this). Or we have actions where we use
instances of a same class with different instance values (e.g. the
:class:`lino.core.actions.ShowSlaveTable` action).   Also an explicit separate
class it is syntactically more readable.


Example project
===============

The :mod:`lino_book.projects.actions` project shows some methods of
defining actions.  Here is the :xfile:`models.py` file used for this
small demo project:

.. literalinclude:: /../../book/lino_book/projects/actions/models.py


>>> from lino import startup
>>> startup('lino_book.projects.actions.settings')
>>> from lino.api.doctest import *
>>> from lino_book.projects.actions.models import *

To demonstrate this, we sign in and instantiate an `Moo` object:

>>> ses = rt.login()
>>> obj = Moo()

Running an action programmatically is done using the
:meth:`run <lino.core.requests.BaseRequest.run>` method of your
session.

Since `a` and `m` are defined on the Model, we can run them directly:

>>> rv = ses.run(obj.a)
>>> print(rv["message"])
Called a() on Moo object
>>> rv["success"]
True

>>> print(ses.run(obj.m)['message'])
Called m() on Moo object

This wouldn't work for `t` and `b` since these are defined on `Moos`
(which is only one of many possible tables on model `Moo`):

>>> ses.run(obj.t)
Traceback (most recent call last):
...
AttributeError: 'Moo' object has no attribute 't'

So in this case we need to specify them table as the first parameter.
And because they are row actions, we need to pass the instance as
mandatory first argument:

>>> print(ses.run(S1.t, obj)['message'])
Called t() on Moo object

>>> print(ses.run(S1.b, obj)['message'])
Called a() on Moo object


How to "remove" an inherited action or collected from a table
-------------------------------------------------------------

Here are the actions on Moos:

>>> pprint([ba.action for ba in Moos.get_actions()])
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[<lino.modlib.bootstrap3.models.ShowAsHtml show_as_html ('HTML')>,
 <lino.core.actions.CreateRow grid_post>,
 <lino.core.actions.SaveGridCell grid_put>,
 <lino.core.actions.SubmitInsert submit_insert ('Create')>,
 <lino.core.actions.DeleteSelected delete_selected ('Delete')>,
 <lino_book.projects.actions.models.A a ('a')>,
 <lino_book.projects.actions.models.A b ('a')>,
 <lino.core.actions.ShowTable grid>,
 <lino.core.actions.Action m ('m')>,
 <lino.core.actions.Action t ('t')>]

A subclass inherits all actions from her parent.
When I define a second table `S1(Moos)`, then `S1` will have
both actions `m` and `t`:

>>> pprint([ba.action for ba in S1.get_actions()])
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[<lino.modlib.bootstrap3.models.ShowAsHtml show_as_html ('HTML')>,
 <lino.core.actions.CreateRow grid_post>,
 <lino.core.actions.SaveGridCell grid_put>,
 <lino.core.actions.SubmitInsert submit_insert ('Create')>,
 <lino.core.actions.DeleteSelected delete_selected ('Delete')>,
 <lino_book.projects.actions.models.A a ('a')>,
 <lino_book.projects.actions.models.A b ('a')>,
 <lino.core.actions.ShowTable grid>,
 <lino.core.actions.Action m ('m')>,
 <lino.core.actions.Action t ('t')>]

S2 does not have these actions because we "removed" them by overriding
them with None:

>>> pprint([ba.action for ba in S2.get_actions()])
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
[<lino.modlib.bootstrap3.models.ShowAsHtml show_as_html ('HTML')>,
 <lino.core.actions.CreateRow grid_post>,
 <lino.core.actions.SaveGridCell grid_put>,
 <lino.core.actions.SubmitInsert submit_insert ('Create')>,
 <lino.core.actions.DeleteSelected delete_selected ('Delete')>,
 <lino.core.actions.ShowTable grid>]



.. _dialog_actions:

Dialog actions
==============

When you specify `parameters` on a custom action, then your action
becomes a "dialog action". When a user invokes a dialog action, Lino
opens a dialog window which asks for the values of these
parameters. The action itself is being run only when the user submits
the dialog window.

Examples of dialog actions:

- users.Users.change_password


- pcsw.Clients.refuse_client
- countries.Places.merge_row
- contacts.Persons.create_household
- coachings.Coachings.create_visit
- cal.Guests.checkin
- lino_xl.lib.trading.VatProductInvoice.make_copy MakeCopy
