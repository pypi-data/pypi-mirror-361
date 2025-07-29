.. doctest docs/projects/polls.rst
.. _dg.projects.polls:

===========================================
``polls`` : Django Polls tutorial
===========================================

.. module:: lino_book.projects.polls

A little application for managing polls, explained in :doc:`/dev/polls/index`.

>>> from lino import startup
>>> startup('lino_book.projects.polls.mysite.settings')

>>> from lino.api.doctest import *

>>> show_menu()
- Polls : Questions, Choices
- Site : About

>>> je = dd.plugins.jinja.renderer.jinja_env
>>> t = je.loader.load(je, "admin_main.html")
>>> t.filename.endswith("polls/mysite/config/admin_main.html")
True

>>> analyzer.show_dialog_actions()
<BLANKLINE>
