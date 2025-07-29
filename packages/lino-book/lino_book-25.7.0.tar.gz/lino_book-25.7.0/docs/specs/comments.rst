.. doctest docs/specs/comments.rst
.. _dg.plugins.comments:

=====================================
``comments`` : The comments framework
=====================================

.. currentmodule:: lino.modlib.comments

The :mod:`lino.modlib.comments` plugin adds a framework for handling comments.

This article is a general description, see also
:doc:`/apps/noi/comments` and
:doc:`/specs/avanti/comments`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *



Don't read this
===============

>>> for cls in comments.Comment.mro():
...     edm = cls.__dict__.get('extra_display_modes', None)
...     if edm is not None and DISPLAY_MODE_SUMMARY in edm:
...         print(cls)

>>> for cls in comments.Comments.mro():
...     ddm = cls.__dict__.get('default_display_modes', None)
...     if ddm is not None and DISPLAY_MODE_SUMMARY in ddm:
...         print(cls)

>>> for cls in comments.Comments.mro():
...     edm = cls.__dict__.get('extra_display_modes', None)
...     if edm is not None and DISPLAY_MODE_SUMMARY in edm:
...         print(cls)

>>> DISPLAY_MODE_SUMMARY in comments.RepliesByComment.extra_display_modes
False


Comments
========

.. class:: Comment

    The :term:`database model` to represent a :term:`comment`.

    .. attribute:: user

        The author of the comment.

    .. attribute:: owner

        The :term:`discussion topic` this comment is about.

        The :attr:`owner` of a comment must be an instance of a subclass of
        :class:`Commentable`.

    .. attribute:: body

        The full body text of your comment.

    .. attribute:: short_preview

        The first paragraph of your :attr:`body`.

    .. attribute:: emotion

        The emotion of this comment.

    .. attribute:: published

        When this comment has been published. A timestamp.

The :attr:`Comment.owner` field is a :term:`generic foreign key`, i.e.
theoretically users can discuss about any database object, but actually the
:term:`application developer` decides which database models can serve as topics
for commenting by

- having these database models inherit from :class:`Commentable` and

- adding the :class:`CommentsByRFC` panel to their :term:`detail layout`.


.. class:: Comments

    .. attribute:: show_published

        Whether to show only (un)published comments, independently of
        the publication date.

    .. attribute:: start_date

      Hide comments before this date.

    .. attribute:: end_date

      Hide comments after this date.

    .. attribute:: observed_event

       Which event (created, modified or published) to consider when
       applying the date range given by :attr:`start_date` and
       :attr:`end_date`.


.. class:: AllComments

    Show all comments.

.. class:: MyComments

    Show the comments posted by the current user.

.. class:: RecentComments

    Show the most recent comments that have been posted on this site.


.. class:: CommentsByX
.. class:: CommentsByType

.. class:: CommentsByRFC

    Shows the comments about a given :term:`database row`.

.. class:: ObservedTime

.. class:: CommentEvents

    The choicelist with selections for
    :attr:`Comments.observed_event`.

.. class:: PublishComment
    Publish this comment.

.. class:: PublishAllComments
    Publish all comments.


Emotions
========

.. class:: Emotions

    The list of available values for the :attr:`Comment.emotion` field.

>>> rt.show("comments.Emotions")
========== ========== ========== =============
 value      name       text       Button text
---------- ---------- ---------- -------------
 ok         ok         Okay
 agree      agree      Agree      ✅
 disagree   disagree   Disagree   ❎
========== ========== ========== =============
<BLANKLINE>


Comment types
=============

.. class:: CommentType

    The :class:`CommentType` model is not being used in production,
    one day we will probably remove it.


.. class:: CommentTypes

    The table with all existing comment types.

    This usually is accessible via the `Configure` menu.


Commentable
===========

.. class:: Commentable

  Mixin for models that are :term:`commentable`, i.e. the rows of which can
  become :term:`discussion topic` of comments.

  .. attribute:: create_comment_template = _("Created a new {model}.")

    The template to use for the comment that gets generated automatically
    when an :term:`end user` creates an instance of this.

    Set this to `None` if you don't want Lino to generate any comment when
    an instance gets created.

  .. method:: add_comments_filter(cls, qs, user)

    Add filters to the given queryset of comments, requested by the given
    user.

    Return `None` to not add any filter.  Otherwise the return value should
    be a :class:`django.db.models.Q` object.

    Default behaviour is that public comments are visible even to anonymous
    while private comments are visible only to their author and to
    :class:`PrivateCommentsReader`.

    You can override this class method to define your own privacy settings.

    Usage example in
    :class:`lino_xl.lib.groups.Group` and
    :class:`lino_xl.lib.tickets.Ticket`.

    If you override this method, you probably want to define a
    :class:`django.contrib.contenttypes.fields.GenericRelation` field on
    your model in order to write filter conditions based on the owner of the
    comment.

  .. method:: get_rfc_description(self, ar)

    Return a HTML formatted string with the description of this
    Commentable as it should be displayed by the slave summary of
    :class:`CommentsByRFC`.

    It must be a string and not an etree element. That's because
    it usually includes the content of RichTextField. If the API
    required an element, it would require us to parse this content
    just in order to generate HTML from it.

  .. method:: on_commented(self, comment, ar, cw)

    This is automatically called when a comment has been created or modified.
