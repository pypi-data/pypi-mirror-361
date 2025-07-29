.. doctest docs/specs/voga/trading.rst
.. _voga.specs.trading:

=======================================
The :mod:`lino_voga.lib.trading` plugin
=======================================

The :mod:`lino_voga.lib.trading` plugin extends :mod:`lino_xl.lib.trading`
for usage in :ref:`voga`.

See also :doc:`invoicing`.

TODO: review after 20230710


.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.voga2.startup import *

Dependencies
============

>>> dd.plugins.trading
<lino_xl.lib.trading.Plugin lino_voga.lib.trading(needs ['lino.modlib.memo', 'lino_xl.lib.products', 'lino_xl.lib.vat'])>


Examples
========

Here are all our sales invoices:

>>> jnl = rt.models.accounting.Journal.get_by_ref('SLS')
>>> rt.show(trading.InvoicesByJournal, jnl)
... #doctest: +ELLIPSIS +REPORT_UDIFF +SKIP
===================== ============ =================== ============ =================================== ============== =============== ================
 No.                   Entry date   Invoiceables from   until        Partner                             Subject line   Total to pay    Workflow
--------------------- ------------ ------------------- ------------ ----------------------------------- -------------- --------------- ----------------
 26/2015               01/03/2015   01/02/2015          28/02/2015   di Rupo Didier                                     48,00           **Registered**
 25/2015               01/03/2015   01/02/2015          28/02/2015   Radermacher Guido                                  100,00          **Registered**
 24/2015               01/03/2015   01/02/2015          28/02/2015   Emonts-Gast Erna                                   64,00           **Registered**
 23/2015               01/03/2015   01/02/2015          28/02/2015   Jacobs Jacqueline                                  48,00           **Registered**
 22/2015               01/03/2015   01/02/2015          28/02/2015   Evers Eberhart                                     48,00           **Registered**
 21/2015               01/02/2015   01/01/2015          31/01/2015   Dupont Jean                                        114,00          **Registered**
 20/2015               01/02/2015   01/01/2015          31/01/2015   Radermacher Jean                                   48,00           **Registered**
 19/2015               01/02/2015   01/01/2015          31/01/2015   Radermacher Hedi                                   48,00           **Registered**
 18/2015               01/02/2015   01/01/2015          31/01/2015   Emonts-Gast Erna                                   50,00           **Registered**
 17/2015               01/02/2015   01/01/2015          31/01/2015   Meier Marie-Louise                                 48,00           **Registered**
 16/2015               01/02/2015   01/01/2015          31/01/2015   Laschet Laura                                      48,00           **Registered**
 15/2015               01/02/2015   01/01/2015          31/01/2015   Kaivers Karl                                       50,00           **Registered**
 14/2015               01/02/2015   01/01/2015          31/01/2015   Engels Edgar                                       50,00           **Registered**
 13/2015               01/02/2015   01/01/2015          31/01/2015   Dobbelstein-Demeulenaere Dorothée                  96,00           **Registered**
 12/2015               01/02/2015   01/01/2015          31/01/2015   Charlier Ulrike                                    164,00          **Registered**
 11/2015               01/01/2015   01/12/2014          31/12/2014   Dupont Jean                                        98,00           **Registered**
 10/2015               01/01/2015   01/12/2014          31/12/2014   di Rupo Didier                                     48,00           **Registered**
 9/2015                01/01/2015   01/12/2014          31/12/2014   Radermacher Guido                                  164,00          **Registered**
 8/2015                01/01/2015   01/12/2014          31/12/2014   Emonts-Gast Erna                                   50,00           **Registered**
 7/2015                01/01/2015   01/12/2014          31/12/2014   Meier Marie-Louise                                 48,00           **Registered**
 6/2015                01/01/2015   01/12/2014          31/12/2014   Kaivers Karl                                       50,00           **Registered**
 5/2015                01/01/2015   01/12/2014          31/12/2014   Jonas Josef                                        64,00           **Registered**
 4/2015                01/01/2015   01/12/2014          31/12/2014   Jacobs Jacqueline                                  48,00           **Registered**
 3/2015                01/01/2015   01/12/2014          31/12/2014   Engels Edgar                                       48,00           **Registered**
 2/2015                01/01/2015   01/12/2014          31/12/2014   Evers Eberhart                                     48,00           **Registered**
 1/2015                01/01/2015   01/12/2014          31/12/2014   Charlier Ulrike                                    148,00          **Registered**
 71/2014               01/12/2014   01/11/2014          30/11/2014   Dupont Jean                                        98,00           **Registered**
 70/2014               01/12/2014   01/11/2014          30/11/2014   Radermacher Hedi                                   48,00           **Registered**
 69/2014               01/12/2014   01/11/2014          30/11/2014   Radermacher Guido                                  50,00           **Registered**
 68/2014               01/12/2014   01/11/2014          30/11/2014   Emonts-Gast Erna                                   114,00          **Registered**
 67/2014               01/12/2014   01/11/2014          30/11/2014   Laschet Laura                                      48,00           **Registered**
 66/2014               01/12/2014   01/11/2014          30/11/2014   Kaivers Karl                                       50,00           **Registered**
 65/2014               01/12/2014   01/11/2014          30/11/2014   Engels Edgar                                       50,00           **Registered**
 64/2014               01/12/2014   01/11/2014          30/11/2014   Dobbelstein-Demeulenaere Dorothée                  96,00           **Registered**
 63/2014               01/12/2014   01/11/2014          30/11/2014   Charlier Ulrike                                    100,00          **Registered**
 62/2014               01/11/2014   01/10/2014          31/10/2014   Dupont Jean                                        64,00           **Registered**
 61/2014               01/11/2014   01/10/2014          31/10/2014   Radermacher Jean                                   48,00           **Registered**
 60/2014               01/11/2014   01/10/2014          31/10/2014   Engels Edgar                                       50,00           **Registered**
 59/2014               01/11/2014   01/10/2014          31/10/2014   Charlier Ulrike                                    64,00           **Registered**
 58/2014               01/10/2014   01/09/2014          30/09/2014   Dupont Jean                                        50,00           **Registered**
 57/2014               01/10/2014   01/09/2014          30/09/2014   Radermacher Hedi                                   48,00           **Registered**
 56/2014               01/10/2014   01/09/2014          30/09/2014   Radermacher Guido                                  64,00           **Registered**
 55/2014               01/10/2014   01/09/2014          30/09/2014   Emonts-Gast Erna                                   50,00           **Registered**
 54/2014               01/10/2014   01/09/2014          30/09/2014   Laschet Laura                                      48,00           **Registered**
 53/2014               01/10/2014   01/09/2014          30/09/2014   Jonas Josef                                        64,00           **Registered**
 52/2014               01/10/2014   01/09/2014          30/09/2014   Engels Edgar                                       50,00           **Registered**
 51/2014               01/10/2014   01/09/2014          30/09/2014   Dobbelstein-Demeulenaere Dorothée                  96,00           **Registered**
 50/2014               01/09/2014   01/08/2014          31/08/2014   Dupont Jean                                        50,00           **Registered**
 49/2014               01/09/2014   01/08/2014          31/08/2014   Emonts-Gast Erna                                   50,00           **Registered**
 48/2014               01/08/2014   01/07/2014          31/07/2014   Dupont Jean                                        114,00          **Registered**
 47/2014               01/08/2014   01/07/2014          31/07/2014   Emonts-Gast Erna                                   114,00          **Registered**
 46/2014               01/08/2014   01/07/2014          31/07/2014   Engels Edgar                                       50,00           **Registered**
 45/2014               01/08/2014   01/07/2014          31/07/2014   Charlier Ulrike                                    64,00           **Registered**
 44/2014               01/07/2014   01/06/2014          30/06/2014   Radermacher Guido                                  64,00           **Registered**
 43/2014               01/07/2014   01/06/2014          30/06/2014   Jonas Josef                                        64,00           **Registered**
 42/2014               01/07/2014   01/06/2014          30/06/2014   Engels Edgar                                       50,00           **Registered**
 41/2014               01/06/2014   01/05/2014          31/05/2014   Dupont Jean                                        50,00           **Registered**
 40/2014               01/06/2014   01/05/2014          31/05/2014   Emonts-Gast Erna                                   50,00           **Registered**
 39/2014               01/06/2014   01/05/2014          31/05/2014   Engels Edgar                                       50,00           **Registered**
 38/2014               01/05/2014   01/04/2014          30/04/2014   Dupont Jean                                        50,00           **Registered**
 37/2014               01/05/2014   01/04/2014          30/04/2014   Emonts-Gast Erna                                   50,00           **Registered**
 36/2014               01/04/2014   01/03/2014          31/03/2014   Dupont Jean                                        64,00           **Registered**
 35/2014               01/04/2014   01/03/2014          31/03/2014   Emonts-Gast Erna                                   64,00           **Registered**
 34/2014               01/04/2014   01/03/2014          31/03/2014   Engels Edgar                                       50,00           **Registered**
 33/2014               01/03/2014   01/02/2014          28/02/2014   Dupont Jean                                        50,00           **Registered**
 32/2014               01/03/2014   01/02/2014          28/02/2014   Emonts-Gast Erna                                   50,00           **Registered**
 31/2014               01/02/2014   01/01/2014          31/01/2014   Dupont Jean                                        50,00           **Registered**
 30/2014               01/02/2014   01/01/2014          31/01/2014   Emonts-Gast Erna                                   50,00           **Registered**
 29/2014               01/02/2014   01/01/2014          31/01/2014   Engels Edgar                                       50,00           **Registered**
 28/2014               01/01/2014                       31/12/2013   Jeanémart Jérôme                                   20,00           **Registered**
 27/2014               01/01/2014                       31/12/2013   Brecht Bernd                                       295,00          **Registered**
 26/2014               01/01/2014                       31/12/2013   Lahm Lisa                                          240,00          **Registered**
 25/2014               01/01/2014                       31/12/2013   Dupont Jean                                        442,00          **Registered**
 24/2014               01/01/2014                       31/12/2013   Ärgerlich Erna                                     80,00           **Registered**
 23/2014               01/01/2014                       31/12/2013   di Rupo Didier                                     68,00           **Registered**
 22/2014               01/01/2014                       31/12/2013   Radermacher Jean                                   96,00           **Registered**
 21/2014               01/01/2014                       31/12/2013   Radermacher Hedi                                   248,00          **Registered**
 20/2014               01/01/2014                       31/12/2013   Radermacher Guido                                  214,00          **Registered**
 19/2014               01/01/2014                       31/12/2013   Radermacher Edgard                                 48,00           **Registered**
 18/2014               01/01/2014                       31/12/2013   Radermacher Christian                              395,00          **Registered**
 17/2014               01/01/2014                       31/12/2013   Emonts-Gast Erna                                   486,00          **Registered**
 16/2014               01/01/2014                       31/12/2013   Meier Marie-Louise                                 324,00          **Registered**
 15/2014               01/01/2014                       31/12/2013   Leffin Josefine                                    20,00           **Registered**
 14/2014               01/01/2014                       31/12/2013   Laschet Laura                                      296,00          **Registered**
 13/2014               01/01/2014                       31/12/2013   Kaivers Karl                                       180,00          **Registered**
 12/2014               01/01/2014                       31/12/2013   Jonas Josef                                        64,00           **Registered**
 11/2014               01/01/2014                       31/12/2013   Jacobs Jacqueline                                  678,00          **Registered**
 10/2014               01/01/2014                       31/12/2013   Hilgers Hildegard                                  80,00           **Registered**
 9/2014                01/01/2014                       31/12/2013   Engels Edgar                                       426,00          **Registered**
 8/2014                01/01/2014                       31/12/2013   Emonts Daniel                                      240,00          **Registered**
 7/2014                01/01/2014                       31/12/2013   Evers Eberhart                                     48,00           **Registered**
 6/2014                01/01/2014                       31/12/2013   Dobbelstein-Demeulenaere Dorothée                  116,00          **Registered**
 5/2014                01/01/2014                       31/12/2013   Demeulenaere Dorothée                              60,00           **Registered**
 4/2014                01/01/2014                       31/12/2013   Dericum Daniel                                     80,00           **Registered**
 3/2014                01/01/2014                       31/12/2013   Charlier Ulrike                                    356,00          **Registered**
 2/2014                01/01/2014                       31/12/2013   Bastiaensen Laurent                                20,00           **Registered**
 1/2014                01/01/2014                       31/12/2013   Altenberg Hans                                     295,00          **Registered**
 **Total (97 rows)**                                                                                                    **10 401,00**
===================== ============ =================== ============ =================================== ============== =============== ================
<BLANKLINE>

The :class:`lino_xl.lib.trading.DueInvoices` table shows a list of invoices that
aren't (completeley) paid.  Example see :doc:`/projects/cosi1`.

Printing invoices
=================

We take a sales invoice, clear the cache, ask Lino to print it and
check whether we get the expected response.

>>> ses = rt.login("robin")
>>> dd.translation.activate('en')
>>> obj = trading.VatProductInvoice.objects.all()[0]
>>> obj.clear_cache()
>>> d = ses.run(obj.do_print)
... #doctest: +ELLIPSIS
appy.pod render .../trading/config/trading/VatProductInvoice/Default.odt -> .../media/cache/appypdf/SLS-2014-1.pdf

>>> d['success']
True

>>> print(d['message'])
Your printable document (<a href="/media/cache/appypdf/SLS-2014-1.pdf">SLS-2014-1.pdf</a>) should now open in a new browser window. If it doesn't, please ask your system administrator.

Trading rules
=============

>>> rt.show(trading.TradingRules)
==== =================================== ============ =================== ======================================= ============
 ID   Partner                             Trade type   Invoicing address   Payment term                            Paper type
---- ----------------------------------- ------------ ------------------- --------------------------------------- ------------
 1    Arens Annette                       Sales                            Payment end of month
 2    Faymonville Luc                     Sales        Engels Edgar        Payment end of month
 3    Radermacher Alfons                  Sales        Emonts-Gast Erna    Payment 90 days after invoice date
 4    Martelaer Mark                      Sales        Dupont Jean         Payment in advance
 5    Bestbank                            Sales                            Payment in advance
 6    Rumma & Ko OÜ                       Sales                            Payment seven days after invoice date
 7    Bäckerei Ausdemwald                 Sales                            Payment ten days after invoice date
 8    Bäckerei Mießen                     Sales                            Payment 30 days after invoice date
 9    Bäckerei Schmitz                    Sales                            Payment 60 days after invoice date
 10   Garage Mergelsberg                  Sales                            Payment 90 days after invoice date
 11   Donderweer BV                       Sales                            Payment end of month
 12   Van Achter NV                       Sales                            Prepayment 30%
 13   Hans Flott & Co                     Sales                            Payment in advance
 14   Bernd Brechts Bücherladen           Sales                            Payment seven days after invoice date
 15   Reinhards Baumschule                Sales                            Payment ten days after invoice date
 16   Moulin Rouge                        Sales                            Payment 30 days after invoice date
 17   Auto École Verte                    Sales                            Payment 60 days after invoice date
 18   Arens Andreas                       Sales                            Payment 90 days after invoice date
 19   Altenberg Hans                      Sales                            Prepayment 30%
 20   Ausdemwald Alfons                   Sales                            Payment in advance
 21   Bastiaensen Laurent                 Sales                            Payment seven days after invoice date
 22   Collard Charlotte                   Sales                            Payment ten days after invoice date
 23   Charlier Ulrike                     Sales                            Payment 30 days after invoice date
 24   Chantraine Marc                     Sales                            Payment 60 days after invoice date
 25   Dericum Daniel                      Sales                            Payment 90 days after invoice date
 26   Demeulenaere Dorothée               Sales                            Payment end of month
 27   Dobbelstein-Demeulenaere Dorothée   Sales                            Prepayment 30%
 28   Dobbelstein Dorothée                Sales                            Payment in advance
 29   Ernst Berta                         Sales                            Payment seven days after invoice date
 30   Evertz Bernd                        Sales                            Payment ten days after invoice date
 31   Evers Eberhart                      Sales                            Payment 30 days after invoice date
 32   Emonts Daniel                       Sales                            Payment 60 days after invoice date
 33   Engels Edgar                        Sales                            Payment 90 days after invoice date
 34   Gernegroß Germaine                  Sales                            Prepayment 30%
 35   Groteclaes Gregory                  Sales                            Payment in advance
 36   Hilgers Hildegard                   Sales                            Payment seven days after invoice date
 37   Hilgers Henri                       Sales                            Payment ten days after invoice date
 38   Ingels Irene                        Sales                            Payment 30 days after invoice date
 39   Jansen Jérémy                       Sales                            Payment 60 days after invoice date
 40   Jacobs Jacqueline                   Sales                            Payment 90 days after invoice date
 41   Johnen Johann                       Sales                            Payment end of month
 42   Jonas Josef                         Sales                            Prepayment 30%
 43   Jousten Jan                         Sales                            Payment in advance
 44   Kaivers Karl                        Sales                            Payment seven days after invoice date
 45   Lambertz Guido                      Sales                            Payment ten days after invoice date
 46   Laschet Laura                       Sales                            Payment 30 days after invoice date
 47   Lazarus Line                        Sales                            Payment 60 days after invoice date
 48   Leffin Josefine                     Sales                            Payment 90 days after invoice date
 49   Malmendier Marc                     Sales                            Payment end of month
 50   Meessen Melissa                     Sales                            Prepayment 30%
 51   Mießen Michael                      Sales                            Payment in advance
 52   Meier Marie-Louise                  Sales                            Payment seven days after invoice date
 53   Emonts Erich                        Sales                            Payment ten days after invoice date
 54   Emontspool Erwin                    Sales                            Payment 30 days after invoice date
 55   Emonts-Gast Erna                    Sales                            Payment 60 days after invoice date
 56   Radermacher Berta                   Sales                            Payment end of month
 57   Radermacher Christian               Sales                            Prepayment 30%
 58   Radermacher Daniela                 Sales                            Payment in advance
 59   Radermacher Edgard                  Sales                            Payment seven days after invoice date
 60   Radermacher Fritz                   Sales                            Payment ten days after invoice date
 61   Radermacher Guido                   Sales                            Payment 30 days after invoice date
 62   Radermacher Hans                    Sales                            Payment 60 days after invoice date
 63   Radermacher Hedi                    Sales                            Payment 90 days after invoice date
 64   Radermacher Inge                    Sales                            Payment end of month
 65   Radermacher Jean                    Sales                            Prepayment 30%
 66   di Rupo Didier                      Sales                            Payment in advance
 67   da Vinci David                      Sales                            Payment seven days after invoice date
 68   van Veen Vincent                    Sales                            Payment ten days after invoice date
 69   Õunapuu Õie                         Sales                            Payment 30 days after invoice date
 70   Östges Otto                         Sales                            Payment 60 days after invoice date
 71   Ärgerlich Erna                      Sales                            Payment 90 days after invoice date
 72   Bodard Bernard                      Sales                            Payment end of month
 73   Dupont Jean                         Sales                            Prepayment 30%
 74   Radermecker Rik                     Sales                            Payment seven days after invoice date
 75   Vandenmeulenbos Marie-Louise        Sales                            Payment ten days after invoice date
 76   Eierschal Emil                      Sales                            Payment 30 days after invoice date
 77   Lahm Lisa                           Sales                            Payment 60 days after invoice date
 78   Brecht Bernd                        Sales                            Payment 90 days after invoice date
 79   Keller Karl                         Sales                            Payment end of month
 80   Dubois Robin                        Sales                            Prepayment 30%
 81   Denon Denis                         Sales                            Payment in advance
 82   Jeanémart Jérôme                    Sales                            Payment seven days after invoice date
==== =================================== ============ =================== ======================================= ============
<BLANKLINE>


..
  >>> dbhash.check_virgin()  #doctest: +ELLIPSIS
  Database .../voga2 isn't virgin:
  - excerpts.Excerpt: 1 rows added
  Tidy up 1 rows from database: [(<class 'lino_xl.lib.excerpts.models.Excerpt'>, {...})].
  Database has been restored.
