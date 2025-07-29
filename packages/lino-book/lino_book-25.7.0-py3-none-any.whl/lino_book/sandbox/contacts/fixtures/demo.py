# -*- coding: UTF-8 -*-
# Copyright 2008-2013 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _

from lino.core.utils import resolve_model
from lino.utils.instantiator import Instantiator
from lino.api import dd
from lino.utils import dblogger
from lino.utils import Cycler

from lino.sandbox.contacts import models as contacts

# ~ print 20120225, 'settings.FIXTURE_DIRS is', settings.FIXTURE_DIRS

dblogger.info("Imported contacts demo fixture")

COUNT = 0

# ~ addresstype= Instantiator('contacts.AddressType',"name").build
role = Instantiator("contacts.Role", "name").build
# ~ person = Instantiator('contacts.Person',"first_name last_name").build
# ~ company = Instantiator('contacts.Company',"name").build
# ~ contact = Instantiator('contacts.Contact').build

Company = contacts.Company
Person = contacts.Person
User = contacts.User
City = resolve_model("countries.City")

if not settings.SITE.abstract_address:
    Address = contacts.Address
    address = Instantiator(Address, "country zip_code city:name street street_no").build


def company(name, country_id, zip_code, city, street, street_no):
    if settings.SITE.abstract_address:
        city = City.objects.get(name=city)
        yield Company(
            name=name,
            country_id=country_id,
            zip_code=zip_code,
            city=city,
            street=street,
            street_no=street_no,
        )
    else:
        addr = address(country_id, zip_code, city, street, street_no)
        yield addr
        com = Company(name=name, address=addr)
        yield com


def person(first_name, last_name, country_id=None, zip_code="", city=None, **kw):
    if settings.SITE.abstract_address:
        if city is not None:
            city = City.objects.get(name=city)
        yield Person(
            first_name=first_name,
            last_name=last_name,
            country_id=country_id,
            zip_code=zip_code,
            city=city,
        )
    else:
        addr = address(country_id, zip_code, city)
        yield addr
        yield Person(first_name=first_name, last_name=last_name, address=addr)


def contact(company, person, **kw):
    return contacts.Contact(person=person, company=company, **kw)


def objects():
    global COUNT
    COUNT += 1
    dblogger.info("Started contacts demo fixture %d", COUNT)

    # ~ yield addresstype(**dd.babel_values('name',en="Default",fr=u'Gérant',de=u"Geschäftsführer",et=u"Manager"))

    yield role(
        **dd.babel_values(
            "name", en="Manager", fr="Gérant", de="Geschäftsführer", et="Manager"
        )
    )
    yield role(
        **dd.babel_values(
            "name", en="Director", fr="Directeur", de="Direktor", et="Direktor"
        )
    )
    yield role(
        **dd.babel_values(
            "name", en="Secretary", fr="Sécrétaire", de="Sekretär", et="Sekretär"
        )
    )
    yield role(
        **dd.babel_values(
            "name",
            en="IT Manager",
            fr="Gérant informatique",
            de="EDV-Manager",
            et="IT manager",
        )
    )

    yield company("Rumma & Ko OÜ", "EE", "10115", "Tallinn", "Tartu mnt", "71")

    yield company(
        "Bäckerei Ausdemwald", "BE", "4700", "Eupen", "Vervierser Straße", "45"
    )
    yield company("Bäckerei Mießen", "BE", "4700", "Eupen", "Gospert", "103")
    yield company("Bäckerei Schmitz", "BE", "4700", "Eupen", "Aachener Straße", "53")
    yield company("Garage Mergelsberg", "BE", "4720", "Kelmis", "Kasinostraße", "13")

    yield company("Donderweer BV", "NL", "4816 AR", "Breda", "Edisonstraat", "12")
    yield company("Van Achter NV", "NL", "4836 LG", "Breda", "Hazeldonk", "2")

    yield company("Hans Flott & Co", "DE", "22453", "Hamburg", "Niendorfer Weg", "532")
    yield company(
        "Bernd Brechts Bücherladen", "DE", "80333", "München", "Brienner Straße", "18"
    )
    yield company(
        "Reinhards Baumschule", "DE", "12487 ", "Berlin", "Segelfliegerdamm", "123"
    )

    yield company("Moulin Rouge", "FR", "75018", "Paris", "Boulevard de Clichy", "82")
    yield company(
        "Auto École Verte", "FR", "54000 ", "Nancy", "rue de Mon Désert", "12"
    )

    # ~ yield person(u'Luc',  u'Saffre', gender=Gender.male)
    yield person("Andreas", "Arens", "BE", "4700", "Eupen", gender=dd.Genders.male)
    yield person("Annette", "Arens", "BE", "4700", "Eupen", gender=dd.Genders.female)
    yield person("Hans", "Altenberg", "BE", "4700", "Eupen", gender=dd.Genders.male)
    yield person("Alfons", "Ausdemwald", "BE", "4700", "Eupen", gender=dd.Genders.male)
    yield person(
        "Laurent", "Bastiaensen", "BE", "4700", "Eupen", gender=dd.Genders.male
    )
    yield person(
        "Charlotte", "Collard", "BE", "4700", "Eupen", gender=dd.Genders.female
    )
    yield person("Ulrike", "Charlier", "BE", "4700", "Eupen", gender=dd.Genders.female)
    yield person("Marc", "Chantraine", "BE", "4700", "Eupen", gender=dd.Genders.male)
    yield person("Daniel", "Dericum", "BE", "4700", "Eupen", gender=dd.Genders.male)
    yield person(
        "Dorothée", "Demeulenaere", "BE", "4700", "Eupen", gender=dd.Genders.female
    )
    yield person("Berta", "Ernst", "BE", "4700", "Eupen", gender=dd.Genders.female)
    yield person("Bernd", "Evertz", "BE", "4700", "Eupen", gender=dd.Genders.male)
    yield person("Eberhart", "Evers", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Daniel", "Emonts", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Edgar", "Engels", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Luc", "Faymonville", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Gérard", "Gernegroß", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Werner", "Groteclaes", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Grete", "Hilgers", "BE", "4700", "Eupen", gender=Gender.female)
    yield person("Hans", "Hilgers", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Irene", "Ingels", "BE", "4700", "Eupen", gender=Gender.female)
    yield person("Jérémy", "Jansen", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Jean-Pierre", "Jacob", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Herbert", "Johnen", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Johannes", "Jonas", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Jan", "Jousten", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Karl", "Kaivers", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Guido", "Lambertz", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Luc", "Laschet", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Line", "Lazarus", "BE", "4700", "Eupen", gender=Gender.female)
    yield person("Josefine", "Leffin", "BE", "4700", "Eupen", gender=Gender.female)
    yield person("Marc", "Malmendier", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Leo", "Meessen", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Franz", "Mießen", "BE", "4700", "Eupen", gender=Gender.male)
    yield person("Marie-Louise", "Meier", "BE", "4700", "Eupen", gender=Gender.female)

    yield person("Erich", "Emonts", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Erwin", "Emontspool", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Erna", "Emonts-Gast", "BE", "4730", "Raeren", gender=Gender.female)
    yield person("Alfons", "Radermacher", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Berta", "Radermacher", "BE", "4730", "Raeren", gender=Gender.female)
    yield person("Christian", "Radermacher", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Daniela", "Radermacher", "BE", "4730", "Raeren", gender=Gender.female)
    yield person("Edgard", "Radermacher", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Fritz", "Radermacher", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Guido", "Radermacher", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Hans", "Radermacher", "BE", "4730", "Raeren", gender=Gender.male)
    yield person("Hedi", "Radermacher", "BE", "4730", "Raeren", gender=Gender.female)
    yield person("Inge", "Radermacher", "BE", "4730", "Raeren", gender=Gender.female)
    yield person("Jean", "Radermacher", "BE", "4730", "Raeren", gender=Gender.male)

    # special challenges for alphabetic ordering
    yield person("Elio", "di Rupo")
    yield person("Leonardo", "da Vinci")
    yield person("Herman", "van Veen")
    yield person("Rein", "Õunapuu")
    yield person("Otto", "Östges")
    yield person("Erna", "Ärgerlich")

    yield person("Bernard", "Bodard", title="Dr.")
    yield person("Jean", "Dupont")

    yield person("Mark", "Martelaer")
    yield person("Rik", "Radermecker")
    yield person("Marie-Louise", "Vandenmeulenbos")

    yield person("Emil", "Eierschal")
    yield person("Lisa", "Lahm")
    yield person("Bernd", "Brecht")
    yield person("Karl", "Keller")

    yield person("Robin", "Dubois")
    yield person("Denis", "Denon")
    yield person("Jérôme", "Jeanémart")

    s = """\
Aachener Straße
Akazienweg
Alter Malmedyer Weg
Am Bahndamm
Am Berg
Am Waisenbüschchen
Auenweg
Auf dem Spitzberg
Auf'm Rain
August-Thonnar-Str.
Bahnhofsgasse
Bahnhofstraße
Bellmerin
Bennetsborn
Bergkapellstraße
Bergstraße
Binsterweg
Brabantstraße
Buchenweg
Edelstraße
Euregiostraße
Favrunpark
Feldstraße
Fränzel
Gewerbestraße
Gospert
Gülcherstraße
Haagenstraße
Haasberg
Haasstraße
Habsburgerweg
Heidberg
Heidgasse
Heidhöhe
Herbesthaler Straße
Hisselsgasse
Hochstraße
Hook
Hostert
Hufengasse
Hugo-Zimmermann-Str.
Hütte
Hütterprivatweg
Im Peschgen
In den Siepen
Industriestraße
Johannesstraße
Judenstraße
Kaperberg
Kaplan-Arnolds-Str.
Karl-Weiß-Str.
Kehrweg
Kirchgasse
Kirchstraße
Klinkeshöfchen
Kügelgasse
Langesthal
Lascheterweg
Limburgerweg
Lindenweg
Lothringerweg
Malmedyer Straße
Maria-Theresia-Straße
Marktplatz
Monschauer Straße
Mühlenweg
Neustraße
Nikolausfeld
Nispert
Noereth
Obere Ibern
Obere Rottergasse
Oestraße
Olengraben
Panorama
Paveestraße
Peter-Becker-Str.
Rosenweg
Rot-Kreuz-Str.
Rotenberg
Rotenbergplatz
Schilsweg
Schlüsselhof
Schnellewindgasse
Schönefeld
Schorberg
Schulstraße
Selterschlag
Simarstraße
Steinroth
Stendrich
Stockbergerweg
Stockem
Theodor-Mooren-Str.
Untere Ibern
Vervierser Straße
Vossengasse
Voulfeld
Werthplatz
Weserstraße
"""

    streets_of_eupen = [
        line.strip() for line in s.splitlines() if len(line.strip()) > 0
    ]

    if settings.SITE.abstract_address:
        nr = 1
        # ~ CITIES = Cycler(City.objects.all())
        eupen = City.objects.get(name="Eupen")
        STREETS = Cycler(streets_of_eupen)
        for p in Person.objects.filter(city=eupen):
            p.street = STREETS.pop()
            p.street_no = str(nr)
            p.save()
            nr += 1
    else:
        nr = 1
        for street in streets_of_eupen:
            for i in range(3):
                yield address("BE", "4700", "Eupen", street, str(nr))
                nr += 1

        ADDRESSES = Cycler(Address.objects.all())
        for p in Person.objects.all():
            p.address = ADDRESSES.pop()
            p.save()

    PERSONS = Cycler(contacts.Person.objects.all())
    COMPANIES = Cycler(contacts.Company.objects.all())
    ROLES = Cycler(contacts.Role.objects.all())
    for i in range(100):
        com = COMPANIES.pop()
        yield contact(com, PERSONS.pop(), role=ROLES.pop())
        yield contact(com, PERSONS.pop(), role=ROLES.pop())

    rumma = contacts.Company.objects.get(name="Rumma & Ko OÜ")

    def user(first_name, last_name, **kw):
        p = Person(first_name=first_name, last_name=last_name)
        p.save()
        return User(person=p, company=rumma, **kw)

    # ~ yield user("Alice","Imedemaal",is_superuser=True)
    yield user("Alice", "Imedemaal", user_type=UserTypes.admin)
    yield user("Bert", "Sesamestreet")
    yield user("Charles", "Braun")
    dblogger.info("Done contacts demo fixture")
