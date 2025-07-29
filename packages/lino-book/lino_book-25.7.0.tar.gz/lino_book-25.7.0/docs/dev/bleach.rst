.. doctest docs/dev/bleach.rst

.. _bleaching:

=========
Bleaching
=========

When an end user copies rich text from other applications into Lino, the text
can contain styles and other things that cause side effects when displaying or
printing them.  Or a malicious user might deliberately insert HTML with scripts
or other diabolic things in order to harm your server. In order to avoid such
problems, we remove any dangerous parts from content that gets entered into a
rich text field using the web interface. This process is called to "sanitize" or
to "bleach".



.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst

>>> import os
>>> from lino import startup
>>> startup('lino_book.projects.noi1r.settings')
>>> from lino.api.doctest import *

.. currentmodule:: lino.utils.soup

Usage
=====

All rich text fields (:class:`RichHtmlField To activate bleaching of all rich
text fields (:class:`RichHtmlField <lino.core.fields.RichHtmlField>`), get
bleached by default.  To deactivate this feature, set :attr:`textfield_bleached
<lino.core.site.Site.textfield_bleached>` to `False` in your
:xfile:`settings.py` file::

      textfield_bleached = False

You might also set :attr:`textfield_bleached
<lino.core.site.Site.textfield_bleached>` to `False`, but keep in mind that
this is only the default value.

The application developer can force bleaching to be activated or not for a
specific field by explicitly saying a :attr:`bleached
<lino.core.fields.RichTextfield.bleached>` argument when declaring the field.


How to bleach existing unbleached data
======================================

The :class:`lino.modlib.system.BleachChecker` data checker reports fields
whose content would change by bleach. This is useful when you activate
:ref:`bleaching` on a site with existing data.  After activating bleach, you
can check for unbleached content by saying::

  $ django-admin checkdata system.BleachChecker

After this you can use the web interface to inspect the data problems. To
manually bleach a single database object, simply save it using the web
interface. You should make sure that bleach does not remove any content which
is actually needed.  If this happens, you must manually restore the content of
the tested database objects, or restore a full backup and then set your
:attr:`bleach_allowed_tags <lino.core.site.Site.bleach_allowed_tags>` setting.

To bleach all existing data, you can say::

  $ django-admin checkdata system.BleachChecker --fix


Which mdels have bleachable fields?
===================================

Which models have bleachable fields?

>>> checker = checkdata.Checkers.get_by_value('system.BleachChecker')
>>> lst = [str(m) for m in checker.get_checkable_models()]
>>> print('\n'.join(sorted(lst)))
<class 'lino.modlib.comments.models.Comment'>
<class 'lino.modlib.tinymce.models.TextFieldTemplate'>
<class 'lino_noi.lib.cal.models.Event'>
<class 'lino_noi.lib.groups.models.Group'>
<class 'lino_noi.lib.tickets.models.Ticket'>
<class 'lino_xl.lib.accounting.models.PaymentTerm'>
<class 'lino_xl.lib.cal.models.Calendar'>
<class 'lino_xl.lib.cal.models.EventType'>
<class 'lino_xl.lib.cal.models.RecurrentEvent'>
<class 'lino_xl.lib.cal.models.Room'>
<class 'lino_xl.lib.cal.models.Task'>
<class 'lino_xl.lib.products.models.Category'>
<class 'lino_xl.lib.products.models.Product'>
<class 'lino_xl.lib.topics.models.Interest'>
<class 'lino_xl.lib.trading.models.InvoiceItem'>
<class 'lino_xl.lib.working.models.Session'>



.. _dg.sanitize.save:

Processing embedded images
==========================

This section verifies that the :func:`lino.utils.soup.sanitize` function has the
side effect of potentially creating :class:`uploads.Upload` database rows.

Prepare the test examples:

>>> import base64
>>> import lino_book
>>> from pathlib import Path
>>> logo_file = Path(lino_book.__file__).parent.parent / 'docs/data/pr/lino-pen.png'
>>> with logo_file.open('rb') as f:
...     logo = base64.b64encode(f.read()).decode('ascii')

>>> from lino.core.gfks import gfk2lookup
>>> def tidy_up():
...     # find this file and delete it.
...     for u in uploads.Upload.objects.order_by('-pk').all():
...         deletable = False
...         if u.file:
...             with u.file.open('rb') as f:
...                 if base64.b64encode(f.read()).decode('ascii') == logo:
...                     deletable = True
...         if deletable:
...             Comment = comments.Comment
...             Comment.objects.filter(**gfk2lookup(Comment.owner, u)).delete()
...             u.file.delete()
...             u.delete()

>>> tidy_up()

>>> imageDataURL = f"data:image/png;base64,{logo}"

>>> ses = rt.login('robin')
>>> content = f"""\
... <p>Here is an image:</p>
... <p><img src="{imageDataURL}" class="bar"></p>\
... """
>>> from lino.utils.soup import sanitize
>>> print(sanitize(content, save=True, ar=ses))
... #doctest: +ELLIPSIS
<p>Here is an image:</p>
<p>[file ...]</p>


>>> content = f"""\
... <p>Here is an image without src attribute:</p>
... <p><img class="bar"></p>\
... """
>>> print(sanitize(content, save=True, ar=ses))
... #doctest: +ELLIPSIS
<p>Here is an image without src attribute:</p>
<p><img class="bar"/></p>

>>> tidy_up()
>>> dd.is_installed('uploads')
True


Restify
=======


The restify function converts reSTructuredText markup into HTML.

>>> from lino.utils.restify import restify
>>> print(restify("A *greatly* **formatted** text: \n\n- one \n\n -two"))
... #doctest: +NORMALIZE_WHITESPACE
<p>A <em>greatly</em> <strong>formatted</strong> text:</p>
<ul class="simple">
<li>one</li>
</ul>
<blockquote>
-two</blockquote>
<BLANKLINE>



Historical notes
================


Until November 2024, we used the `bleach
<http://bleach.readthedocs.org/en/latest/>`_ Python package for sanitizing HTML
input. But this package had been  `deprecated in January 2023
<https://bluesock.org/~willkg/blog/dev/bleach_6_0_0_deprecation.html>`__. Now we
use our own function :func:`lino.utils.soup.sanitize`, which relies on
BeautifulSoup and is inspired by a  `blog post by Chase Seibert
<https://chase-seibert.github.io/blog/2011/01/28/sanitize-html-with-beautiful-soup.html>`__.

`bleach` until 20170225 required html5lib` version
`0.9999999` (7*"9") while the current version is `0.999999999`
(9*"9"). Which means that you might inadvertently break `bleach` when
you ask to update `html5lib`::

    $ pip install -U html5lib
    ...
    Successfully installed html5lib-0.999999999
    $ python -m bleach
    Traceback (most recent call last):
      File "/usr/lib/python2.7/runpy.py", line 163, in _run_module_as_main
        mod_name, _Error)
      File "/usr/lib/python2.7/runpy.py", line 111, in _get_module_details
        __import__(mod_name)  # Do not catch exceptions initializing package
      File "/site-packages/bleach/__init__.py", line 14, in <module>
        from html5lib.sanitizer import HTMLSanitizer
    ImportError: No module named sanitizer
