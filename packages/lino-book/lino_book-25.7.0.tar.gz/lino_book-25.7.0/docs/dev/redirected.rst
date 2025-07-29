.. doctest docs/dev/redirected.rst
.. _dev.redirected_urls:

========================
Redirected historic URLs
========================

The documentation system of the :ref:`Lino framework <lf>` has evolved over the
years.  Here are some links that have been published in different places and the
content of which has been moved to an new URL. 


>>> import requests
>>> from bs4 import BeautifulSoup
>>> def test(url, text=None):
...     r = requests.get(url)
...     if r.status_code != 200:
...          print("Oops: {} --> {}".format(url, r.status_code))
...     if text is not None:
...         soup = BeautifulSoup(r.content, 'lxml')
...         got = soup.get_text(" ", strip=True)
...         if text not in got:
...             print("Oops {} has no text {} (it has {})".format(url, text, got))
...

>>> test("https://saffre-rumma.net/posts/2021/0130/", "Lino-Lösungen für die Kleinen")  # 20210202
>>> test("https://saffre-rumma.net/fr/lino/welfare/")  # 20210423
>>> # test("https://fr.welfare.lino-framework.org/clients.html")  # 20210423
>>> test("https://saffre-rumma.net/fr/services/lino4all/")  # 20210423
>>> # test("https://de.welfare.lino-framework.org/changes/19.11.0.html")  # 20200103
>>> test("https://luc.lino-framework.org/blog/2020/0628.html")  # 20200630
>>> test("https://eidreader.lino-framework.org/install.html#install-eidreader-on-windows")

The following URLs are no longer being automatically redirected:

>>> # test("https://weleup.lino-framework.org/changes/coming.html")  # 20200103
