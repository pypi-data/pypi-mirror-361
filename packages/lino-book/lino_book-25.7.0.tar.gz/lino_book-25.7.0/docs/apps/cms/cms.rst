.. doctest docs/apps/cms/cms.rst
.. _cms.plugins.cms:

======================================
``cms`` (main plugin for Lino CMS)
======================================

In Lino CMS this plugin defines the :xfile:`locale` directory for all
translations.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *


>>> rt.show(checkdata.Messages)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
============= ===========...=== ========================================================= =======================
 Responsible   Database object   Message text                                              Checker
------------- -----------...--- --------------------------------------------------------- -----------------------
 Robin Rood    `...png <…>`__    Stored file size None differs from real file size 25620   uploads.UploadChecker
============= ===========...=== ========================================================= =======================
<BLANKLINE>



>>> obj = blogs.Entry.objects.get(id=2)
>>> obj.body_short_preview
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
'<a href="/admin/#/api/uploads/Uploads/17" target="_blank"><img
src="/media/thumbs/uploads/2022/09/crossroads.jpg" style="padding:4px;
max-width:100%; float:left; max-height:20ex" title="Crossroads, Kilham West
Field - geograph.org.uk - 2097672"/></a>Let\'s choose one or the other of the
either roads (or NOT)! And the hesitation, does it comes rarely(?), Nooo!, we
are very frequently and suddenly put to situations where we must choose between
roads. Of course, how to choose and what to choose are the questions. But did we
ever ask \'why?\' But of co...'
