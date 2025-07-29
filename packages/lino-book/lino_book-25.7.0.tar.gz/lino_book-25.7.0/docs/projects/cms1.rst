.. doctest docs/projects/cms1.rst
.. _book.projects.cms1:

=======================================
``cms1`` : a content management system
=======================================

.. module:: lino_book.projects.cms1

A :term:`demo project` showing a :ref:`cms`.

It includes a page with usage examples of the :cmd:`[file]` and
:cmd:`[gallery]` commands. To see it, say :cmd:`go cms1` followed by :cmd:`pm
runserver` and then point your browser to http://127.0.0.1:8000/p/9


>>> from lino import startup
>>> startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *
>>> mp = settings.SITE.plugins.memo.parser

>>> rt.models.uploads.Upload.objects.get(description__startswith="Murder")
Upload #13 ('Murder on the orient express cover')


>>> print(mp.parse("[file 13] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:100%; max-height:20ex" title="Murder on the orient
express cover"/></a> Some text.

>>> print(mp.parse("[file 13 My caption] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:100%; max-height:20ex" title="My caption"/></a>
Some text.

>>> print(mp.parse("[file 13 thumb|My caption] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:100%; float:right; max-height:20ex" title="My
caption"/></a> Some text.


>>> print(mp.parse("[file 13 thumb|right|My caption] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:100%; float:right; max-height:20ex" title="My
caption"/></a> Some text.

>>> print(mp.parse("[file 13 right|thumb|My caption] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
[ERROR Invalid format name 'right' (allowed names are ('thumb', 'tiny', 'wide',
'solo', 'duo', 'trio')). in '[file 13 right|thumb|My caption]' at position
0-32] Some text.

>>> print(mp.parse("[file 13 thumb|right|] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:100%; float:right; max-height:20ex" title="Murder
on the orient express cover"/></a> Some text.

The only difference between ``thumb`` and ``tiny`` is the size of the image. For
``thumb`` it has a height of `10em` and for ``tiny`` the height is `5em`.

We don't specify the width in order to let the browser compute it. We specify
the height and not the width because we don't care about whether the image is
landscape or portrait.

>>> print(mp.parse("[file 13 tiny|My caption] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:25%; max-height:15ex" title="My caption"/></a>
Some text.


>>> print(mp.parse("[file 13 wide|A wide image] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:100%; max-height:30ex" title="A wide image"/></a>
Some text.

Spaces around the pipe character don't count:

>>> print(mp.parse("[file 13 wide | A wide image] Some text."))
... #doctest: +NORMALIZE_WHITESPACE
<a href="/admin/#/api/uploads/Uploads/13" target="_blank"><img
src="/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg"
style="padding:4px; max-width:100%; max-height:30ex" title="A wide image"/></a>
Some text.

The syntax is given by the
:func:`rstgen.sphinxconf.sigal_image.parse_image_spec`
function.

"image URL" versus "download URL"
=================================

>>> obj = uploads.Upload.objects.get(pk=13)
>>> mf = obj.get_media_file()
>>> print(mf.get_download_url())
/media/uploads/2022/09/MurderontheOrientExpress.jpg
>>> print(mf.get_image_url())
/media/thumbs/uploads/2022/09/MurderontheOrientExpress.jpg

>>> # obj = uploads.Upload.objects.get(pk=18)
>>> obj = uploads.Upload.objects.get(description__startswith="History")
>>> obj
Upload #20 ('History of PDF')
>>> mf = obj.get_media_file()
>>> print(mf.get_download_url())
/media/uploads/2022/09/History_of_PDF.pdf
>>> print(mf.get_image_url())
/media/thumbs/uploads/2022/09/History_of_PDF.pdf.png

Don't read me
=============

The following request had caused a traceback:

>>> res = test_client.get("/s/1")
>>> txt = beautiful_soup(res.content.decode()).text
>>> "Private collection by Luc Saffre" in txt
True

>>> res = test_client.get("/b/1")

But let's extend above test to systematically loop over all publisher locations
and GET each item:

>>> for loc, dv in dd.plugins.publisher.locations:
...     for obj in dv.model.objects.all():
...         url = "/{}/{}".format(loc, obj.pk)
...         # print(dv, url)
...         res = test_client.get(url)
...         if res.status_code not in {200, 302}:
...             print(f"{url} failed with {res.status_code} ({res.content.decode()})")

>>> [obj.pk for obj in blogs.LatestEntries.request()]
[2, 3, 4, 5, 1]
