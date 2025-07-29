.. doctest docs/plugins/votes.rst
.. _dg.plugins.votes:

==============================
``votes``: User opinions
==============================

.. currentmodule:: lino_xl.lib.votes

The :mod:`lino_xl.lib.votes` plugin adds functionality for managing votes.


Table of contents:

.. contents::
   :depth: 1
   :local:


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

>>> ses = rt.login("robin")
>>> translation.activate('en')

Overview
========

.. glossary::

  vote

    A database object that expresses the fact that a :term:`site user` has an
    opinion or interest about a given :term:`votable`.

  votable

    A database object that can receive :term:`votes <vote>`.

    The :term:`application developer` can make the instances of a given
    :term:`database model` :term:`votable` by letting the model inherit from
    :class:`Votable` and specifying the model in :attr:`Plugin.votable_model`.


Usage
=====

When adding this plugin to your application, you must specify the
:attr:`lino_xl.lib.votes.Plugin.votable_model`.

Plugin configuration
====================

Nothing special.


Votes
=====


.. class:: Vote

  Django model for representing a :term:`vote`.
  Inherits from UserAuthored, Created, Workable

  .. attribute:: votable

      The ticket (or other votable) being voted.

  .. attribute:: user

      The user who is voting.

  .. attribute:: state

      The state of this vote.  Pointer to :class:`VoteStates
      <lino_xl.lib.votes.choicelists.VoteStates>`.

  .. attribute:: priority

      My personal priority for this ticket.

  .. attribute:: rating

      How the ticket author rates my help on this ticket.

  .. attribute:: remark

      Why I am interested in this ticket.

  .. attribute:: nickname

      My nickname for this ticket. Optional.

      If this is specified, then I get a quicklink to this ticket.


.. class:: Votes

    Table parameters:

    .. attribute:: observed_event

        There are two class attributes for defining a filter conditions
        which cannot be removed by the user:

    .. attribute:: filter_vote_states

        A set of vote states to require (i.e. to filter upon).  This
        must resolve using :meth:`resolve_states
        <lino.core.model.Model.resolve_states>`.

    .. attribute:: exclude_vote_states

        A set of vote states to exclude.  This must
        resolve using :meth:`resolve_states
        <lino.core.model.Model.resolve_states>`.


    .. attribute:: filter_ticket_states

        A set of ticket states to require (i.e. to filter upon). This
        must resolve using :meth:`resolve_states
        <lino.core.model.Model.resolve_states>`.



.. class:: AllVotes

    Show all votes of all users.

.. class:: MyVotes

    Show all my votes.

.. class:: VotesByVotable

    Show the votes about this object.


The state of a vote
===================


.. >>> rt.show(votes.VoteStates)
.. ======= ========== ========== =============
..  value   name       text       Button text
.. ------- ---------- ---------- -------------
..  10      watching   Watching
..  20      silenced   Silenced
.. ======= ========== ========== =============
.. <BLANKLINE>



.. class:: VoteState

    The state of a vote.

    .. attribute:: vote_name

        Translatable text. How a vote is called when in this state.


.. class:: VoteStates

    The list of possible states of a vote.  This is used as choicelist for the
    :attr:`state <Vote.state>` field of a :term:`vote`.

    The default implementation defines the following choices:

    .. attribute:: author

        Reserved for the author's vote.  Lino automatically creates an
        **author vote** for every author of a ticket (see
        :meth:`get_vote_raters
        <lino_xl.lib.votes.choicelists.Votable.get_vote_raters>`).


    .. attribute:: watching
    .. attribute:: candidate
    .. attribute:: assigned
    .. attribute:: done
    .. attribute:: rated
    .. attribute:: cancelled


Using votes for rating
======================

.. class:: Ratings

  The list of available ratings.

.. >>> rt.show(votes.Ratings)
.. ======= ====== ==============
..  value   name   text
.. ------- ------ --------------
..  10             Very good
..  20             Good
..  30             Satisfying
..  40             Deficient
..  50             Insufficient
..  90             Unratable
.. ======= ====== ==============
.. <BLANKLINE>



Vote events
===========

.. class:: VoteEvents


Welcome messages
================

This plugin adds a :term:`welcome message` "Your favourites are X, Y, ..." that
mentions all :term:`votables <votable>` for which the requesting user has given
a :attr:`nickname <Vote.nickname>`.

Votables
========

.. class:: Votable

  This model mixin adds two workflow actions ☆ and ★, which are mutually
  exclusive.

  .. attribute:: create_vote

    Define your vote about this object.

    Button label: ☆

    Visible only when you don't yet have a vote on this
    object. Clicking it will create a default vote object and show
    that object in a detail window.


  .. attribute:: edit_vote

    Edit your vote about this object.

    Button label: ★
