.. _dg.topics.urls:

============================
Handling URLs in text fields
============================

In the text editor you can hit :kbd:`Ctrl-K` to insert a clickable weblink (a
``<a href="">`` tag). If you paste a URL into a rich text field, Lino will
automatically convert it into a clickable weblink.


.. contents::
   :local:
   :depth: 2

.. include:: /../docs/shared/include/tested.rst


Make URLs clickable
===================

The :func:`lino.utils.soup.sanitize` function internally calls
:func:`lino.utils.soup.url2a`, which recognizes URLs in a plain text and
converts them into clickable links.

>>> from lino.utils.soup import url2a

>>> print(url2a("https://www.example.com"))
<a href="https://www.example.com" target="_blank">www.example.com</a>

Of course we don't want it to convert a weblink that has already been converted:

>>> print(url2a('<a href="https://www.example.com">www.example.com</a>'))
<a href="https://www.example.com">www.example.com</a>

Invalid URLs aren't converted:

>>> print(url2a("http://invalid-url"))
http://invalid-url

More examples:

>>> print(url2a("https://www.foo.com/bar/baz.tgz"))
<a href="https://www.foo.com/bar/baz.tgz" target="_blank">www.foo.com/bar/baz.tgz</a>


>>> content = """
... <p>Some url: https://foo.example.com and
... some other url: https://saffre-rumma.net</p>
... """.strip()
>>> print(url2a(content))
<p>Some url: <a href="https://foo.example.com" target="_blank">foo.example.com</a> and
some other url: <a href="https://saffre-rumma.net" target="_blank">saffre-rumma.net</a></p>

>>> print(url2a("""A <a href="https://www.foo.com/foo">foo</a>
... and a <a href="https://bar.com">bar</a>."""))
A <a href="https://www.foo.com/foo">foo</a>
and a <a href="https://bar.com">bar</a>.


TODO
====

When :mod:`lino_xl.lib.sources` is installed, weblink will be converted into a
:class:`lino_xl.lib.sources.Source` row and a memo command:

>>> print(url2a('<a href="https://www.example.com">www.example.com</a>'))
... #doctest: +SKIP
[source 123 The retrieved title of the page]

Multiple links to the same URL will reuse the same
:class:`lino_xl.lib.sources.Source` row:

>>> print(url2a('<a href="https://www.example.com">www.example.com</a>'))
... #doctest: +SKIP
[source 123 The retrieved title of the page]
