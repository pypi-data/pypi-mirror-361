.. doctest docs/specs/printing.rst
.. _specs.printing:

===========================================
``printing`` : Basic printing functionality
===========================================

..  Initialize doctest:

    >>> from lino import startup
    >>> startup('lino_book.projects.min9.settings')
    >>> from lino.api.shell import *
    >>> from lino.api.doctest import *


.. currentmodule:: lino.modlib.printing

As a :term:`application developer` you can use several approaches for adding
printing functionality to your application:

- The :class:`Printable` mixin adds a hard-coded "Print" button to your
  :term:`database model`.

- The :doc:`excerpts <excerpts>` plugin also causes a "Print" button to be added
  to database models, but in a more configurable way.

- :mod:`lino_xl.lib.appypod` adds a button to each :term:`grid window`, which
  prints the current grid as a table to pdf.

- A "report" (:mod:`lino.utils.report`) is a hard-coded sequence of
  tables and arbitrary content.

Lino has the following plugins related to printing:

- :mod:`lino.modlib.printing` -- general functionality for printing
- :mod:`lino_xl.lib.excerpts` -- :doc:`excerpts`
- :mod:`lino.modlib.jinja`
- :mod:`lino.modlib.weasyprint`
- :mod:`lino.modlib.wkhtmltopdf`

Plugin configuration
====================

.. setting:: printing.print_demo_objects

  The number of database rows per :term:`database model` for which to run the
  print method when loading demo fixtures during :manage:`prep`.

  The default value is 1.

  This is used as the default value for :attr:`Printable.print_demo_objects`.

Build methods
=============

.. glossary::

  build method

    The technology to use for building a :term:`printable document`.

We have *build methods*, *print actions* and mixins for *printable* database
objects.

The :term:`build method` specifies both the required **template format**
(usually each build method has its specific template language) and the format of
the **produced output** file.

>>> rt.show(printing.BuildMethods)  #doctest: +NORMALIZE_WHITESPACE
============ ============ ======================
 value        name         text
------------ ------------ ----------------------
 appydoc      appydoc      AppyDocBuildMethod
 appyodt      appyodt      AppyOdtBuildMethod
 appypdf      appypdf      AppyPdfBuildMethod
 appyrtf      appyrtf      AppyRtfBuildMethod
 latex        latex        LatexBuildMethod
 pub          pub          PublisherBuildMethod
 rtf          rtf          RtfBuildMethod
 weasy2html   weasy2html   WeasyHtmlBuildMethod
 weasy2pdf    weasy2pdf    WeasyPdfBuildMethod
 xml          xml          XmlBuildMethod
============ ============ ======================
<BLANKLINE>


The **print action** is either defined manually on the model, or dynamically at
startup when excerpts is installed.

The mixins defined in :class:`lino.modlib.printing` (:class:`Printable`,
:class:`TypedPrintable`, :class:`CachedPrintable` :class:`TypedPrintable`) are
needed to make your database objects printable. Note that when your application
uses :mod:`lino_xl.lib.excerpts`, you don't need to worry about their
difference, you just inherit from :class:`Printable`.


.. _tplcontext:

The template context
====================

When a :term:`printable document` is generated, Lino parses a template using
Jinja. Here is a list of template context names available when parsing a
template.

See also :meth:`lino.core.requests.BaseRequest.get_printable_context`

.. class:: PrintableContext

  .. attribute:: this

    The printable object instance

  .. attribute:: site

    shortcut for `settings.SITE`


.. tcname:: mtos

        "amount to string" using :func:`decfmt`

.. tcname:: iif

        :func:`iif <atelier.utils.iif>`

.. tcname:: tr(**kw)

        Shortcut to :meth:`babelitem <lino.core.site.Site.babelitem>`.

.. tcname:: _(s)

        gettext

.. tcname:: E

        HTML tag generator, see :mod:`etgen.html`

.. tcname:: unicode()

        the builtin Python :func:`unicode` function

.. tcname:: len()

        the builtin Python :func:`len` function

.. tcname:: settings``

        The Django :xfile:`settings.py` module

.. tcname:: site`

        shortcut for `settings.SITE`

.. tcname:: ar

        a Lino :class:`lino.core.requests.BaseRequest` instance around
        the calling Django request


.. tcname:: request`

        the Django HttpRequest instance
        (available in :xfile:`admin_main.html`,
        rendered by :meth:`get_main_html <lino.core.site.Site.get_main_html>`,
        which calls :func:`lino.modlib.jinja.render_from_ar`)



.. initialization for doctest

    >>> from lino import startup
    >>> startup('lino_book.projects.min9.settings')
    >>> from lino.api.shell import *
    >>> from lino.utils.format_date import fds, fdm, fdl, fdf
    >>> import datetime


.. _datefmt:

Date formatting functions
-------------------------

Lino includes shortcuts to `python-babel`'s
`date formatting functions <http://babel.pocoo.org/docs/dates/>`_:

.. tcname:: fds

    "format date short", see :ref:`datefmt`

.. tcname:: fdm

    "format date medium", see :ref:`datefmt`

.. tcname:: fdl

    "format date long", see :ref:`datefmt`

.. tcname:: fdf

    "format date full", see :ref:`datefmt`

.. tcname:: dtos

    deprecated for :tcname:`fds`

.. tcname:: dtosl

    deprecated for :tcname:`fdl`



Examples:

>>> d = datetime.date(2013,8,26)
>>> print(fds(d)) # short
26/08/2013
>>> print(fdm(d)) # medium
26 Aug 2013
>>> print(fdl(d)) # long
26 August 2013
>>> print(fdf(d)) # full
Monday, 26 August 2013





Printing a normal pdf table
===========================

>>> settings.SITE.appy_params.update(raiseOnError=True)
>>> url = 'http://127.0.0.1:8000/api/contacts/Partners?an=as_pdf'
>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> print(res.status_code)
200
>>> result = json.loads(res.content)
>>> print(result['success'])
True
>>> print(result['open_url'])
/media/cache/appypdf/127.0.0.1/contacts.Partners.pdf



Printing address labels
=======================

>>> settings.SITE.appy_params.update(raiseOnError=True)
>>> url = 'http://127.0.0.1:8000/api/contacts/Partners?an=print_labels'
>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> print(res.status_code)
200
>>> result = json.loads(res.content)
>>> print(result['success'])
True
>>> print(result['open_url'])
/media/cache/appypdf/127.0.0.1/contacts.Partners.pdf



Model mixins
============

.. class:: Printable

    Mixin for models for which Lino can generate a printable
    document.

    Extended by :class:`CachedPrintable` and :class:`TypedPrintable`.
    Other methods for printing a printable is to add an excerpt type
    or to provide your own subclass of DirectPrintAction.

    .. attribute:: print_demo_objects::

      The number of database rows of this :term:`database model` for which to
      run the `print` method when loading demo fixtures during :manage:`prep`.

      This is a class attribute of the database model. Default value is `None`,
      which means that the :setting:`printing.print_demo_objects` plugin setting
      applies. If they both are `None`, Lino will print all rows of this model
      during :manage:`prep`.

    .. method:: get_print_language(self)

        Return a Django language code to be activated when an instance
        of this is being printed.  The default implementation returns
        the Site's default language.

        Returning `None` is equivalent to the Site's default language.

    .. method:: get_print_templates(self, bm, action)

        Return a list of file names of templates for the specified
        build method.  Returning an empty list means that this item is
        not printable.  For subclasses of :class:`SimpleBuildMethod`
        the returned list may not contain more than 1 element.

        The default method calls
        :meth:`BuildMethod.get_default_template` and returns this as a
        list with one item.

    .. method:: get_printable_context(self, ar=None, **kw)

        Adds a series of names to the context used when rendering
        printable documents.

        :class:`lino_xl.lib.notes.models.Note` extends this.

    .. method:: get_body_template(self)

        Return the name of the body template to use when rendering this
        object in a printable excerpt (:mod:`lino_xl.lib.excerpts`).
        An empty string means that Lino should use the default value
        defined on the ExcerptType.

    .. method:: get_printable_demo_objects(cls, excerpt_type)

        Return an iterable of database rows for which Lino should generate a
        printable excerpt.

        This is being called by :mod:`lino_xl.lib.excerpts.fixtures.demo2`.

        Default behaviour is to return the first
        :attr:`Printable.print_demo_objects` rows in the database.


    .. method:: get_build_method(self)

        Return the build method to use when printing this object.

        This is expected to rather raise an exception than return
        `None`.

    .. method:: get_excerpt_options(self, ar, **kw)

        Set additional fields of newly created excerpts from this.  Called
        from
        :class:`lino_xl.lib.excerpts.models.ExcerptType.get_or_create_excerpt`.

    .. method:: before_printable_build(self, bm)

        This is called by print actions before the printable is being
        generated.  Application code may e.g. raise a `Warning`
        exception in order to refuse the print action.  The warning
        message can be a translatable string.


.. class:: CachedPrintable

    Mixin for Models that generate a unique external file at a
    determined place when being printed.

    Adds a "Print" button, a "Clear cache" button and a `build_time`
    field.

    The "Print" button of a :class:`CachedPrintable
    <lino.mixins.printable.CachedPrintable>` transparently handles the
    case when multiple rows are selected.  If multiple rows are
    selected (which is possible only when :attr:`cell_edit
    <lino.core.tables.AbstractTable.cell_edit>` is True), then it will
    automatically:

    - build the cached printable for those objects who don't yet have
      one

    - generate a single temporary pdf file which is a merge of these
      individual cached printable docs

    Database fields:

    .. attribute:: build_time

        Timestamp of the built target file. Contains `None`
        if no build hasn't been called yet.

    Actions:

    .. attribute:: do_print

        The action used to print this object.
        This is an instance of
        :class:`DirectPrintAction` or :class:`CachedPrintAction` by
        default.  And if :mod:`lino_xl.lib.excerpts` is installed,
        then :func:`set_excerpts_actions
        <lino_xl.lib.excerpts.set_excerpts_actions>` possibly replaces
        :attr:`do_print` by a
        :class:`lino_xl.lib.excerpts.CreateExcerpt` instance.

    .. attribute:: edit_template

.. class:: TypedPrintable

    A :class:`CachedPrintable` that uses a "Type" for deciding which
    template to use on a given instance.

    A TypedPrintable model must define itself a field ``type`` which
    is a ForeignKey to a Model that implements :class:`PrintableType`.

    Alternatively you can override :meth:`get_printable_type` if you
    want to name the field differently. An example of this is
    :attr:`ml.sales.TradingVoucher.imode`.


.. class:: PrintableType

    Base class for models that specify the
    :attr:`TypedPrintable.type`.

    .. attribute:: templates_group

        Default value for `templates_group` is the model's full name.

    .. attribute:: build_method

        A pointer to an item of :class:`BuildMethods`.

    .. attribute:: template

        The name of the file to be used as template.

        If this field is empty, Lino will use the filename returned by
        :meth:`lino.modlib.printing.Plugin.get_default_template`.

        The list of choices for this field depend on the
        :attr:`build_method`.  Ending must correspond to the
        :attr:`build_method`.

Utilities
=========

.. class:: CachedPrintableChecker

    Checks for missing cache files on all objects which inherit
    :class:`CachedPrintable`.

    When a CachedPrintable has a non-empty :attr:`build_time
    <CachedPrintable.build_time>` field, this means that the target
    file has been built.  That file might no longer exists for several
    reasons:

    - it has really beeen removed from the cache directory.

    - we are working in a copy of the database, using a different
      cache directory.

    - the computed name of the file has changed due to a change in
      configuration or code.

    An easy quick "fix" would be to set `build_time` to None, but this
    is not automatic because in cases of real data loss a system admin
    might want to have at least that timestamp in order to search for
    the lost file.


.. function:: weekdays(d)

    Yield a series of five dates, starting at the given date which should be a
    Monday.

    Utility function available in the default printable context.

    TODO: move this to lino_xl.lib.cal and let plugins add items to the
    printable context.

    >>> from lino.modlib.printing.models import weekdays
    >>> list(weekdays(i2d(20190603)))
    [datetime.date(2019, 6, 3), datetime.date(2019, 6, 4), datetime.date(2019, 6, 5), datetime.date(2019, 6, 6), datetime.date(2019, 6, 7)]




Print actions
=============

.. class:: BasePrintAction

    Base class for all "Print" actions.

.. class:: DirectPrintAction

    Print using a hard-coded template and without cache.

.. class:: CachedPrintAction

    A print action which uses a cache for the generated printable
    document and builds is only when it doesn't yet exist.

.. class:: ClearCacheAction

    Defines the :guilabel:`Clear cache` button on a Printable record.

    The `run_from_ui` method has an optional keyword argmuent
     `force`. This is set to True in `docs/tests/debts.rst`
     to avoid compliations.


.. class:: EditTemplate

    Edit the print template, i.e. the file specified by
    :meth:`Printable.get_print_templates`.

    The action available only when :mod:`lino.modlib.davlink` is
    installed, and only for users with `SiteStaff` role.

    If it is available, then it still works only when

    - your site has a local config directory
    - your :xfile:`webdav` directory (1) is published by your server under
      "/webdav" and (2) has a symbolic link named `config` which points
      to your local config directory.
    - the local config directory is writable by `www-data`

    **Factory template versus local template**

    The action automatically copies a factory template to the local
    config tree if necessary. Before doing so, it will ask for
    confirmation: :message:`Before you can edit this template we must
    create a local copy on the server.  This will exclude the template
    from future updates.`


Build methods
=============

.. class:: BuildMethods

    The choicelist of build methods offered on this site.

.. class:: BuildMethod

    Base class for all build methods.  A build method encapsulates the
    process of generating a "printable document" that inserts data
    from the database into a template, using a given combination of a
    template parser and post-processor.

    .. attribute:: use_webdav

        Whether this build method results is an editable file.  For
        example, `.odt` files are considered editable while `.pdf` files
        aren't.

        In that case the target will be in a webdav folder and the print
        action will respond `open_davlink_url` instead of the usual
        `open_url`, which extjs3 ui will implement by calling
        `Lino.davlink_open()` instead of the usual `window.open()`.

        When :mod:`lino.modlib.davlink` is not installed, this setting
        still influences the target path of resulting files, but the
        clients will not automatically recognize them as webdav-editable
        URLs.

.. class:: TemplatedBuildMethod

    A :class:`BuildMethod` which uses a template.

.. class:: DjangoBuildMethod

    A :class:`TemplatedBuildMethod` which uses Django's templating engine.


.. class:: XmlBuildMethod

    Generates .xml files from .xml templates.

.. class:: SimpleBuildMethod

    Base for build methods which use Lino's templating system
    (:meth:`find_config_file <lino.core.site.Site.find_config_file>`).

    TODO: check whether this extension to Django's templating system
    is still needed.


.. class:: CustomBuildMethod

    For example CourseToXls.

    Simple example::

        from lino.modlib.printing.utils import CustomBuildMethod

        class HelloWorld(CustomBuildMethod):
            target_ext = '.txt'
            name = 'hello'
            label = _("Hello")

            def custom_build(self, ar, obj, target):
                # this is your job
                file(target).write("Hello, world!")

        class MyModel(Model):
            say_hello = HelloWorld.create_action()




    .. method:: custom_build(self, ar, obj, target)

        Concrete subclasses must implement this.

        This is supposed to create a file named `target`.


.. class:: LatexBuildMethod

    Not actively used.
    Generates `.pdf` files from `.tex` templates.

.. class:: RtfBuildMethod

    Not actively used.
    Generates `.rtf` files from `.rtf` templates.

.. class:: PisaBuildMethod

    Deprecated.
    Generates .pdf files from .html templates.
    Requires `pisa <https://pypi.python.org/pypi/pisa>`_.
    Usage example see :mod:`lino_book.projects.pisa`.
