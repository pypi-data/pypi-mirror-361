.. doctest docs/plugins/cars.rst
.. _dg.plugins.cars:

================================
``cars`` : Managing cars
================================

.. module:: lino_xl.lib.cars

This is the developer reference about the :mod:`lino_xl.lib.cars` plugin, which
adds functionality for managing cars and similar vehicles.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi2.startup import *
>>> ses = rt.login('robin')

The `cars` plugin is being used by the
:mod:`lino_book.projects.cosi2`
demo project.
The :class:`Car` model is declared as
:data:`lino_xl.lib.trading.project_model`.

.. class:: Car

  Django model used to represent a car.

.. class:: Brand

  Django model used to represent a brand.


Configuration options
=====================

You can activate this plugin by overriding your Site's
:meth:`lino.core.site.Site.get_installed_plugins` method like this::

    def get_installed_plugins(self):
        yield super().get_installed_plugins()
        yield 'lino_xl.lib.cars'


Usage
=====

As a :term:`site manager` you can see all cars by selecting
:menuselection:`Cars --> Cars`.
:menuselection:`Cars --> Brands`.

>>> show_menu_path(cars.Cars)
Cars --> Cars
>>> show_menu_path(cars.Brands)
Cars --> Car brands

>>> rt.show(cars.Brands)
=============== ===========
 Désignation     Reference
--------------- -----------
 Alfa Romeo
 Audi
 BMW
 Chevrolet
 Chrysler
 Citroen
 Dacia
 Daewoo
 Daihatsu
 Dodge
 Fiat
 Ford
 Honda
 Hyundai
 Isuzu
 Iveco
 Jaguar
 Jeep
 Kia
 Lada
 Lancia
 Land Rover
 Linhai
 MG
 Mazda
 Mercedes-Benz
 Mini
 Mitsubishi
 Nissan
 Opel
 Peugeot
 Plymouth
 Pontiac
 Porsche
 Renault
 Rover
 Saab
 Seat
 Skoda
 Smart
 Ssangyong
 Subaru
 Suzuki
 Toyota
 VW
 Volvo
=============== ===========
<BLANKLINE>



>>> rt.show(cars.Cars)
===================== =============== ============ ======== ============
 Partenaire            License plate   Car brand    Modèle   Vehicle ID
--------------------- --------------- ------------ -------- ------------
 Bestbank              ABC123          Alfa Romeo
 Rumma & Ko OÜ         ABC456          Audi
 Bäckerei Ausdemwald   DEF123          BMW
 Bäckerei Mießen       DEF789          Chevrolet
 Bäckerei Schmitz      GHI123          Chrysler
 Garage Mergelsberg    GHI789          Citroen
===================== =============== ============ ======== ============
<BLANKLINE>

>>> rt.show(cars.CarsByBrand, cars.Brand.objects.get(name="Audi"))
======== =============== =============== ============
 Modèle   Partenaire      License plate   Vehicle ID
-------- --------------- --------------- ------------
          Rumma & Ko OÜ   ABC456
======== =============== =============== ============
<BLANKLINE>

>>> obj = contacts.Company.objects.get(name="Bestbank")
>>> rt.show(cars.CarsByPartner, obj)
=============== ============ ======== ============
 License plate   Car brand    Modèle   Vehicle ID
--------------- ------------ -------- ------------
 ABC123          Alfa Romeo
=============== ============ ======== ============
<BLANKLINE>
