.. doctest docs/specs/uploads.rst
.. _specs.uploads:

=====================================
``uploads`` : Managing uploaded files
=====================================

.. module:: lino.modlib.uploads

The :mod:`lino.modlib.uploads` plugin adds functionality for managing
:term:`upload files <upload file>`.
We assume that you have read the :ref:`end-user docs <ug.plugins.uploads>`.


There is also an extension of this plugin, the :mod:`lino_xl.lib.uploads`
plugin, which is described in :doc:`/specs/avanti/uploads`.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *


Upload files
============

.. class:: Upload

    Django model representing an :term:`upload file`.

    .. attribute:: file

        Pointer to the uploaded file itself (a `Django FileField
        <https://docs.djangoproject.com/en/5.0/ref/models/fields/#filefield>`_).

    .. attribute:: file_size

        The size of the file in bytes. Not yet implemented.

    .. attribute:: mimetype

        The `media type <https://en.wikipedia.org/wiki/Media_type>`_ of the
        uploaded file.

        See also `this thread
        <https://stackoverflow.com/questions/643690/maximum-mimetype-length-when-storing-type-in-db>`_
        about length of MIME type field.

    .. attribute:: type

        The type of this upload.

        Pointer to :class:`UploadType`. The choices for this field are usually
        limited to those in the same *upload area*.

    .. attribute:: description

        A short description entered manually by the user.

    .. attribute:: volume

        A pointer to the :term:`library volume` where this file is stored.

    .. attribute:: upload_area

        The :term:`upload area` this file belongs to.

    .. attribute:: library_file

        The path of this file, relative the volume's root.

    .. attribute:: description_link

        Almost the same as :attr:`description`, but if :attr:`file` is
        not empty, the text is clickable, and clicking on it opens the
        uploaded file in a new browser window.

.. class:: Uploads

  Base class for all data tables of :term:`upload files <upload file>`.

.. class:: AllUploads

  Shows all :term:`upload files <upload file>` on this :term:`Lino site`.

  Visible to the :term:`end user` as :menuselection:`Explorer --> Office -->
  Upload files`.

  ..
    >>> show_menu_path('uploads.AllUploads', language="en")
    Explorer --> Office --> Upload files

>>> rt.show(uploads.AllUploads, language="en")
==== ===================================================== ================================= ================= ================= =====================
 ID   Description                                           File                              Upload type       Uploaded by       Attached to
---- ----------------------------------------------------- --------------------------------- ----------------- ----------------- ---------------------
 11   Found on 2025-03-12 by uploads.UploadsFolderChecker   uploads/2025/03/foo.pdf                             Rolf Rompen
 10   Found on 2025-03-12 by uploads.UploadsFolderChecker   uploads/orphan.txt                                  Rolf Rompen
 9                                                          uploads/2025/03/PRC_21_2025.pdf   Source document   Robin Rood        `PRC 21/2025 <…>`__
 8                                                          uploads/2025/03/PRC_20_2025.pdf   Source document   Rolf Rompen       `PRC 20/2025 <…>`__
 7                                                          uploads/2025/03/PRC_19_2025.pdf   Source document   Romain Raffault   `PRC 19/2025 <…>`__
 6                                                          uploads/2025/03/PRC_18_2025.pdf   Source document   Robin Rood        `PRC 18/2025 <…>`__
 5                                                          uploads/2025/03/PRC_17_2025.pdf   Source document   Rolf Rompen       `PRC 17/2025 <…>`__
 4                                                          uploads/2025/03/PRC_16_2025.pdf   Source document   Romain Raffault   `PRC 16/2025 <…>`__
 3                                                          uploads/2025/03/PRC_15_2025.pdf   Source document   Robin Rood        `PRC 15/2025 <…>`__
 2    screenshot-toolbar.png
 1    Screenshot 20250124 104858.png
==== ===================================================== ================================= ================= ================= =====================
<BLANKLINE>


.. class:: AreaUploads

    Mixin for tables of :term:`upload files <upload file>` where the
    :term:`upload area` is known.

    The summary displays the :term:`upload files <upload file>` as a list
    grouped by uploads type.

    This is inherited by :class:`UploadsByController`.

    This also works on :class:`lino_welfare.modlib.uploads.UploadsByProject` and
    their subclasses for the different `_upload_area`.


.. class:: MyUploads

    Shows my uploads (i.e. those whose author is the requesting user).


.. class:: UploadBase

    Abstract base class of :class:`Upload`
    encapsulating some really basic functionality.

    Its usage is deprecated. If you were inheriting from
    :class:`lino.mixins.Uploadable`, you should convert that model to point to
    an :class:`Upload` instead.




Upload areas
============

The application developer can define **upload areas**.  Every upload area has
its list of upload types.  The default has only one upload area.

>>> rt.show(uploads.UploadAreas, language="en")
======= ========= =========
 value   name      text
------- --------- ---------
 90      general   Uploads
======= ========= =========
<BLANKLINE>

For example :ref:`welfare` extends this list.


Upload types
============

.. class:: UploadType

    Django model representing an :term:`upload type`.

    .. attribute:: shortcut

        Optional pointer to a virtual **upload shortcut** field.  If
        this is not empty, then the given shortcut field will manage
        uploads of this type.  See also :class:`Shortcuts`.

.. class:: UploadTypes

    The table with all existing upload types.

    This usually is accessible via the `Configure` menu.

Upload controllers
==================

An :term:`upload file` is usually **attached** to a another database object
called its :term:`controller <upload controller>`. Upload files without a
controller are considered "useless", and the :term:`site manager` should decide
what to do with them.

.. glossary::

  upload controller

    A database object that can potentially have :term:`uploaded files <upload
    file>` associated to it.

    Any database model that inherits from :class:`UploadController`.

.. class:: UploadController

    Model mixin for database objects that can have :term:`upload files <upload
    file>` associated to them.

    Turns a model into an :term:`upload controller`.

    .. attribute:: show_uploads

        Opens a :term:`data window` with the :term:`uploaded files <upload
        file>` associated to this :term:`database object`.

        This action is automatically shown in the :term:`toolbar` as a
        :guilabel:`❏` button.

Additionally to :attr:`UploadController.show_uploads`, the :term:`application
developer` can decide to add a :term:`slave panel` :class:`UploadsByController`
to the :term:`detail layout` of any :term:`upload controller`.


.. class:: UploadsByController

    Shows the :term:`uploaded files <upload file>` associated to this
    :term:`database object`.

This panel gives a summary of the :term:`upload files <upload file>` linked to
this :term:`database row`. This summary is influenced by the configuration of
:term:`upload types <upload type>`.


>>> # obj = vat.VatAccountInvoice.objects.get(id=105)
>>> obj = vat.VatAccountInvoice.objects.get(number=20, fiscal_year__ref="2025")
>>> rt.show(uploads.UploadsByController, obj)
Eingangsdokument: `PRC_20_2025.pdf <…>`__ `⎙ </media/uploads/2025/03/PRC_20_2025.pdf>`__



Upload shortcuts
================

The application developer can define **upload shortcuts**.  Every upload
shortcut will create an **upload shortcut field**, a virtual field with a set
of actions for quickly uploading or viewing uploads of a particular type for a
given database object.

Usage:

- Declare your Site's upload shortcuts from within your
  :attr:`workflows_module
  <lino.core.site.Site.workflows_module>`. For example::

      from lino.modlib.uploads.choicelists import add_shortcut as add
      add('contacts.Person', 'uploaded_foos', _("Foos"))

- Make the ``uploaded_foos`` field visible in some detail layout.

- Using the web interface, select :menuselection:`Configure --> Office
  --> Upload types`, create an upload type named "Foo" and set its
  `shortcut` field to "Foos".

- Upload a file from your PC to the server.
- Open the uploaded file in a new browser window


.. class:: Shortcuts

    The list of available upload shortcut fields in this application.

>>> rt.show(uploads.Shortcuts, language="en")
==================================== ================= =================
 value                                name              text
------------------------------------ ----------------- -----------------
 accounting.Voucher.source_document   source_document   Source document
==================================== ================= =================
<BLANKLINE>


.. function:: add_shortcut(*args, **kw)

    Declare an upload shortcut field. This is designed to be called from within
    a :attr:`workflows_module <lino.core.site.Site.workflows_module>` or a
    :meth:`lino.core.plugins.Plugin.before_analyze`.


.. xfile:: uploads

  A directory below your :xfile:`media` directory. This is where web uploads
  (i.e. files uploaded via the web interface) are stored.  Lino creates this
  directory at startup if it doesn't exist.

Previewers
==========


Lino currently offers only two previewers, "full" and "small", and these two
names are used in miscellaneous places of the source code. For example when
rendering an :class:`Upload` row as a list item, Lino uses the "small"
previewer, but when rendering a detail view it uses the "full" previewer.


Data checkers
=============

This plugin defines two :term:`data checkers <data checker>`:

.. class:: UploadChecker
.. class:: UploadsFolderChecker

  Find orphaned files in uploads folder.

  Walks through the :term:`uploads folder` and reports files for which there is
  no upload entry
