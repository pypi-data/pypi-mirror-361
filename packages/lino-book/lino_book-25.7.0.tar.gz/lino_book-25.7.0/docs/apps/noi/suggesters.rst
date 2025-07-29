.. doctest docs/apps/noi/suggesters.rst
.. _specs.noi.suggesters:

======================
Suggesters in Lino Noi
======================


Compare the :fixture:`demo2` fixture of :mod:`lino.modlib.comments`.

.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1e.startup import *

The memo parser in :ref:`noi` has two suggesters:

>>> mp = settings.SITE.plugins.memo.parser

>>> pprint(mp.suggesters)  #doctest: +ELLIPSIS
{'#': <lino.modlib.memo.parser.Suggester object at ...>,
 '@': <lino.modlib.memo.parser.Suggester object at ...>}

Where ``#`` refers to a ticket and ``@`` refers to a user.

>>> print(mp.parse("This comment refers to #11 and @robin."))
This comment refers to <a href="/api/tickets/Tickets/11" title="#11 (Class-based Foos and Bars?)" style="text-decoration:none">#11</a> and <a href="/api/users/AllUsers/1" title="Robin Rood" style="text-decoration:none">@robin</a>.

If the word behind a suggester char does not point to any existing database row,
the text remains unchanged:

>>> print(mp.parse("This comment refers to #robin and @11."))
This comment refers to #robin and @11.

>>> print(mp.parse("This comment refers to # and @."))
This comment refers to # and @.

All parsing is done using a special anonymous user having `user_type`
:attr:`lino.modlib.users.UserTypes.admin` because otherwise the stored previews
of memo texts would depend on who saved them. You can override this by
specifying your own :term:`action request`:

>>> ses = rt.login('robin')
>>> print(mp.parse("This comment refers to #11 and @robin.", ar=ses))
This comment refers to <a href="…" title="#11 (Class-based Foos and Bars?)">#11</a> and <a href="…" title="Robin Rood">@robin</a>.
