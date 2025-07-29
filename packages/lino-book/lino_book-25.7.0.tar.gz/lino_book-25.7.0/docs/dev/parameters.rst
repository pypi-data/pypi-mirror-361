.. doctest docs/dev/parameters.rst
.. include:: /../docs/shared/include/defs.rst
.. _dev.parameters:

================================
Introduction to actor parameters
================================

Any table in Lino can have optional panel with :term:`actor parameters <actor
parameter>`.  This document explains what they are. They are both similar to and
different from :term:`action parameters <action parameter>`.

.. contents::
    :depth: 2
    :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


Introduction
============

For example, here is a `My Appointments` table, first with the
:term:`parameter panel` collapsed and then expanded:

.. image:: parameters1.png
   :width: 300

.. image:: parameters2.png
   :width: 300

You can toggle between these two states by clicking the |gear|  button in the
toolbar. The help text of that button says `Show or hide the table parameters`.
This button is available only on tables that do have parameters.


.. glossary::

  actor parameter

    A run-time parameter that can be given to an actor in the :term:`parameter panel`.

    Actor parameters are stored in the :attr:`parameters
    <lino.core.actors.Actor.parameters>` attribute of their :class:`Actor
    <lino.core.actors.Actor>`.

  parameter panel

    A panel used to enter :term:`actor parameters <actor parameter>` of an
    actor. In ExtJS it expands or collapses by clicking the |gear| button in the
    toolbar.

  simple actor parameter

    An :term:`actor parameter` that maps to a given database field. For example
    :attr:`lino_xl.lib.contacts.Persons.gender` is a simple actor parameter
    that, when set, will cause the table to show only persons of the gender
    given in the parameter panel. You declare them by overriding the
    :meth:`get_simple_parameters <lino.core.model.Model.get_simple_parameters>`
    method of your model.


>>> pprint(rt.models.contacts.Persons.parameters)
{'aged_from': <django.db.models.fields.IntegerField: aged_from>,
 'aged_to': <django.db.models.fields.IntegerField: aged_to>,
 'end_date': <django.db.models.fields.DateField: end_date>,
 'gender': <lino.core.choicelists.ChoiceListField: gender>,
 'observed_event': <lino.core.choicelists.ChoiceListField: observed_event>,
 'start_date': <django.db.models.fields.DateField: start_date>}

Only one of these is a simple parameter:

>>> list(rt.models.contacts.Persons.get_simple_parameters())
['gender']

For the other parameters we must override the model's
:meth:`lino.core.model.Model.get_request_queryset` method in order to tell Lino
how they influence the data to be displayed.

TODO: continue to write documentation.


- :attr:`lino.core.utils.Parametrizable.parameters`



.. class:: lino.core.model.Model
  :noindex:

.. class:: lino.core.actors.Actor
  :noindex:

  .. attribute:: parameters

    User-definable parameter fields for this actor or action.  Set this to a
    `dict` of `name = models.XyzField()` pairs.

  .. attribute:: params_layout = None

    The layout to be used for the parameter panel.
    If this table or action has parameters, specify here how they
    should be laid out in the parameters panel.

  .. attribute:: params_panel_hidden = True

    If this table has parameters, set this to True if the parameters
    panel should be initially hidden when this table is being
    displayed.

  .. attribute:: params_panel_pos

    Where to place the parameters panel within the :term:`data window` when it
    is expanded.  Allowed values are "top", "bottom", "left" and "right"

  .. method:: use_detail_param_panel = False

    Set to true if you want the params panel to be displayed in the detail view.
    Used only in :class:`lino_xl.lib.cal.CalView`.



  .. attribute:: simple_parameters = None

    A tuple of names of filter parameters that are handled automatically.

    Application developers should not set this attribute directly,
    they should rather define a :meth:`get_simple_parameters` on the
    model.

  .. attribute:: get_simple_parameters(cls)

    Hook for defining which parameters are simple.

    Expected to return a list of names of parameter fields.
