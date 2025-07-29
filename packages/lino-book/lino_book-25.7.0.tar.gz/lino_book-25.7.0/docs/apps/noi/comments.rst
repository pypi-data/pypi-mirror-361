.. doctest docs/apps/noi/comments.rst
.. _noi.specs.comments:

==============================
``comments`` in Noi
==============================

.. currentmodule:: lino.modlib.comments


The :mod:`lino.modlib.comments` plugin in :ref:`noi` is configured and used to
satisfy the application requirements.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *



Overview
========

Public comments in :ref:`noi` are visible even to anonymous users.

There are seven :class:`Commentable` models in :ref:`noi`, but only tickets have
a `CommentsByRFC` panel in their detail.

>>> pprint(list(rt.models_by_base(comments.Commentable)))
[<class 'lino_xl.lib.contacts.models.Company'>,
 <class 'lino_xl.lib.contacts.models.Partner'>,
 <class 'lino_noi.lib.contacts.models.Person'>,
 <class 'lino_noi.lib.groups.models.Group'>,
 <class 'lino_noi.lib.tickets.models.Ticket'>,
 <class 'lino.modlib.uploads.models.Upload'>]

Whether a comment is private or not depends on its :term:`discussion topic`:
Comments on a ticket are public when neither the ticket nor its site are marked
private.

Comments are private by default:

>>> dd.plugins.comments.private_default
True

Comments on a team are public when the team is not private.

.. _dg.plugins.comments.visibility:

Visibility of comments
======================

The demo database contains 420 comments, 84 of which have no team.
49 comments are public and 371 are confidential.

>>> comments.Comment.objects.all().count()
504
>>> comments.Comment.objects.filter(group__isnull=False).count()
84
>>> comments.Comment.objects.filter(group__isnull=False).first()
Comment #253 ('Comment #253')

>>> comments.Comment.objects.filter(ticket__isnull=False).count()
84
>>> comments.Comment.objects.filter(ticket__isnull=False).first()
Comment #337 ('Comment #337')
>>> comments.Comment.objects.filter(ticket=None).count()
420
>>> comments.Comment.objects.filter(private=False).count()
49
>>> comments.Comment.objects.filter(private=True).count()
455

>>> from django.db.models import Q
>>> rt.login("robin").show(comments.Comments,
...     column_names="id ticket__group user owner",
...     filter=Q(ticket__isnull=False),
...     limit=20, display_mode=DISPLAY_MODE_GRID)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
===== ============ ================= =============================================
 ID    Team         Author            Topic
----- ------------ ----------------- ---------------------------------------------
 337                Jean              `#116 (Why <p> tags are so bar) <…>`__
 338                Luc               `#116 (Why <p> tags are so bar) <…>`__
 339                Marc              `#116 (Why <p> tags are so bar) <…>`__
 340                Mathieu           `#116 (Why <p> tags are so bar) <…>`__
 341                Romain Raffault   `#116 (Why <p> tags are so bar) <…>`__
 342                Rolf Rompen       `#116 (Why <p> tags are so bar) <…>`__
 343                Robin Rood        `#116 (Why <p> tags are so bar) <…>`__
 344   Developers   Jean              `#115 (Cannot delete foo) <…>`__
 345   Developers   Luc               `#115 (Cannot delete foo) <…>`__
 346   Developers   Marc              `#115 (Cannot delete foo) <…>`__
 347   Developers   Mathieu           `#115 (Cannot delete foo) <…>`__
 348   Developers   Romain Raffault   `#115 (Cannot delete foo) <…>`__
 349   Developers   Rolf Rompen       `#115 (Cannot delete foo) <…>`__
 350   Developers   Robin Rood        `#115 (Cannot delete foo) <…>`__
 351                Jean              `#114 (No more foo when bar is gone) <…>`__
 352                Luc               `#114 (No more foo when bar is gone) <…>`__
 353                Marc              `#114 (No more foo when bar is gone) <…>`__
 354                Mathieu           `#114 (No more foo when bar is gone) <…>`__
 355                Romain Raffault   `#114 (No more foo when bar is gone) <…>`__
 356                Rolf Rompen       `#114 (No more foo when bar is gone) <…>`__
===== ============ ================= =============================================
<BLANKLINE>




Marc is a customer, so he can see only comments that are (1) public OR (2) his
own OR (3) about a group ("team") that he can see OR (4) about something that he
can see.

Comments in Noi can be about tickets or about groups.

- marc can see tickets that are (public OR his own) AND in a group that he can see
- marc can see groups that are (public OR of which he is a member)

>>> qs = rt.login('marc').spawn(comments.RecentComments).data_iterator
>>> printsql(qs)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
SELECT comments_comment.id,
       comments_comment.modified,
       comments_comment.created,
       comments_comment.body,
       comments_comment.body_short_preview,
       comments_comment.body_full_preview,
       comments_comment.user_id,
       comments_comment.owner_type_id,
       comments_comment.owner_id,
       comments_comment.reply_to_id,
       comments_comment.private,
       comments_comment.comment_type_id,
       COUNT(T5.id) AS num_replies,
       COUNT(comments_reaction.id) AS num_reactions
FROM comments_comment
LEFT OUTER JOIN groups_group ON (comments_comment.owner_id = groups_group.id
                                 AND (comments_comment.owner_type_id = 65))
LEFT OUTER JOIN tickets_ticket ON (comments_comment.owner_id = tickets_ticket.id
                                   AND (comments_comment.owner_type_id = 42))
LEFT OUTER JOIN comments_comment T5 ON (comments_comment.id = T5.reply_to_id)
LEFT OUTER JOIN comments_reaction ON (comments_comment.id = comments_reaction.comment_id)
WHERE ((NOT comments_comment.private
        OR comments_comment.user_id = 4)
       AND (groups_group.id IS NULL
            OR groups_group.id IN
              (SELECT DISTINCT U0.id
               FROM groups_group U0
               LEFT OUTER JOIN groups_membership U1 ON (U0.id = U1.group_id)
               WHERE (NOT U0.private
                      OR U1.user_id = 4)))
       AND (tickets_ticket.id IS NULL
            OR tickets_ticket.id IN
              (SELECT DISTINCT U0.id
               FROM tickets_ticket U0
               LEFT OUTER JOIN groups_group U1 ON (U0.group_id = U1.id)
               LEFT OUTER JOIN groups_membership U2 ON (U1.id = U2.group_id)
               WHERE ((NOT U1.private
                       AND NOT U0.private)
                      OR U2.user_id = 4
                      OR U0.user_id = 4))))
GROUP BY comments_comment.id,
         comments_comment.modified,
         comments_comment.created,
         comments_comment.body,
         comments_comment.body_short_preview,
         comments_comment.body_full_preview,
         comments_comment.user_id,
         comments_comment.owner_type_id,
         comments_comment.owner_id,
         comments_comment.reply_to_id,
         comments_comment.private,
         comments_comment.comment_type_id
ORDER BY comments_comment.created DESC

>>> rt.login("robin").show(comments.RecentComments,
...     column_names="id ticket__group user owner",
...     filter=Q(ticket__isnull=False),
...     limit=10, display_mode=DISPLAY_MODE_GRID)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===== ========== ================= ============================================
 ID    Team       Author            Topic
----- ---------- ----------------- --------------------------------------------
 420   Managers   Robin Rood        `#105 (Irritating message when bar) <…>`__
 419   Managers   Rolf Rompen       `#105 (Irritating message when bar) <…>`__
 418   Managers   Romain Raffault   `#105 (Irritating message when bar) <…>`__
 417   Managers   Mathieu           `#105 (Irritating message when bar) <…>`__
 416   Managers   Marc              `#105 (Irritating message when bar) <…>`__
 415   Managers   Luc               `#105 (Irritating message when bar) <…>`__
 414   Managers   Jean              `#105 (Irritating message when bar) <…>`__
 413              Robin Rood        `#106 (How can I see where bar?) <…>`__
 412              Rolf Rompen       `#106 (How can I see where bar?) <…>`__
 411              Romain Raffault   `#106 (How can I see where bar?) <…>`__
===== ========== ================= ============================================
<BLANKLINE>


>>> rt.login("marc").show(comments.RecentComments,
...     column_names="id ticket__group user owner",
...     filter=Q(ticket__isnull=False),
...     limit=10, display_mode=DISPLAY_MODE_GRID)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===== ============ ================= =============================================================
 ID    Team         Author            Topic
----- ------------ ----------------- -------------------------------------------------------------
 406   Sales team   Robin Rood        `#107 (Misc optimizations in Baz) <…>`__
 405   Sales team   Rolf Rompen       `#107 (Misc optimizations in Baz) <…>`__
 404   Sales team   Romain Raffault   `#107 (Misc optimizations in Baz) <…>`__
 403   Sales team   Mathieu           `#107 (Misc optimizations in Baz) <…>`__
 402   Sales team   Marc              `#107 (Misc optimizations in Baz) <…>`__
 401   Sales team   Luc               `#107 (Misc optimizations in Baz) <…>`__
 400   Sales team   Jean              `#107 (Misc optimizations in Baz) <…>`__
 395                Marc              `#108 (Default account in invoices per partner) <…>`__
 392   Developers   Robin Rood        `#109 ('NoneType' object has no attribute 'isocode') <…>`__
 391   Developers   Rolf Rompen       `#109 ('NoneType' object has no attribute 'isocode') <…>`__
===== ============ ================= =============================================================
<BLANKLINE>


Anonymous users they see only public comments.

>>> rt.show(comments.RecentComments,
...     column_names="id ticket__group user owner",
...     filter=Q(ticket__isnull=False),
...     limit=10, display_mode=DISPLAY_MODE_GRID)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===== ============ ================= =============================================================
 ID    Team         Author            Topic
----- ------------ ----------------- -------------------------------------------------------------
 406   Sales team   Robin Rood        `#107 (Misc optimizations in Baz) <…>`__
 405   Sales team   Rolf Rompen       `#107 (Misc optimizations in Baz) <…>`__
 404   Sales team   Romain Raffault   `#107 (Misc optimizations in Baz) <…>`__
 403   Sales team   Mathieu           `#107 (Misc optimizations in Baz) <…>`__
 402   Sales team   Marc              `#107 (Misc optimizations in Baz) <…>`__
 401   Sales team   Luc               `#107 (Misc optimizations in Baz) <…>`__
 400   Sales team   Jean              `#107 (Misc optimizations in Baz) <…>`__
 392   Developers   Robin Rood        `#109 ('NoneType' object has no attribute 'isocode') <…>`__
 391   Developers   Rolf Rompen       `#109 ('NoneType' object has no attribute 'isocode') <…>`__
 390   Developers   Romain Raffault   `#109 ('NoneType' object has no attribute 'isocode') <…>`__
===== ============ ================= =============================================================
<BLANKLINE>


>>> rows = []
>>> views = (comments.Comments, tickets.Tickets, groups.Groups)
>>> headers = ["User", "type"] + [i.__name__ for i in views]
>>> user_list = [users.User.get_anonymous_user()] + list(users.User.objects.all())
>>> for u in user_list:
...    cells = [str(u.username), u.user_type.name]
...    for dv in views:
...       qs = dv.create_request(user=u).data_iterator
...       cells.append(str(qs.count()))
...    rows.append(cells)
>>> print(rstgen.table(headers, rows))
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ============= ========== ========= ========
 User        type          Comments   Tickets   Groups
----------- ------------- ---------- --------- --------
 anonymous   anonymous     28         39        0
 jean        developer     504        116       3
 luc         developer     476        116       2
 marc        customer      85         50        2
 mathieu     contributor   91         67        3
 romain      admin         504        116       3
 rolf        admin         504        116       3
 robin       admin         504        116       3
=========== ============= ========== ========= ========
<BLANKLINE>



.. _ticket5759:

#5759 (Anonymous can GET private comments)
==========================================

Ticket :ticket:`5759` (Anonymous can GET private comments) was a security issue
between 20240920 and 20241001.
For example the following request failed to cause an exception.

Comment 420 is confidential:

>>> obj = comments.Comment.objects.get(pk=420)
>>> obj.private
True

An anonymous request may of course not see it:

>>> test_client.cookies  # nobody is signed in
<SimpleCookie: >

When processing the incoming request, Lino logs a warning in the logger and then
returns a 404 error:

>>> res = test_client.get("/api/comments/RecentComments/420")  #doctest: +ELLIPSIS
Error during ApiElement.get(): Invalid request for '420' on comments.RecentComments (Row 420 does not exist on comments.RecentComments)
Row 420 does not exist on comments.RecentComments
Traceback (most recent call last):
...
django.http.response.Http404: Row 420 does not exist on comments.RecentComments
Not Found: /api/comments/RecentComments/420

>>> res.status_code
404

It would be more correct to return 403 (Forbidden) instead of 404 (Not found),
at least in above case, because the requested comment 420 does exist, only the
user lacks permission to see it.  The case below is quite similar, except that a
comment with id 123456789 does not exist:

>>> res = test_client.get("/api/comments/RecentComments/123456789")
... #doctest: -REPORT_UDIFF +ELLIPSIS
Error during ApiElement.get(): Invalid request for '123456789' on comments.RecentComments (Row 123456789 does not exist on comments.RecentComments)
Row 123456789 does not exist on comments.RecentComments
Traceback (most recent call last):
...
django.http.response.Http404: Row 123456789 does not exist on comments.RecentComments
Not Found: /api/comments/RecentComments/123456789

>>> res.status_code
404

In both cases we return the same error code until further notice because
differentiating them would need an additional database query.

Ticket :ticket:`5759` had been introduced by :ticket:`5751` (ObjectDoesNotExist:
Invalid primary key 4968 for avanti.Clients), which came because avanti.Clients
has default table parameters that show only registered clients. When the user
manually removed that filter and then double-clicked on a client that was
usually filtered out, Lino gave this (false) error.


.. _ticket5763:

#5763 (Big unreadable warning with HTML tags)
=============================================

:ticket:`5763` (A permalink with Bad request shows a big unreadable warning with
HTML tags)

TODO: The React front end does above call as an AJAX call and expects a
JSON-encoded response. But Lino returns Django's default HttpResponseNotFound
response, which is in HTML. That's why the user sees a big red warning saying

  **Bad request**

  <!DOCTYPE html> <html lang="en"> <head> <meta http-equiv="content-type"
  content="text/html; charset=utf-8"> <title>Page not found at
  /media/cache/json/Lino_comments.Comments.420_000_en.json</title> <meta
  name="robots" content="NONE,NOARCHIVE"> <style> html * { padding:0; margin:0;
  ...

>>> print(res.content.decode())  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
<!DOCTYPE html>
<html lang="en">
<head>
...
