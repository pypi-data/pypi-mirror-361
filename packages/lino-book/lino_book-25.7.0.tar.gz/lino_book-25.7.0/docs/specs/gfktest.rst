.. _lino.tutorial.gfks:

==============================
A tested example of GFK fields
==============================

..  doctest initialization:

    >>> import lino
    >>> lino.startup('lino_book.projects.gfktest.settings.demo')
    >>> from lino.api.doctest import *
    >>> from django.db.models import Q
    >>> from django.core.management import call_command
    >>> call_command('initdb', interactive=False, verbosity=0) #doctest: +ELLIPSIS
    >>> Member = rt.models.gfktest.Member
    >>> Comment = rt.models.gfktest.Comment
    >>> Note = rt.models.gfktest.Note
    >>> Memo = rt.models.gfktest.Memo

This tutorial project
uses the :mod:`lino_book.projects.gfktest` demo application
to illustrate some aspects of :doc:`/dev/gfks`.

The :xfile:`models.py` file defines four database models:

.. literalinclude:: /../../book/lino_book/projects/gfktest/lib/gfktest/models.py

A `Member` is the potential owner of the other three things.

A `Comment` has `allow_cascaded_delete` and thus will be silently deleted if the owner gets deleted.
A `Note` does not allow cascaded delete, and thus will cause a veto when we try to delete a member which is owner of some note.
A `Memo` has a nullable `owner` field and thus will be cleared when we delete the owner.

This project also uses :mod:`lino.modlib.contenttypes`. We define this
in our :xfile:`settings.py` module:

.. literalinclude:: /../../book/lino_book/projects/gfktest/settings/__init__.py


A utility function:

>>> def status():
...     return [m.objects.all().count() for m in [Member, Comment, Note, Memo]]
...

We create a member and three GFK-related objects whose `owner` fields
point to that member. And then we try to delete that member.

>>> mbr = Member(name="John")
>>> mbr.save()
>>> Comment(owner=mbr, text="Just a comment").save()
>>> Note(owner=mbr, text="John owes us 100€").save()
>>> Memo(owner=mbr, text="About John and his friends").save()

>>> print(status())
[1, 1, 1, 1]

The :meth:`disable_delete <lino.core.model.Model.disable_delete>`
method also sees these objects:

>>> print(mbr.disable_delete())
Cannot delete member John because 1 notes refer to it.

This means that Lino would prevent users from deleting this member
through the web interface.

Lino also protects normal application code from deleting a member:

>>> mbr.delete()
Traceback (most recent call last):
  ...
Warning: Cannot delete member John because 1 notes refer to it.

All objects are still there:

>>> print(status())
[1, 1, 1, 1]

The above behaviour is thanks to a `pre_delete_handler` which Lino
adds automatically.

We can disable this `pre_delete_handler` and use Django's raw `delete`
method in order produce broken GFKs:

>>> from django.db.models.signals import pre_delete
>>> from lino.core.model import pre_delete_handler
>>> pre_delete.disconnect(pre_delete_handler) in (None, True)
True

(Above syntax is because Django 1.6 returns None while 1.7+ returns True)

Now deleting the member will not fail:

>>> from django.db import models
>>> models.Model.delete(mbr) in (None, (1, {u'gfktest.Member': 1}))
True

Note: With Django 1.8 , the method models.Model.delete() doesn't
return anything, while since 1.8 it returns a dict describing the
number of objects deleted.

And it will leave the GFK-related objects in the database.

>>> print(status())
[0, 1, 1, 1]

The users of a Lino application can see these broken GFKs by opening
the :class:`BrokenGFKs <lino.modlib.contenttypes.models.BrokenGFKs>`
table:

>>> rt.show(gfks.BrokenGFKs)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
================= ======================== ======================================================== ========
 Database model    Database object          Message                                                  Action
----------------- ------------------------ -------------------------------------------------------- --------
 `comment <…>`__   `Comment object <…>`__   Invalid primary key 1 for gfktest.Member in `owner_id`   delete
 `note <…>`__      `Note object <…>`__      Invalid primary key 1 for gfktest.Member in `owner_id`   manual
 `memo <…>`__      `Memo object <…>`__      Invalid primary key 1 for gfktest.Member in `owner_id`   clear
================= ======================== ======================================================== ========
<BLANKLINE>


TODO: a :term:`django-admin command` to cleanup broken GFK fields. This would
execute the suggested actions (delete and clear) without any further
user interaction. Attention:

Note that in plain Django you can achieve some of the above things by
using `GenericRelation
<https://docs.djangoproject.com/en/5.0/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericRelation>`_
fields.  That is, if we define a GenericRelation from Member to every
model which potentially points to it.  In our case three
GenericRelation objects.

A detailed comparison is yet to be written, but it seems that Django's
approach is uncomplete compared to what Lino can do.


Tested twice
============

This tutorial project is tested twice.  Most things which we tested in
the present document are also being tested in a plain unittest module:

.. literalinclude:: /../../book/lino_book/projects/gfktest/test_gfk.py
