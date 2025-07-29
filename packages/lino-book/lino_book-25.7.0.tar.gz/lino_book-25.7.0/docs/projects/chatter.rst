.. doctest docs/projects/chatter.rst
.. _book.projects.chatter:

===========================================
``chatter`` : an instant messaging system
===========================================

.. module:: lino_book.projects.chatter

A :term:`demo project` showing a little application for chatting.

Used in :doc:`/specs/notify`.

The chatter project has :setting:`users.with_nickname` activated and two users
(Andy and Bert) have nicknames while other users (Chloé, Robin) don't have a
nickname and thus are being shown with their full name.


>>> from lino import startup
>>> startup('lino_book.projects.chatter.settings')
>>> from lino.api.doctest import *

>>> headers = ["username", "first name", "last name", "nickname", "__str__()", "full name"]
>>> rows = [[u.username, u.first_name, u.last_name, u.nickname, str(u), u.get_full_name()]
...      for u in users.User.objects.all()]
>>> print(rstgen.table(headers, rows))
========== ============ =========== ========== ================ ==================
 username   first name   last name   nickname   __str__()        full name
---------- ------------ ----------- ---------- ---------------- ------------------
 andy       Andreas      Anderson    Andy       Andy             Andreas Anderson
 bert       Albert       Bernstein   Bert       Bert             Albert Bernstein
 chloe      Chloe        Cleoment               Chloe Cleoment   Chloe Cleoment
 robin      Robin        Rood                   Robin Rood       Robin Rood
========== ============ =========== ========== ================ ==================
<BLANKLINE>
