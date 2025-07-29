.. doctest docs/plugins/peppol/scenarios.rst
.. _dg.plugins.peppol.scenarios:


===============
Usage scenarios
===============

The tested docs for the :mod:`lino_xl.lib.peppol`  plugin use three demo projects:
:mod:`lino_book.projects.noi1e` shows the first scenario, while
:mod:`lino_book.projects.cosi1` and :mod:`lino_book.projects.cosi2` show the
second scenario.

More precisely:

>>> from lino_book.projects.noi1r.startup import *
>>> from lino_book.projects.cosi1.settings import SITE as C1
>>> from lino_book.projects.cosi2.settings import SITE as C2
>>> rows = []
>>> headers = ['title', 'host', 'my supplier_id', 'VAT id']
>>> def site2cells(site):
...     return (
...         site.title,
...         "Yes" if site.plugins.peppol.with_suppliers else "No",
...         site.plugins.peppol.supplier_id,
...         site.plugins.contacts.site_owner_lookup.get('vat_id', settings.SITE.plugins.contacts.site_owner.vat_id))
>>> for site in settings.SITE, C1, C2:
...     rows.append(site2cells(site))
>>> print(rstgen.table(headers, rows))
======= ====== ====================================== =================
 title   host   my supplier_id                         VAT id
------- ------ -------------------------------------- -----------------
 noi1r   Yes    None                                   EE 100.588.749
 cosi1   No     257e1470-b192-4eff-ae30-b83a295a907e   BE 0123.456.749
 cosi2   No     5d314e69-e462-4a4d-8694-c34ca7805e0b   BE 0234.567.873
======= ====== ====================================== =================
<BLANKLINE>

The supplier IDs in above code snippet will change if you use another
integration environment than the one we use. The credentials for our integration
environment at Ibanity are currently not published, i.e. if you want to run
these tests yourself, you must either `join our team
<https://www.synodalsoft.net/jobs>`__ or use your own integration environment
from :term:`Ibanity`.

A Lino site having :data:`with_suppliers` activated generates a :xfile:`data.py`
file, which contains a list :data:`suppliers`.

.. xfile:: data.py

  A file that contains some of the data of a :term:`Lino site` as a Python
  module so that it can be imported by scripts on the system.

  It is currently is always located in the :attr:`site_dir
  <lino.core.site.Site.site_dir>` and it gets generated only once after :cmd:`pm
  prep`, but that rule might change if needed.


>>> from lino_book.projects.noi1e.settings.data import suppliers
>>> pprint(suppliers, width=90)
[Supplier(vat_id='BE 0123.456.749', names='Number One', supplier_id='257e1470-b192-4eff-ae30-b83a295a907e'),
 Supplier(vat_id='BE 0234.567.873', names='Number Two', supplier_id='5d314e69-e462-4a4d-8694-c34ca7805e0b'),
 Supplier(vat_id='BE 0322.862.421', names='Bäckerei Mießen', supplier_id='bcce2b6f-d636-4390-9d47-4c02969db218'),
 Supplier(vat_id='BE 0345.678.997', names='Number Three', supplier_id='c1b8263e-88ef-4df0-ae37-1ca46ee7ec81'),
 Supplier(vat_id='BE 0404.484.654', names='Ethias s.a.', supplier_id=None),
 Supplier(vat_id='BE 0419.897.855', names='Niederau Eupen AG', supplier_id='76e631c1-05c7-4229-a038-6ca99d8a91f0'),
 Supplier(vat_id='BE 0506.780.656', names='Garage Mergelsberg', supplier_id='0aaf855b-49dd-4b65-947f-27a80f13d2d0'),
 Supplier(vat_id='BE 0561.962.669', names='Bäckerei Ausdemwald', supplier_id='997dc48c-b953-4588-81c0-761871e37e42'),
 Supplier(vat_id='BE 0650.238.114', names='Leffin Electronics', supplier_id='4c78ea55-ee5f-4e98-8675-88fa099a7789'),
 Supplier(vat_id='BE 0966.980.726', names='Bäckerei Schmitz', supplier_id='88fc5add-98cf-4bf1-9f7c-3214c94549b3')]

The :data:`suppliers` list is sorted by :attr:`vat_id`.

The :xfile:`data.py` file of :mod:`lino_book.projects.noi1e` is imported by
:mod:`lino_book.projects.cosi1` and  :mod:`lino_book.projects.cosi2`  to set
their :data:`lino_xl.lib.peppol.supplier_id` and
:data:`lino_xl.lib.contacts.site_owner_lookup`.


..
  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
