.. doctest docs/dev/myroles.rst
.. _lino.tutorials.myroles:

============================================
Local customizations to the user permissions
============================================

This page explains how to locally override a user types module.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.myroles.settings')
>>> from lino.api.doctest import *

.. flush the database to remove data from a previous test run

    >>> from django.core.management import call_command
    >>> call_command('initdb', interactive=False) #doctest: +ELLIPSIS
    `initdb ` started on database .../lino_book/projects/myroles/default.db.
    ...



The example
===========

For example on a standard Lino Polly site (:mod:`lino_book.projects.polly`),
only a :term:`site manager` can see the global list of all polls. This
list is visible through :menuselection:`Explorer --> Polls --> Polls`.  A normal
user does not see that menu command.

We are going to apply a local customization. In our variant of a Lino
Polly application, *every* authenticated user (not only site admins)
can see that table.

Here is the :xfile:`settings.py` file used by this tutorial:

.. literalinclude:: ../../lino_book/projects/myroles/settings.py

In our :xfile:`settings.py` file, we override the :attr:`user_types_module
<lino.core.site.Site.user_types_module>` of the Polly :class:`Site` class and
set it to the Python path of our :file:`myroles.py` file::

    user_types_module = 'mysite.myroles'

Now we create this module, i.e. a file named :file:`myroles.py` with the
following content:

.. literalinclude:: ../../lino_book/projects/myroles/myroles.py

The first line imports everything from the standard module::

    from lino_xl.lib.xl.user_types import *

How did we know that the name of the standard user types module of a Lino Polly
is :mod:`lino_xl.lib.xl.user_types`? For example like this:

>>> from lino_book.projects.polly.settings import Site
>>> print(Site.user_types_module)
lino_xl.lib.xl.user_types

The following lines basically just set the :attr:`required_roles` of the
:class:`polls.AllPolls` table require the :class:`PollsUser` role::

  AllPolls.required_roles = dd.login_required(PollsUser)

Testing it
==========

Yes our local :file:`myroles.py` module is being imported at startup:

>>> print(settings.SITE.user_types_module)
lino_book.projects.myroles.myroles


The following code snippets are to test whether a normal user now
really can see all polls (i.e. has the :menuselection:`Explorer -->
Polls --> Polls` menu command):

>>> u = users.User(username="user", user_type="100")
>>> u.full_clean()
>>> u.save()
>>> show_menu('user')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Polls : My Polls, My Responses
- Explorer :
  - Polls : Polls
- Site : About
