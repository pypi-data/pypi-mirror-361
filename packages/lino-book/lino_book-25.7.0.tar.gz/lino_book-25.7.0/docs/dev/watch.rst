.. doctest docs/dev/watch.rst
.. _dev.watch:

======================================
``watch`` -- Watching database changes
======================================

The :mod:`lino_book.projects.watch` demo project illustrates some local
customizations.


This tutorial explains how to use the :mod:`lino.modlib.changes` plugin for
logging changes to individual rows of database tables and implementing a kind of
`audit trail <https://en.wikipedia.org/wiki/Audit_trail>`_.

This tutorial is a :term:`tested document` and
uses the :mod:`lino_book.projects.watch` sample application:

>>> from lino import startup
>>> startup('lino_book.projects.watch.settings')

To enable database change watching, you add :mod:`lino.modlib.changes`
to your :meth:`get_installed_plugins
<lino.core.site.Site.get_installed_plugins>` and then register "change
watchers" for every type of change you want to watch.

..
  You will also want to make your changes visible for users by adding
  the :class:`changes.ChangesByMaster
  <lino.modlib.changes.models.ChangesByMaster>` slave table to some of
  your detail layouts.

The example in this tutorial uses the :mod:`lino_xl.lib.contacts`
module.  It also adds a model `Entry` as an example of a watched slave model.

The "master" of a change watcher is the object to which every change should be
attributed.  In this example the master is *Partner*: every tracked change to
*Entry*, *Partner* **or** *Company* will be assigned to their *Partner* record.

In the :xfile:`settings.py` file we define our own subclass of :class:`Site
<lino.core.site.Site>`, with a :meth:`setup_actions
<lino.core.site.Site.setup_actions>` method to call :func:`watch_changes
<lino.modlib.changes.watch_changes>`.

.. literalinclude:: /../../book/lino_book/projects/watch/settings.py

The :file:`entries/models.py` file defines the `Entry` model and its data tables:

.. literalinclude:: /../../book/lino_book/projects/watch/entries/models.py

The :file:`tests/test_basics.py` file contains a unit test:

.. literalinclude:: /../../book/lino_book/projects/watch/tests/test_basics.py


Here is our demo fixture, which partly reproduces what we are doing in the
temporary database during djangotests:

.. literalinclude:: /../../book/lino_book/projects/watch/fixtures/demo.py


>>> from lino.api.doctest import *

>>> rt.show('changes.Changes')
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF +ELLIPSIS -SKIP
==== ============ ============================ ============= ============== =========== ============= =========== ============================================= ======== ================= =================
 ID   Author       time                         Change Type   Object type    object id   Master type   master id   Changes                                       Fields   Object            Master
---- ------------ ---------------------------- ------------- -------------- ----------- ------------- ----------- --------------------------------------------- -------- ----------------- -----------------
 2    Robin Rood   ...                          Update        Organization   82          Partner       82          name : 'My pub' --> 'Our pub'                 name     `Our pub <…>`__   `Our pub <…>`__
 1    Robin Rood   ...                          Create        Organization   82          Partner       82          Company(id=82,name='My pub',partner_ptr=82)            `Our pub <…>`__   `Our pub <…>`__
==== ============ ============================ ============= ============== =========== ============= =========== ============================================= ======== ================= =================
<BLANKLINE>
