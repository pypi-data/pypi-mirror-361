.. doctest docs/projects/cosi4.rst
.. _book.projects.cosi4:

=========================================
``cosi4`` : a Lino Così for Uruguay
=========================================

.. module:: lino_book.projects.cosi4

A :term:`demo project` showing a :ref:`cosi` configured for usage in Uruguay.


>>> from lino import startup
>>> startup('lino_book.projects.cosi4.settings')
>>> from lino.api.doctest import *


Overview
========

The :mod:`lino_book.projects.cosi4` demo project is an example of a :ref:`cosi`
having

- :attr:`lino_xl.lib.contacts.Plugin.demo_region` set to ``UY``

  >>> dd.plugins.contacts.demo_region
  'UY'

- Spanish as second language

  >>> [i.django_code for i in settings.SITE.languages]
  ['en', 'es']

It also has :setting:`countries.full_data` set to True and because of this is
used by :doc:`/ref/demo_fixtures`.

The :mod:`lino.utils.demonames.ury` module  already localizes names of poeple,
but names of places and streets are not yet implemented.

>>> rt.show('contacts.Persons')
... #doctest: +ELLIPSIS +REPORT_UDIFF
======================= ========================================== =================== ============== ======== ==== ==========
 Name                    Address                                    e-mail address      Phone          Mobile   ID   Language
----------------------- ------------------------------------------ ------------------- -------------- -------- ---- ----------
 Mr Ademir Abreu         Akazienweg, 4700 Eupen, Belgium            andreas@arens.com   +32 87123456            13
 Mrs Agustina Acevedo    Alter Malmedyer Weg, 4700 Eupen, Belgium   annette@arens.com   +32 87123457            14
 Mr Aldemir Acosta       Aachener Straße, 4700 Eupen, Belgium                                                   15
 Mr Aldrin Acua          Am Bahndamm, 4700 Eupen, Belgium                                                       16
 Mr Ale Aguiar           Am Berg, 4700 Eupen, Belgium                                                           17
 Mrs Aliki Aguilar       Auf dem Spitzberg, 4700 Eupen, Belgium                                                 18
 Mrs Alondra Aguilera    Auenweg, 4700 Eupen, Belgium                                                           19
 Mr Alekos Aguirre       Am Waisenbüschchen, 4700 Eupen, Belgium                                                20
 Mr Alexander Albornoz   August-Thonnar-Str., 4700 Eupen, Belgium                                               21
 Mrs Andrea Alfaro       Auf'm Rain, 4700 Eupen, Belgium                                                        22
 Mrs Andressa Alfonso    Bahnhofstraße, 4700 Eupen, Belgium                                                     23
 Mrs Angelina Almada     Bahnhofsgasse, 4700 Eupen, Belgium                                                     24
 Mrs Anny Almeida        Bergkapellstraße, 4700 Eupen, Belgium                                                  25
 Mr Asaiah Alonso        Binsterweg, 4700 Eupen, Belgium                                                        26
 Mr Axel Alonzo          Bergstraße, 4700 Eupen, Belgium                                                        27
 Mr Azarel Altez         Bellmerin, 4700 Eupen, Belgium                                                         28
 Mr Babu Alvarez         Bennetsborn, 4700 Eupen, Belgium                                                       29
 Mr Bento Alves          Brabantstraße, 4700 Eupen, Belgium                                                     30
 Mrs Ayelen Alvez        Buchenweg, 4700 Eupen, Belgium                                                         31
 Mr Bruno Amaral         Edelstraße, 4700 Eupen, Belgium                                                        32
 Mrs Bettina Amaro       Favrunpark, 4700 Eupen, Belgium                                                        33
 Mr Clever Amorin        Euregiostraße, 4700 Eupen, Belgium                                                     34
 Mrs Camila Andrada      Feldstraße, 4700 Eupen, Belgium                                                        35
 Mr Darwin Andrade       Gewerbestraße, 4700 Eupen, Belgium                                                     36
 Mrs Cecilia Antunez     Fränzel, 4700 Eupen, Belgium                                                           37
 Mr Dereck Aparicio      Gospert, 4700 Eupen, Belgium                                                           38
 Mr Derian Aquino        Gülcherstraße, 4700 Eupen, Belgium                                                     39
 Mr Diaval Aranda        Haagenstraße, 4700 Eupen, Belgium                                                      40
 Mr Diego Araujo         Haasberg, 4700 Eupen, Belgium                                                          41
 Mr Dilan Arbelo         Haasstraße, 4700 Eupen, Belgium                                                        42
 Mrs Eimy Arevalo        Habsburgerweg, 4700 Eupen, Belgium                                                     43
 Mrs Eliana Arias        Heidberg, 4700 Eupen, Belgium                                                          44
 Mrs Eliane Artigas      Heidgasse, 4700 Eupen, Belgium                                                         45
 Mr Elwin Avila          Heidhöhe, 4700 Eupen, Belgium                                                          46
 Mrs Elizabeth Ayala     Herbesthaler Straße, 4700 Eupen, Belgium                                               47
 Mr Emmanuel Baez        Hochstraße, 4700 Eupen, Belgium                                                        48
 Mrs Emy Banchero        Hisselsgasse, 4700 Eupen, Belgium                                                      49
 Mr Enzo Barboza         4730 Raeren, Belgium                                                                   50
 Mr Erich Barcelo        4730 Raeren, Belgium                                                                   51
 Mrs Evelyn Barreiro     4730 Raeren, Belgium                                                                   52
 Mr Evan Barrera         4730 Raeren, Belgium                                                                   53
 Mrs Florencia Barreto   4730 Raeren, Belgium                                                                   54
 Mr Felipe Barrios       4730 Raeren, Belgium                                                                   55
 Mrs Geneviève Barros    4730 Raeren, Belgium                                                                   56
 Mr Franco Batista       4730 Raeren, Belgium                                                                   57
 Mr Frank Bello          4730 Raeren, Belgium                                                                   58
 Mr Freddy Beltran       4730 Raeren, Belgium                                                                   59
 Mr Gabriel Benitez      4730 Raeren, Belgium                                                                   60
 Mrs Grissel Bentancor   4730 Raeren, Belgium                                                                   61
 Mrs Heimy Bentancur     4730 Raeren, Belgium                                                                   62
 Mr Gaston Bentos        4730 Raeren, Belgium                                                                   63
 Mr Georgian Bermudez    4730 Raeren, Belgium                                                                   64
 Mr Geovanni Berrutti    4730 Raeren, Belgium                                                                   65
 Mr Gerardo Bianchi      4730 Raeren, Belgium                                                                   66
 Mrs Isabel Blanco       4730 Raeren, Belgium                                                                   67
 Mr Gregory Bonilla      4730 Raeren, Belgium                                                                   68
 Mrs Jessica Borba       4730 Raeren, Belgium                                                                   69
 Dr. Jimena Borges       4031 Angleur, Belgium                                                                  70
 Josefina Bravo          4031 Angleur, Belgium                                                                  71
 Mr Ignacio Britos       Amsterdam, Kingdom of the Netherlands                                                  72
 Mr Ihan Brum            Amsterdam, Kingdom of the Netherlands                                                  73
 Mrs Kamila Brun         Amsterdam, Kingdom of the Netherlands                                                  74
 Mr Illya Bruno          Aachen, Germany                                                                        75
 Mrs Kassandra Bueno     Aachen, Germany                                                                        76
 Mr Ismael Burgos        Aachen, Germany                                                                        77
 Mr Ithan Caballero      Aachen, Germany                                                                        78
 Mr Ivo Cabral           Paris, France                                                                          79
 Mr Jalen Cabrera        Paris, France                                                                          80
 Mr Javier Caceres       Paris, France                                                                          81
======================= ========================================== =================== ============== ======== ==== ==========
<BLANKLINE>
