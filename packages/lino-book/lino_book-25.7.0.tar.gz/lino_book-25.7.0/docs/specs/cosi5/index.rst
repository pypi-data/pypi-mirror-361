.. doctest docs/specs/cosi5/index.rst
.. _i18n.bn:

===============
Lino in Bengali
===============

Lino translations to Bengali were contributed by Sharif Mehedi. The
:mod:`lino_book.projects.cosi5` project makes them visible.

Here is a screenshot:

.. image:: /images/screenshots/0307_cosi5_bn.png


.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.cosi5.settings')
>>> from lino.api.doctest import *

The main menu in English and Bengali:

>>> show_menu('robin')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Contacts : Persons, Organizations
- Office : My Excerpts, My Upload files, My Notification messages
- Sales : Sales invoices (SLS), Sales notes (SSN), My invoicing plan
- Reports :
  - Accounting : Debtors, Creditors, Accounting Report
  - Sales : Due invoices
- Configure :
  - System : Users, Site configuration, System tasks
  - Places : Countries, Places
  - Contacts : Legal forms, Functions
  - Office : Excerpt Types, Library volumes, Upload types
  - Accounting : Accounts, Journals, Payment terms, Payment methods, Sheet items, Fiscal years, Accounting periods
  - Sales : Products, Product Categories, Price rules, Paper types, Flatrates, Follow-up rules, Invoicing tasks
- Explorer :
  - System : Authorities, User types, User roles, content types, Notification messages, Background procedures, Data checkers, Data problem messages
  - Contacts : Contact persons, Partners, Contact detail types, Contact details
  - Office : Excerpts, Upload files, Upload areas, Mentions
  - Accounting : Common accounts, Match rules, Vouchers, Voucher types, Movements, Trade types, Journal groups, Accounting Reports, Common sheet items, General account balances, Analytic accounts balances, Partner balances, Sheet item entries
  - SEPA : Bank accounts
  - Sales : Price factors, Trading rules, Trading invoices, Trading invoice items, Invoicing plans
  - Financial : Bank statements, Journal entries, Payment orders
  - VAT : VAT areas, VAT regimes, VAT classes, VAT columns, Ledger invoices, VAT rules
- Site : About, User sessions


>>> show_menu('roby')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF +SKIP
- যোগাযোগ : ব্যক্তি, সংস্থা
- অফিস : আমার উদ্ধৃতি, আমার ফাইল আপলোড
- বিক্রয় : বিক্রয়ের চালান (SLS), বিক্রয় চালান (SSN), বিক্রয় চালান প্রকল্প
- রিপোর্ট :
  - হিসাবরক্ষণ : দেনাদার, পাওনাদার, হিসাবরক্ষণ রিপোর্ট
  - বিক্রয় : বকেয়া চালান
- কনফিগার :
  - সিস্টেম : ব্যাবহারকারী, সাইট প্যারামিটার, System tasks
  - স্থান : দেশ, স্থান
  - যোগাযোগ : আইনি ফর্ম, কর্মরূপ
  - অফিস : উদ্ধৃতিরূপ, গ্রন্থ খন্ড, আপলোডের ধরন
  - হিসাবরক্ষণ : হিসাব, খতিয়ান, আর্থিক বছর, হিসাবরক্ষণ কাল, পরিশোধের সর্ত, পরিশোধের নিয়ম, শীট আইটেম, হিসাবরক্ষণ কাল, আর্থিক বছর
  - বিক্রয় : পণ্য, পণ্যের ধরন, দামের বিধি, কাগজের ধরন, একদর, পশ্চাদাবনির নিতি, চালান প্রকল্প
- অনুসন্ধান :
  - সিস্টেম : কর্তৃপক্ষ, ব্যবহারকারীর ধরন, ব্যবহারকারীর ভূমিকা, কনটেন্ট টাইপ সমূহ, নেপথ্য কার্যপ্রণালী, তথ্য পরীক্ষক, তথ্য সমস্যা
  - যোগাযোগ : ব্যক্তি যোগাযোগ, অংশীদার, যোগাযোগ ঠিকানার ধরন, যোগাযোগের ঠিকানা
  - অফিস : উদ্ধৃতি, ফাইল আপলোড, স্থান আপলোড, উল্লেখ
  - হিসাবরক্ষণ : সাধারন হিসাব, মিলন বিধি, ভাউচার, ভাউচারের ধরন, গতিবিধি, লেনদেনের ধরন, খতিয়ান শ্রেণী, হিসাবরক্ষন রিপোর্ট, প্রচলিত শীট আইটেম, সাধারন হিসাব ভারসাম্য, বিশ্লেষণমূলক হিসাব ভারসাম্য, অংশীদার হিসাব ভারসাম্য, শীট আইটেম লিপিভুক্তি
  - এস ই পি এ (SEPA) : ব্যাং হিসাব
  - বিক্রয় : দামের প্রভাবক, বিক্রয়ের চালান, পণ্য বিক্রয় চালান, বিক্রয় চালান প্রকল্প, বিক্রয় নিতি
  - আর্থিক : ব্যাং বিবরণী, খতিয়ান লিপিভুক্তি, পরিশোধ ফরমাশ
  - কর : কর অঞ্চল, কর আমল, কর শ্রেণী, কর কলাম, চালান, কর বিধি
- সাইট : প্রামাণ্য, ইউজার সেশন


Example of :term:`multilingual database content`:

>>> rt.show(products.Products)
==== ================================================================ ===================================================== ================= =============
 ID   Designation                                                      Designation (bn)                                      Category          Sales price
---- ---------------------------------------------------------------- ----------------------------------------------------- ----------------- -------------
 10   Book                                                             বই                                                    Other             29,90
 6    IT consultation & maintenance                                    আই টি (IT) পরামর্শ এবং রক্ষণাবেক্ষণ                      Website Hosting   30,00
 9    Image processing and website content maintenance                 ছবি প্রক্রিয়াজাতকরণ এবং ওয়েবসাইটের বিষয়াধি রক্ষণাবেক্ষণ   Website Hosting   25,00
 4    Metal chair                                                      ধাতব চেয়ার                                            Furniture         79,99
 3    Metal table                                                      ধাতব টেবিল                                            Furniture         129,99
 8    Programming                                                      প্রোগ্রামিং                                             Website Hosting   40,00
 7    Server software installation, configuration and administration   সার্ভার সফটওয়্যার স্থাপন, কনফিগারেশন এবং প্রশাসন          Website Hosting   35,00
 11   Stamp                                                            স্ট্যাম্প                                                Other             1,40
 12   Subtotal                                                         Subtotal
 5    Website hosting 1MB/month                                        ওয়েবসাইট হোস্টিং ১এমবি(1MB)/মাস                        Website Hosting   3,99
 2    Wooden chair                                                     কাঠের চেয়ার                                           Furniture         99,99
 1    Wooden table                                                     কাঠের টেবিল                                           Furniture         199,99
                                                                                                                                               **675,25**
==== ================================================================ ===================================================== ================= =============
<BLANKLINE>
