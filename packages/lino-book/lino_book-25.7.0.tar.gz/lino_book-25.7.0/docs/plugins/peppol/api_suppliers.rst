.. doctest docs/plugins/peppol/api_suppliers.rst
.. _dg.plugins.peppol.api.suppliers:

================================
Ibanity API (part 1) : suppliers
================================

This section explores the supplier management subset of the :term:`Ibanity API`,
which is used internally by the :mod:`lino_xl.lib.peppol` plugin. As a Lino
:term:`application developer` you won't need to know these details if you just
use the plugin.

.. contents::
  :local:


About this document
===================

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.noi1r.startup import *

>>> pytest.skip("Code snippets in this document currently aren't tested")


The code snippets in this document are tested only if you have :term:`Ibanity
credentials` installed:

>>> if not dd.plugins.peppol.credentials:
...     pytest.skip('this doctest requires Ibanity credentials')

>>> from lino_xl.lib.peppol.utils import supplier_attrs, res2str, EndpointID

Tidying up from previous runs is more complicated for this doctest because it
communicates with the Ibanity environment.

>>> ar = rt.login("robin")
>>> ses = dd.plugins.peppol.get_ibanity_session(ar)

>>> def tidy_up_ibanity():
...     eid = EndpointID("BE0404484654")
...     if (data := ses.find_supplier_by_eid(eid)) is not None:
...         ses.delete_supplier(data['id'])
>>> tidy_up_ibanity()


Access token
============

The :setting:`peppol.credentials` setting is the identifier of your
application in the :term:`Ibanity developer portal`.

This is a string of the form "{client_id}:{client_secret}".

>>> dd.plugins.peppol.credentials  #doctest: +ELLIPSIS
'6b6720e4-bed2-4272-ab77-f534bab6dcc7:AJib13J5MiVBHjGLSImHd1dDlyJvtGPE'

>>> dd.plugins.peppol.cert_file  #doctest: +ELLIPSIS
PosixPath('.../secrets/certificate.pem')
>>> print(dd.plugins.peppol.cert_file.read_text().strip())  #doctest: +ELLIPSIS
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----

>>> pprint(ses.get_access_token())  #doctest: +ELLIPSIS +REPORT_UDIFF
{'access_token': '...',
 'expires_in': 300,
 'not-before-policy': 0,
 'refresh_expires_in': 0,
 'scope': 'email profile',
 'token_type': 'Bearer'}

The above code snippet is a confirmation that your credentials are set up
correctly. Congratulations! You won't need this access token directly, but Lino
will call it internally for every API call.

Suppliers
=========

Lino's :class:`Supplier` model matches what :term:`Ibanity` calls a `Supplier
resource <https://documentation.ibanity.com/einvoicing/1/api/curl#supplier>`__

The :mod:`lino_book.projects.noi1e` demo site contains three fictive
:term:`Ibanity suppliers <Ibanity supplier>`, which have been created in the
Ibanity environment when we run :cmd:`pm prep`.

List suppliers
--------------

>>> lst = list(ses.list_suppliers())
>>> len(lst) == 3
True
>>> pprint(lst[0])  #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
{'attributes': {'city': 'Eupen',
                'companyNumber': '0345678997',
                'contactEmail': 'info@example.com',
                'country': 'Belgium',
                'createdAt': '...',
                'email': 'info@example.com',
                'enterpriseIdentification': {'enterpriseNumber': '0345678997',
                                             'vatNumber': 'BE0345678997'},
                'homepage': 'https://',
                'ibans': [{'id': '...',
                           'value': 'BE86973367680150'}],
                'names': [{'id': '...',
                           'value': 'Number Three'}],
                'onboardingStatus': 'ONBOARDED',
                'peppolReceiver': False,
                'phoneNumber': '+3223344556',
                'street': 'Peppolstraße',
                'streetNumber': '34',
                'supportEmail': '',
                'supportPhone': '',
                'supportUrl': 'https://www.saffre-rumma.net/',
                'zip': '4700'},
  'id': '...',
  'type': 'supplier'}


Look up a supplier
------------------

>>> DEMO_SUPPLIER_ID = lst[0]['id']
>>> data, errmsg = ses.get_supplier(DEMO_SUPPLIER_ID)
>>> assert errmsg is None
>>> pprint(data)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
{'attributes': {'city': 'Eupen',
                'companyNumber': '0345678997',
                'contactEmail': 'info@example.com',
                'country': 'Belgium',
                'createdAt': '...',
                'email': 'info@example.com',
                'enterpriseIdentification': {'enterpriseNumber': '0345678997',
                                             'vatNumber': 'BE0345678997'},
                'homepage': 'https://',
                'ibans': [{'id': '...',
                           'value': 'BE86973367680150'}],
                'names': [{'id': '...',
                           'value': 'Number Three'}],
                'onboardingStatus': 'ONBOARDED',
                'peppolReceiver': False,
                'phoneNumber': '+3223344556',
                'street': 'Peppolstraße',
                'streetNumber': '34',
                'supportEmail': '',
                'supportPhone': '',
                'supportUrl': 'https://www.saffre-rumma.net/',
                'zip': '4700'},
 'id': '...',
 'type': 'supplier'}


>>> data, errmsg = ses.get_supplier('123456-789-abc')
>>> assert data is None
>>> print(errmsg)
{'code': 'invalidParameter', 'detail': "The parameter 'supplierId' expected type is: 'uuid'"}


Create a supplier
-----------------

Let's try to register a new supplier.

>>> d = supplier_attrs("BE1234567890")

Lino currently supports only countries that identify using VAT id. Enterprise
number is not used. In the future we might want to have both:

>>> pprint(d)
{'enterpriseIdentification': {'enterpriseNumber': '1234567890',
                              'vatNumber': 'BE1234567890'}}

The `enterpriseIdentification` is not enough:

>>> data, errmsg = ses.create_supplier(**d)
>>> print(errmsg)  #doctest: +NORMALIZE_WHITESPACE
city: must not be blank, contactEmail: must not be blank, country: must not be
blank, email: must not be blank, homepage: must not be null, ibans: must not be
empty, names: must not be empty, phoneNumber: must not be blank, street: must
not be blank, streetNumber: must not be blank, zip: must not be blank


>>> d["contactEmail"] = "contact@example.be"
>>> d["names"] = [{"value": "Company" }, {"value": "Company S.A."}]
>>> d["ibans"] = [{"value": "BE68539007547034"}, {"value": "BE38248017357572"}]
>>> d["city"] = "Eupen"
>>> d["country"] = "Belgium"
>>> d["email"] = "someone@example.com"
>>> d["homepage"] = "https://www.example.com"
>>> d["phoneNumber"] = "+3287654312"
>>> d["street"] = "Neustraße"
>>> d["streetNumber"] = "123"
>>> d["supportEmail"] = "support@example.be"
>>> d["supportPhone"] = "+3212345121"
>>> d["supportUrl"] = "www.support.com"
>>> d["zip"] = "4700"
>>> d["peppolReceiver"] = True

Even now that we specify all required data, it fails because our `vatNumber` is
invalid:

>>> data, errmsg = ses.create_supplier(**d)
>>> assert data is None
>>> print(errmsg)
enterpriseIdentification/enterpriseNumber: must be a valid Belgian enterprise number, enterpriseIdentification/vatNumber: must be a valid Belgian VAT number

It's not allowed to create a supplier for a company who is already registered at
another Peppol Access Point:

>>> d = supplier_attrs("BE0650238114", **d)
>>> data, errmsg = ses.create_supplier(**d)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
...
lino_xl.lib.peppol.utils.PeppolFailure: POST https://api.ibanity.com/einvoicing/suppliers/ () returned 409
{"errors":[{"code":"alreadyRegistered","detail":"A supplier already exists with this enterprise identification"}]} (options were {'json': {'data': {'type': 'supplier', 'attributes': {'enterpriseIdentification': {'enterpriseNumber': '0650238114', 'vatNumber': 'BE0650238114'}, 'contactEmail': 'contact@example.be', 'names': [{'value': 'Company'}, {'value': 'Company S.A.'}], 'ibans': [{'value': 'BE68539007547034'}, {'value': 'BE38248017357572'}], 'city': 'Eupen', 'country': 'Belgium', 'email': 'someone@example.com', 'homepage': 'https://www.example.com', 'phoneNumber': '+3287654312', 'street': 'Neustraße', 'streetNumber': '123', 'supportEmail': 'support@example.be', 'supportPhone': '+3212345121', 'supportUrl': 'www.support.com', 'zip': '4700', 'peppolReceiver': True}}},
...)

Here is a valid VAT number of a real company (called SA ETHIAS, found on
Internet) and we try to create a supplier from it with our fictive data:

>>> d = supplier_attrs("BE0404484654", **d)
>>> data, errmsg = ses.create_supplier(**d)  #doctest: +SKIP
>>> errmsg  #doctest: +SKIP
>>> pprint(data)  #doctest: +SKIP
{'attributes': {'city': 'Eupen',
                'companyNumber': '0404484654',
                'contactEmail': 'contact@example.be',
                'country': 'Belgium',
                'createdAt': '...',
                'email': 'someone@example.com',
                'enterpriseIdentification': {'enterpriseNumber': '0404484654',
                                             'vatNumber': 'BE0404484654'},
                'homepage': 'https://www.example.com',
                'ibans': [{'id': '...',
                           'value': 'BE68539007547034'},
                          {'id': '...',
                           'value': 'BE38248017357572'}],
                'names': [{'id': '...',
                           'value': 'Company'},
                          {'id': '...',
                           'value': 'Company S.A.'}],
                'onboardingStatus': 'ONBOARDED',
                'peppolReceiver': True,
                'phoneNumber': '+3287654312',
                'street': 'Neustraße',
                'streetNumber': '123',
                'supportEmail': 'support@example.be',
                'supportPhone': '+3212345121',
                'supportUrl': 'www.support.com',
                'zip': '4700'},
 'id': '...',
 'type': 'supplier'}

Above code snippet is skipped because the Ibanity API doesn't provide a way to
remove a supplier.  If we really ran that request on each test run, the Ibanity
environment would grow in an uncontrolled way.


List Peppol Registrations
=========================

A **registration** is when an supplier has registered with an Access Point. The
`List Peppol Registrations
<https://documentation.ibanity.com/einvoicing/1/api/curl#list-peppol-registrations>`_
call returns a list of registrations for a given supplier.

>>> lst = list(ses.list_registrations(DEMO_SUPPLIER_ID))

The result looks as follows, but we cannot test this here because it depends on
previous test runs.

>>> pprint(lst)  #doctest: +ELLIPSIS +SKIP
{'data': [{'attributes': {'accessPoints': ['Billit'],
                          'createdAt': '2023-08-16T12:38:16.662354Z',
                          'failedSince': '2023-08-16T12:38:16.662354Z',
                          'modifiedAt': '2023-08-16T12:38:22.575373Z',
                          'reason': 'already-registered',
                          'status': 'registration-failed',
                          'type': 'enterprise-number',
                          'value': '0143824670'},
           'id': '9d12d39d-2b03-4ea6-a770-f5d6b37edea7',
           'type': 'peppolRegistration'}]}


Customer search
=================

This can used to check whether my customer exists and whether they accept Peppol
invoices.

Small and medium enterprises don't use this feature because they just ask their
customer and then try whether it works.

>>> peppol_id = "9925:BE0840559537"
>>> res = ses.customer_search(peppol_id)
>>> pprint(res)  #doctest: +ELLIPSIS
{'data': {'attributes': {'customerReference': '9925:BE0840559537',
                         'supportedDocumentFormats': [{'customizationId': 'urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0',
                                                       'localName': 'CreditNote',
                                                       'profileId': 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
                                                       'rootNamespace': 'urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2',
                                                       'ublVersionId': '2.1'},
                                                      {'customizationId': 'urn:cen.eu:en16931:2017#conformant#urn:UBL.BE:1.0.0.20180214',
                                                       'localName': 'CreditNote',
                                                       'profileId': 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
                                                       'rootNamespace': 'urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2',
                                                       'ublVersionId': '2.1'},
                                                      {'customizationId': 'urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0',
                                                       'localName': 'Invoice',
                                                       'profileId': 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
                                                       'rootNamespace': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
                                                       'ublVersionId': '2.1'},
                                                      {'customizationId': 'urn:cen.eu:en16931:2017#conformant#urn:UBL.BE:1.0.0.20180214',
                                                       'localName': 'Invoice',
                                                       'profileId': 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
                                                       'rootNamespace': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
                                                       'ublVersionId': '2.1'}]},
          'id': '...',
          'type': 'peppolCustomerSearch'}}


The Flowin integration environment contains hard-coded fake data.  Using another
reference than ``'9925:BE0010012671'`` as `customerReference` will result in a
404 response, even when you specify a valid VAT number:

>>> res = ses.customer_search("9925:BE0433670865")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
Traceback (most recent call last):
...
lino_xl.lib.peppol.utils.PeppolFailure: POST
https://api.ibanity.com/einvoicing/peppol/customer-searches ()
returned 404
{"errors":[{"code":"customerNotFound","detail":"Customer not found: 9925:BE0433670865"}]}
(options were {...})

The ``ibans`` and ``names`` fields
==================================

The `Ibanity docs
<https://documentation.ibanity.com/einvoicing/1/api/curl#update-supplier>`__
describe how Lino must submit changes in the  the ``ibans`` and ``names``
fields.  The following snippets verify the rules.

>>> from lino_xl.lib.peppol.suppliers import update_id_list
>>> oldlist = [{'id': '123', 'value':'ABC'}]
>>> update_id_list(oldlist, "ABC")
[{'id': '123', 'value': 'ABC'}]

>>> update_id_list(oldlist, "ABC;DEF")
[{'id': '123', 'value': 'ABC'}, {'value': 'DEF'}]

>>> update_id_list(oldlist, "")
[]

>>> oldlist = []
>>> update_id_list(oldlist, "ABC")
[{'value': 'ABC'}]
>>> update_id_list(oldlist, "ABC;DEF")
[{'value': 'ABC'}, {'value': 'DEF'}]
>>> update_id_list(oldlist, "")
[]


The :manage:`list_suppliers` admin command
==========================================

The :manage:`list_suppliers` admin command lists the Ibanity suppliers defined
in the API environment connected to this Lino site.


.. management_command:: list_suppliers

Example run:

>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)
>>> shell('python manage.py list_suppliers')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
1) ... BE0345678997 ONBOARDED (Number Three)
2) ... BE0234567873 ONBOARDED (Number Two)
3) ... BE0123456749 ONBOARDED (Number One)





..
  At the end of this page we tidy up the database to avoid side effects in
  other pages:

  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
  >>> tidy_up_ibanity()
