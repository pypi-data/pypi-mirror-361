.. doctest docs/specs/beid.rst
.. _specs.lib.beid:

==================================
``beid`` : Belgian ID card holders
==================================

.. currentmodule:: lino_xl.lib.beid

The :mod:`lino_xl.lib.beid` plugin adds functionality for reading Belgian eID
cards and storing that data in the database. It also adds an action to open the
:term:`detail window` of the card holder after reading a card.

.. contents::
   :depth: 1
   :local:

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.avanti1.startup import *

See also unit tests in :mod:`lino_welfare.tests.test_beid`.


Introduction
============

This plugin makes sense only if there is exactly one subclass of the
:class:`BeIdCardHolder` model mixin among your application's models.  That model
is referrable as :data:`holder_model`.

>>> dd.plugins.beid.holder_model
<class 'lino_avanti.lib.avanti.models.Client'>


See unit tests in :mod:`lino_welfare.tests.test_beid`.

.. class:: SSIN

    A mixin that adds two fields :attr:`national_id` and :attr:`nationality`.

    You can use this mixin also when the plugin is not installed.

    Class attributes:

    .. attribute:: validate_national_id = False

        Whether to validate the :attr:`national_id` immediately before saving a
        record.  If this is `False`, the :attr:`national_id` might contain
        invalid values which would later be reported as :term:`data problem
        messages <data problem message>`.

    .. attribute:: national_id

        The SSIN. It is a *nullable char field* declared *unique*. It
        is not validated directly because that would cause problems
        with legacy data where SSINs need manual control. See also
        :class:`BeIdCardHolderChecker`.

    Database fields:

    .. attribute:: nationality

        The nationality. This is a pointer to
        :class:`countries.Country
        <lino_xl.lib.statbel.countries.models.Country>` which should
        contain also entries for refugee statuses.

        Note that the nationality is *not* being read from eID card
        because it is stored there as a language and gender specific
        plain text.


.. class:: BeIdCardHolder

    Mixin for models which represent an eid card holder.
    Currently only Belgian eid cards are tested.
    Concrete subclasses must also inherit from :mod:`lino.mixins.Born`.

    Database fields:

    .. attribute:: birth_country

    .. attribute:: nationality_text

      The nationality in plain text as it was on the eid card. For a French
      citizen the value on the eid card can be "Français", "Française", "Frans",
      "Franzose", "Französin", "French" depending on the sex and the issuing
      municipality.  This field is just informative, Lino does not automatically
      map it to the :attr:`nationality` field.

    .. attribute:: birth_place

      The birth place in plain text as it was on the eid card.

    .. attribute:: card_number
    .. attribute:: card_valid_from
    .. attribute:: card_valid_until

    .. attribute:: card_type

        The type of id card.

        Choices are defined in :class:`BeIdCardTypes`

    .. attribute:: card_issuer

        The administration who issued this ID card.

    .. attribute:: noble_condition

        The eventual noble condition of this person.

    .. method:: read_beid

        Update card holder data from eID card

        Read eId card and store the data on the selected holder.

        This is a row action (called on a given holder).

        When the selected holder has an empty `national_id`, and when
        there is no holder yet with that `national_id` in the database,
        then we want to update the existing holder from the card.


    .. method:: find_by_beid

        Find or create card holder from eID card

        Read an eID card, then either show the existing holder or ask to
        create a new holder.

        This is a list action, usually called from a quicklink or a main
        menu item.


    .. attribute:: image

        Virtual field which displays the picture.



ID card types
=============

>>> show_choicelist(beid.BeIdCardTypes)
======= ================== ======================================== ==================================================================================== ==============================================
 value   name               en                                       de                                                                                   fr
------- ------------------ ---------------------------------------- ------------------------------------------------------------------------------------ ----------------------------------------------
 01      belgian_citizen    Belgian citizen                          Belgischer Staatsbürger                                                              Citoyen belge
 06      kids_card          Kids card (< 12 year)                    Kind unter 12 Jahren                                                                 Kids card (< 12 year)
 11      foreigner_a        Foreigner card A                         A (Bescheinigung der Eintragung im Ausländerregister - Vorübergehender Aufenthalt)   Étranger A (Séjour temporaire)
 12      foreigner_b        Foreigner card B                         B (Bescheinigung der Eintragung im Ausländerregister)                                Foreigner card B
 13      foreigner_c        Foreigner card C                         C (Personalausweis für Ausländer)                                                    Foreigner card C
 14      foreigner_d        Foreigner card D                         D (Daueraufenthalt - EG)                                                             Foreigner card D
 15      foreigner_e        Foreigner card E                         E (Anmeldebescheinigung)                                                             Foreigner card E
 16      foreigner_e_plus   Foreigner card E+                        E+                                                                                   Foreigner card E+
 17      foreigner_f        Foreigner card F                         F (Aufenthaltskarte für Familienangehörige eines Unionsbürgers)                      Foreigner card F
 18      foreigner_f_plus   Foreigner card F+                        F+                                                                                   Foreigner card F+
 99      orange_card        Registration certificate (Orange card)   Eintragungsbescheinigung (Orange Karte)                                              Attestation d’immatriculation (Carte orange)
======= ================== ======================================== ==================================================================================== ==============================================
<BLANKLINE>


.. class:: BeIdCardTypes

    A list of Belgian identity card types.

    We didn't yet find any official reference document.

    The eID applet returns a field `documentType` which contains a
    numeric code.  For example 1 is for "Belgian citizen", 6 for "Kids
    card",...

    The eID viewer, when saving a card as xml file, doesn't save these
    values nowhere, it saves a string equivalent (1 becomes
    "belgian_citizen", 6 becomes "kids_card", 17 becomes
    "foreigner_f", 16 becomes "foreigner_e_plus",...

    Sources:

    - [1] `kuleuven.be <https://securehomes.esat.kuleuven.be/~decockd/wiki/bin/view.cgi/EidForums/ForumEidCards0073>`__
    - [2] The `be.fedict.commons.eid.consumer.DocumentType <http://code.google.com/p/eid-applet/source/browse/trunk/eid-applet-service/src/main/java/be/fedict/eid/applet/service/DocumentType.java>`__ enum.

    - http://www.adde.be/joomdoc/guides/les-titres-de-sejours-en-belgique-guide-pratique-dec12-g-aussems-pdf/download


    Excerpts from [1]:

    - Johan: A document type of 7 is used for bootstrap cards -- What
      is a bootstrap card (maybe some kind of test card?)  Danny: A
      bootstrap card was an eID card that was used in the early start
      of the eID card introduction to bootstrap the computers at the
      administration. This type is no longer issued.

    - Johan: A document type of 8 is used for a
      "habilitation/machtigings" card -- Is this for refugees or
      asylum seekers? Danny: A habilitation/machtigings card was aimed
      at civil servants. This type is also no longer used.


Residence types
===============

>>> rt.show(beid.ResidenceTypes)
======= ====== ========================
 value   name   text
------- ------ ------------------------
 1              Register of citizens
 2              Register of foreigners
 3              Waiting register
======= ====== ========================
<BLANKLINE>


.. class:: ResidenceTypes

    The list of Belgian resident registers
    (Einwohnerregister, Registre de résidents).

    https://en.wikipedia.org/wiki/Resident_registration

    ======================= =========================== =======================
    de                      fr                          nl
    ======================= =========================== =======================
    Bevölkerungsregister    Registre de la population   Bevolkingsregister
    Fremdenregister         Registre des étrangers      Vreemdelingenregister
    Warteregister           Registre d'attente
    ======================= =========================== =======================





.. class:: BeIdCardHolderChecker

    Invalid NISSes are not refused à priori using a ValidationError
    (see :attr:`BeIdCardHolder.national_id`), but this checker reports
    them.

    Belgian NISSes are stored including the formatting characters (see
    :mod:`lino.utils.ssin`) in order to guarantee uniqueness.


Plugin settings
===============


.. data:: holder_model

  The one and only model on this site that implements :class:`BeIdCardHolder`.

  This is available only after site startup.

.. data:: data_collector_dir

  When this is a non-empty string containing a directory name on the
  server, then Lino writes the raw data of every eid card into a
  text file in this directory.

.. data:: read_only_simulate

  Whether to just simulate. Used for testing.

.. data:: eidreader_timeout

  How many seconds to wait for a response from the card reader.

  Default value is 15.

.. data:: data_cache_dir

  Where to store cache data.

  Defaults to ``settings.SITE.site_dir / 'media' / 'cache' / 'beid'``.

.. data:: simulate_eidreader_path = None

  Path for eidreader simulation data.

  If given, this should be the name of a directory containing files with
  eidreader data to be used for simulation.


.. data:: urlhandler_prefix

  The prefix to be passed by the :func:`beid_card_processor` Javascript function
  to the URL protocol handler responsible for running eidreader.

  Default value is ``'beid://'`` which should work in a standard usage.

  You can tell Lino to use another URL protocol than ``beid`` by
  saying::

     SITE.plugins.beid.urlhandler_prefix = 'mybeid://'

  You can disable eidreader functionality by saying::

     SITE.plugins.beid.urlhandler_prefix = None

.. data:: preprocessor_delay = 0

  Time (in milliseconds) Lino should wait between opening the eidreader URL and
  sending the actions' AJAX request.

  For example on an nginx server with only one worker process, you can set
  this to make sure that the client machine has read the card data and sent it
  to the server *before* you ask the server to process that data::

      preprocessor_delay = 3000



Tests
=====

The :attr:`national_id <lino_xl.lib.beid.BeIdCardHolder.national_id>`
field of a client. It nullable and unique: it can be empty, but must
be unique when it isn't.

>>> fld = rt.models.avanti.Client._meta.get_field('national_id')
>>> print(fld.help_text)  #doctest: +NORMALIZE_WHITESPACE
The SSIN. It is a nullable char field declared unique. It is not validated
directly because that would cause problems with legacy data where SSINs need
manual control. See also BeIdCardHolderChecker.

>>> print(fld.null)
True
>>> print(fld.unique)
True



>>> from lino_xl.lib.beid.views import read_card_data_from_file
>>> from pathlib import Path
>>> from lino_book import DEMO_DATA
>>> fn = DEMO_DATA / "beid/20190311.json"
>>> data = read_card_data_from_file(fn)
>>> print(data.success)
True
>>> print(data.issuing_municipality)
Charleroi
>>> print(data.address_municipality)
Châtelet

>>> rt.models.countries.Place.objects.filter(name="Châtelet").exists()
False

>>> img_file = Path(rt.models.avanti.Client.card_number_to_image_path(data.card_number))  #doctest: +ELLIPSIS
>>> str(img_file).endswith("/beid/592400976752.jpg")
True
>>> img_dir = Path(settings.MEDIA_ROOT) / 'beid'
>>> str(img_file).startswith(str(img_dir))
True

>>> settings.SITE.makedirs_if_missing(img_dir)
>>> kwargs = rt.models.avanti.Client.find_by_beid.card2client(data)
>>> img_file.unlink()
>>> # img_dir.rmdir()
>>> rt.models.countries.Place.objects.filter(name="Châtelet").exists()
True
>>> rt.models.countries.Place.objects.filter(name="Châtelet").delete()
(1, {'countries.Place': 1})


>>> fn = DEMO_DATA / "beid/nocard.json"
>>> data = read_card_data_from_file(fn)
Traceback (most recent call last):
...
Warning: No card data found: Could not find any reader with a card inserted

>>> # skip because under Python 2 it is another exception
>>> data = read_card_data_from_file("foo")  #doctest: -SKIP
Traceback (most recent call last):
...
FileNotFoundError: [Errno 2] No such file or directory: 'foo'


.. class:: SSINChecker

  A :term:`data checker` that reports invalid SSINs.

  See :doc:`/specs/ssin`.


>>> dbhash.check_virgin()
