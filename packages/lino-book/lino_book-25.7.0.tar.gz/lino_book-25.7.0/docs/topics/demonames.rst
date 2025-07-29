.. doctest docs/topics/utils.rst

==========
Demo names
==========

Most Lino applications include some form of contacts management and store names
and postal addresses of :term:`business partners <business partner>`.

Lino was born in Eastern Belgium and during its first years all potential new
customers lived in that region. Until now the :fixture:`demo` fixture of the
:mod:`lino_xl.lib.contacts` plugin creates persons and organizations in Eupen,
Raeren, La Calamine, ... and who have names that sound "normal" for people of
that region. Look at the `source code
<https://gitlab.com/lino-framework/xl/-/blob/master/lino_xl/lib/contacts/fixtures/demo.py?ref_type=heads>`__
if you don't believe me.

But meanwhile Lino has grown international. When a :term:`hosting provider` in
Tallinn wants to show Lino to a potential customer, it's a bit silly to start
their demo with such contact data.

The :mod:`commondata.demonames` module is for generating fictive names of
people living in different places of the world.

.. contents::
   :depth: 1
   :local:


>>> from lino import startup
>>> startup('lino.projects.std.settings_test')
>>> from pprint import pprint
>>> from lino.utils import Cycler

Names of fictive persons
========================

Belgian last names:

>>> from commondata.demonames import bel, est, ury, russian, muslim

>>> pprint(bel.LAST_NAMES[:5])
['Adam', 'Adami', 'Adriaen', 'Adriaensen', 'Adriaenssen']
>>> pprint(bel.LAST_NAMES[-5:])
['Yilmaz', 'Zadelaar', 'Zegers', 'Zeggers', 'Zègres']

Next comes a group of five Russians:

>>> pprint(russian.LAST_NAMES[:5])
['Abezgauz', 'Aleksandrov', 'Altukhov', 'Alvang', 'Ankundinov']


Or here is a mixture of nationalities, for each Belgian comes one foreigner:

>>> LAST_NAMES = Cycler(
...     Cycler(bel.LAST_NAMES),
...     Cycler(russian.LAST_NAMES),
...     Cycler(bel.LAST_NAMES),
...     Cycler(muslim.LAST_NAMES))

>>> for i in range(10):
...     print(LAST_NAMES.pop())
Adam
Abezgauz
Adam
Abad
Adami
Aleksandrov
Adami
Abbas
Adriaen
Altukhov


Five fictive Estonian couples, each couple consisting of one male and one
female:

>>> MALE_FIRST_NAMES = Cycler(est.MALE_FIRST_NAMES)
>>> FEMALE_FIRST_NAMES = Cycler(est.FEMALE_FIRST_NAMES)
>>> LAST_NAMES = Cycler(est.LAST_NAMES)
>>> for i in range(5):
...    he = (MALE_FIRST_NAMES.pop(), LAST_NAMES.pop())
...    she = (FEMALE_FIRST_NAMES.pop(), LAST_NAMES.pop())
...    print("%s %s & %s %s" % (he + she))
Aadu Aas & Adeele Aasa
Aare Aasmäe & Age Aavik
Aarne Abel & Age-Kaie Abramov
Aaro Adamson & Aili Ader
Aaron Afanasjev & Aino Alas


Uruguayan demo names:

>>> pprint(ury.LAST_NAMES[:5])
['Abreu', 'Acevedo', 'Acosta', 'Acua', 'Aguiar']
>>> pprint(ury.LAST_NAMES[-5:])
['Villanueva', 'Villar', 'Zapata', 'Zeballos', 'Zunino']
>>> pprint(ury.MALE_FIRST_NAMES[:5])
['Ademir', 'Alberico', 'Aldemir', 'Aldrin', 'Ale']
>>> pprint(ury.MALE_FIRST_NAMES[-5:])
['Vitali', 'Washington', 'Wilmar', 'Wolfram', 'Ziadh']
>>> pprint(ury.FEMALE_FIRST_NAMES[:5])
['Addis', 'Agustina', 'Alai', 'Alexandra', 'Alice']
>>> pprint(ury.FEMALE_FIRST_NAMES[-5:])
['Yan', 'Yanara', 'Yomira', 'Yoselin', 'Yuliana']



Street names
============

Names of some streets:

>>> from commondata.demonames.streets import STREETS_IN_EUPEN, STREETS_IN_LIEGE, STREETS_IN_TALLINN

>>> for s in STREETS_IN_EUPEN[:5]:
...     print(s)
Aachener Straße
Akazienweg
Alter Malmedyer Weg
Am Bahndamm
Am Berg

>>> for s in STREETS_IN_LIEGE[:5]:
...     print(s)
Au Péri
Avenue Albert Mahiels
Avenue Blonden
Avenue Charles Rogier
Avenue Maurice Destenay


>>> streets = Cycler(STREETS_IN_TALLINN)
>>> print(len(streets))
1523
>>> for street, suburb in STREETS_IN_TALLINN[:10]:
...     print(f"{street} ({suburb})")
1. liin (Põhja-Tallinn)
2. liin (Põhja-Tallinn)
3. liin (Põhja-Tallinn)
4. liin (Põhja-Tallinn)
5. liin (Põhja-Tallinn)
20. Augusti väljak (Kesklinn)
A. H. Tammsaare tee (Mustamäe)
Aarde tn (Põhja-Tallinn)
Aasa tn (Kesklinn)
Aate tn (Nõmme)


Sources
=======

The raw data was originally copied from:

- Belgian last names from http://www.lavoute.org/debuter/Belgique.htm
- French last names from http://www.nom-famille.com/noms-les-plus-portes-en-france.html
- Russian last names from http://www.meetmylastname.com/prd/articles/24
- French first names from
  http://meilleursprenoms.com/site/LesClassiques/LesClassiques.htm
- African, Muslim and Russian names from
  http://www.babynames.org.uk
  and http://genealogy.familyeducation.com

- Estonian last names were originally extracted from
  `www.ekspress.ee <https://ekspress.delfi.ee/artikkel/27677149/top-500-eesti-koige-levinumad-perekonnanimed>`__
  (Luc manually added some less frequent names).

- Estonian first names were originally extracted from Luc's personal database.
