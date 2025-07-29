.. doctest docs/specs/topics.rst
.. _specs.topics:

============================
``topics`` : topics and tags
============================

.. currentmodule:: lino_xl.lib.topics

The :mod:`lino_xl.lib.topics` plugin adds the notions of "topics" and "tags".
Optionally it can also manage "partners" who are "interested" in a topic.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *
>>> from django.db.models import Q


Overview
========

A **topic** is something a partner can be interested in.
A **tag** is the fact that a given :term:`database row` has to do with a given topic.
An **interest** is the fact that a given partner is interested in a given topic.

Users can see a panel "Interests" (:class:`InterestsByPartner`) in the detail
window of a partner. They can add a row in that panel to specify that this
partner is interested in a topic.  They can open the panel in a window to delete
interests.

A site manager can configure the list of available topics.

>>> show_menu_path(topics.AllTopics)
Configure --> Topics --> Topics


Partner
=======

The :term:`application developer` can decide what a "partner" means for the
topics plugin by setting the :setting:`topics.partner_model`.

.. setting:: topics.partner_model

    The :term:`database model` that represents the people who can be interested
    in a topic. If this is `None`, interest management is deactivated.

For example in :ref:`noi` the "partners" who can be interested in a topic are
the :term:`site users <site user>`.

>>> print(dd.plugins.topics.partner_model)
users.User

The detail window of a topic has a panel "Interests" (:class:`InterestsByTopic`)
which shows the users for which this topic is interesting.

A site manager can see a global list of all interests.
This might be useful e.g. for exporting the data.

>>> show_menu_path(topics.AllInterests)
Explorer --> Topics --> Interests



Database models
===============

.. class:: Topic

    Django model representing a *topic*.

    .. attribute:: ref

        The reference.

        See :attr:`lino.mixins.ref.StructuredReferrable.ref`

    .. attribute:: name

        The designation in different languages.

    .. attribute:: description_text

        Rich text field for a longer multi-line description.

    .. attribute:: description

        Virtual field which includes the formatted structured reference and the
        :attr:`description_text`.

        See :attr:`lino.mixins.ref.StructuredReferrable.description`

    .. attribute:: topic_group

        Deprecated. Don't use.


.. class:: Topics
.. class:: AllTopics
.. class:: TopicsByGroup


.. class:: Tag

    Django model used to represent a *tag*.

    .. attribute:: owner
    .. attribute:: topic


.. class:: Interest

    Django model used to represent an *interest*.

    .. attribute:: partner
    .. attribute:: topic
    .. attribute:: remark

.. class:: Interests
.. class:: InterestsByTopic



Model mixins
============

.. class:: Taggable

  Adds an :attr:`add_tag` field.

  .. attribute:: add_tag

      A virtual field that lets the user select a topic to tag this database row
      with.

User roles
==========

.. class:: TopicsUser

  User role required to see the topics plugin.

Don't read me
=============


Because :class:`Topic` defines a database field :attr:`Topic.description` the
virtual field :attr:`lino.core.model.Model.description` is hidden:

>>> sorted(rt.models.topics.Topic._meta.private_fields, key=lambda f: str(f))
... #doctest: +NORMALIZE_WHITESPACE
[lino_xl.lib.topics.models.Topic.description,
lino_xl.lib.topics.models.Topic.full_page,
lino_xl.lib.topics.models.Topic.list_item,
lino_xl.lib.topics.models.Topic.name_column,
lino_xl.lib.topics.models.Topic.navigation_panel,
lino_xl.lib.topics.models.Topic.overview,
lino_xl.lib.topics.models.Topic.rowselect,
lino_xl.lib.topics.models.Topic.workflow_buttons]
