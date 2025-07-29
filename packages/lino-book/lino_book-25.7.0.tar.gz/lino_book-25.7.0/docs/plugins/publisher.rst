.. doctest docs/plugins/publisher.rst
.. _dg.plugins.publisher:

======================================================
``publisher`` : render database content as styled html
======================================================

.. module:: lino.modlib.publisher

.. currentmodule:: lino.modlib.publisher


The :mod:`lino.modlib.publisher` plugin adds the notion of :term:`content pages
<content page>` used to produce the pages of websites or books.


It doesn't add any database model, but a choicelist, a model mixin and an
action. It also adds a printing build method
(:class:`lino.modlib.printing.BuildMethods`).


.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino import startup
>>> startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *
>>> from django.db.models import Q

Configuration
=============

.. setting:: publisher.use_markup

  Whether to use markup (instead of wysiwyg) for editing content.

  When this is `False`, the body of pages gets edited using a wysiwyg editor and
  stored as (bleached) html.


Content pages
=============

.. glossary::

  content page

    The basic building unit of a website or book, consisting of a title and a
    body.

>>> rt.show('publisher.Pages', display_mode="grid", filter=Q(parent=None))
=========== =============================== ====
 Reference   Title                           ID
----------- ------------------------------- ----
 index       Home                            1
 index       Startseite                      2
 index       Départ                          3
             Terms and conditions            4
             Allgemeine Geschäftsbediungen   5
             Conditions générales            6
             Privacy policy                  7
             Datenschutz                     8
             Privacy policy                  9
             Cookie settings                 10
             Cookie settings                 11
             Cookie settings                 12
             Copyright                       13
             Autorenrecht                    14
             Droits d'auteur                 15
             About us                        16
             Über uns                        17
             À propos                        18
=========== =============================== ====
<BLANKLINE>


>>> home = publisher.Page.objects.get(pk=1)
>>> rt.show('publisher.TranslationsByPage', master_instance=home)
(de) `Startseite <…>`__, (fr) `Départ <…>`__

>>> rt.show('publisher.TranslationsByPage', master_instance=home, nosummary=True)
=========== ============ ========== ====
 Reference   Title        Language   ID
----------- ------------ ---------- ----
 index       Startseite   de         2
 index       Départ       fr         3
=========== ============ ========== ====
<BLANKLINE>

When I am on the English home page, the link to translation DE will redirect me
to page #25:

>>> test_client.get("/p/1?ul=de")
<HttpResponseRedirect status_code=302, "text/html; charset=utf-8", url="/p/2?ul=de">

The same happens when I am on the French home page:

>>> test_client.get("/p/3?ul=de")
<HttpResponseRedirect status_code=302, "text/html; charset=utf-8", url="/p/2?ul=de">



The `previous_page` fields have been updated:

>>> rt.show(publisher.Pages, column_names="id title previous_page",
... display_mode="grid", filter=Q(language="en"), language="en")
... #doctest: +REPORT_UDIFF
==== ====================== ======================
 ID   Title                  Previous page
---- ---------------------- ----------------------
 1    Home
 4    Terms and conditions   Conditions générales
 7    Privacy policy         Conditions générales
 10   Cookie settings        Privacy policy
 13   Copyright              Cookie settings
 16   About us               Droits d'auteur
 19   Blog                   Home
 22   Services               Blog
 23   Washing                Services
 24   Drying                 Washing
 25   Air drying             Drying
 26   Machine drying         Air drying
 27   Drying foos            Machine drying
 28   Drying bars            Drying foos
 29   Drying bazes           Drying bars
 30   Ironing                Drying bazes
 31   Prices                 Ironing
 32   Photos                 Prices
 33   Default formatting     Photos
 34   Thumbnail              Default formatting
 35   Thumbnail left         Thumbnail
 36   Tiny thumbnail         Thumbnail left
 37   Tiny thumbnail left    Tiny thumbnail
 38   Wide                   Tiny thumbnail left
 39   Gallery                Wide
 40   About us               Gallery
 41   Team                   About us
 42   History                Team
 43   Contact                History
 44   Terms & conditions     Contact
==== ====================== ======================
<BLANKLINE>


Classes reference
=================

.. class:: Page

  The Django model that represents a :term:`content page`.



.. class:: PublisherBuildMethod

  This deserves better documentation.


.. class:: Publishable

  Model mixin to add to models that are potentially publishable.

  .. attribute:: publisher_template

    The name of the template to use when rendering a database row via the
    publisher interface.

    "publisher/page.pub.html"

  .. attribute:: preview_publication

    Show this :term:`database row` via the publisher interface.

    Icon: 🌐

.. class:: PublishableContent

    Model mixin to add to models that are potentially publishable.

    Inherits from :class:`Publishable`.

    .. attribute:: language

      The language of this content.

    .. attribute:: publishing_state

      Default value is 'draft'

      Pointer to :class:`PublishingStates`

    .. attribute:: filler

      Pointer to :class:`PageFillers`


.. class:: PublishingStates

    A choicelist with the possible states of a publisher page.

    >>> rt.show(publisher.PublishingStates, language="en")
    ======= =========== ========= ============= ========
     value   name        text      Button text   public
    ------- ----------- --------- ------------- --------
     10      draft       Draft                   No
     20      ready       Ready                   No
     30      published   Public                  Yes
     40      removed     Removed                 No
    ======= =========== ========= ============= ========
    <BLANKLINE>

.. class:: PageFillers

    A choicelist with the page fillers that are available for this application.

    A page filler is a hard-coded method to produce dynamic web content.

    >>> rt.show(publisher.PageFillers, language="en")
    ========================= ====== ========================= =========================
     value                     name   text                      Data table
    ------------------------- ------ ------------------------- -------------------------
     blogs.LatestEntries              blogs.LatestEntries       blogs.LatestEntries
     comments.RecentComments          comments.RecentComments   comments.RecentComments
    ========================= ====== ========================= =========================
    <BLANKLINE>



.. class:: SpecialPages

    A choicelist with the special pages available on this site.

    >>> rt.show(publisher.SpecialPages, language="en")
    =========== ====================== ======================================
     name        text                   Pages
    ----------- ---------------------- --------------------------------------
     home        Home                   `en <…>`__ | `de <…>`__ | `fr <…>`__
     terms       Terms and conditions   `en <…>`__ | `de <…>`__ | `fr <…>`__
     privacy     Privacy policy         `en <…>`__ | `de <…>`__ | `fr <…>`__
     cookies     Cookie settings        `en <…>`__ | `de <…>`__ | `fr <…>`__
     copyright   Copyright              `en <…>`__ | `de <…>`__ | `fr <…>`__
     about       About us               `en <…>`__ | `de <…>`__ | `fr <…>`__
     blog        blog                   `en <…>`__ | `de <…>`__ | `fr <…>`__
    =========== ====================== ======================================
    <BLANKLINE>


Configuration
=============

.. setting:: publisher.locations

    A tuple of 2-tuples `(loc, cls)` where `loc` is a location string and `cls`
    a data table.

    >>> pprint(dd.plugins.publisher.locations)
    (('b', lino_xl.lib.blogs.models.LatestEntries),
     ('p', lino.modlib.publisher.ui.Pages),
     ('f', lino.modlib.uploads.ui.Uploads),
     ('s', lino_xl.lib.sources.models.Sources),
     ('t', lino_xl.lib.topics.models.Topics))

    When setting this setting (usually in a :meth:`get_plugin_configs` method),
    the application developer should specify the data tables using their names.
    The above locations have been set in :mod:`lino_cms.lib.cms.settings` as
    follows::

        yield ('publisher', 'locations', (
            ('b', 'blogs.LatestEntries'),
            ('p', 'publisher.Pages'),
            ('t', 'topics.Topics'),
            ('u', 'users.Users')))
