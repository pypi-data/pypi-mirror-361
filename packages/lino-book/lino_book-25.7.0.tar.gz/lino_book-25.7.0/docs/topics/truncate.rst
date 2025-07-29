.. doctest docs/topics/truncate.rst
.. _book.topics.truncate:

=====================================
Truncating HTML texts
=====================================

.. currentmodule:: lino.utils.soup

This document digs deeper into the :func:`truncate_comment` function.

The function was reimplemented in July 2023, triggered by :ticket:`5039`
(Comment with a ``<base>`` tag caused Jane to break). In February 2025 we had
:ticket:`5916` (truncate_comment truncates in the middle of a html tag).


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst


Longer examples
===============

The default `max_length` of :func:`truncate_comment` is 300. In Lino we can
override this default value in :setting:`memo.short_preview_length`.

One day we made a copy of the English Wikipedia start page and stored it into
our demo data for testing purposes. It contains 121 KB of data.

>>> from lino_book import DEMO_DATA
>>> html = (DEMO_DATA / "html" / "wikipedia.html").read_text()
>>> len(html)
121429

Let's truncate it:

>>> from lino.utils.soup import truncate_comment as tc

>>> print(tc(html, 10))  #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF -ELLIPSIS
<a class="mw-jump-link" href="#bodyContent">Jump to co...</a>

Even when truncated, the HTML is very long because it contains tags without
textual content but with long class and style and title and src tags. So,
according to our rules, even the short_preview of a Wikipedia page will take
quite much space:

>>> len(tc(html, 100)) > 70000
True

TODO: The truncated HTML still contains more than one image (because
TextCollector doesn't descend into the children of `<span>` tags):

>>> print(tc(html, 100)[:1000])
... #doctest: -SKIP +NORMALIZE_WHITESPACE +REPORT_UDIFF -ELLIPSIS
<a class="mw-jump-link" href="#bodyContent">Jump to content</a>
<BLANKLINE>
<span>
<div class="vector-header-start">
<span>
<div class="vector-dropdown vector-main-menu-dropdown vector-button-flush-left vector-button-flush-right" title="Main menu">
<span/>
<span><span class="vector-icon mw-ui-icon-menu mw-ui-icon-wikimedia-menu"></span>
<span class="vector-dropdown-label-text">Main menu</span>
</span>
<div class="vector-dropdown-content">
<div class="vector-unpinned-container">
</div>
</div>
</div>
</span>
<a class="mw-logo" href="/wiki/Main_Page">
<img alt="" class="mw-logo-icon" src="/static/images/icons/wikipedia.png"/>
<span class="mw-logo-container skin-invert">
<img alt="Wikipedia" class="mw-logo-wordmark" src="/static/images/mobile/copyright/wikipedia-wordmark-en.svg" style="width: 7.5em; height: 1.125em;"/>
<img alt="The Free Encyclopedia" class="mw-logo-tagline" src="/static/images/mobile/copyright/wikipedia-tagline-en.svg" style="width: 7.3125em; height: 0.8125em;"/>
</span>
</a>
</div>




Sanitizing
==========

The :func:`truncate_comment <lino.modlib.memo.truncate_comment>` function also
sanitizes the content, similar to :func:`sanitize`.

..
  : it does not try to remove dangerous html
  (because this must be done also for non-truncated HTML and is the job of bleach)

>>> print(tc("""<p>foo <html><head><base href="bar" target="_blank"></head><body></p><p>baz</p>"""))
... #doctest: +NORMALIZE_WHITESPACE
foo  <span/>baz

Let's try to truncate a whole HTML page:

>>> html_str = """
... <!doctype html><html lang="en">
... <head><title>Bad Request (400)</title></head>
... <body>
... <h1>Bad Request (400)</h1>
... <p></p>
... </body>
... </html>"""

>>> print(tc(html_str)) #doctest: +NORMALIZE_WHITESPACE
<span>Bad Request (400)</span>

Verifying :ticket:`5916` (truncate_comment truncates in the middle of a html
tag):

Simplified case:

>>> body = """<span class="a"><span class="b">1234</span></span> 5678 90"""
>>> print(tc(body, max_length=7))
<span class="a"><span class="b">1234</span></span> 56...

Full case:

>>> body = """After talking about it with <span class="mention"
... data-denotation-char="@"
... data-index="0" data-link="javascript:window.App.runAction({\'actorId\':
... \'users.AllUsers\', \'an\': \'detail\', \'rp\': null, \'status\':
... {\'record_id\': 347}})" data-title="Sharif Mehedi"
... data-value="8lurry">\ufeff<span
... contenteditable="false">@8lurry</span>\ufeff</span> : Yes, let\'s replace the
... card_layout by as_card(). And when working on this, also think about how to
... configure the width of the cards (as mentioned in #5385, BUT let\'s wait with
... actually doing this until we have a concrete use case for cards. Right now they
... are just a kind of nice gimmick.'"""
>>> print(tc(body))  #doctest: +NORMALIZE_WHITESPACE
After talking about it with <span class="mention" data-denotation-char="@"
data-index="0" data-link="javascript:window.App.runAction({'actorId':
'users.AllUsers', 'an': 'detail', 'rp': null, 'status': {'record_id': 347}})"
data-title="Sharif Mehedi" data-value="8lurry">﻿<span
contenteditable="false">@8lurry</span>﻿</span> : Yes, let's replace the
card_layout by as_card(). And when working on this, also think about how to
configure the width of the cards (as mentioned in #5385, BUT let's wait with
actually doing this until we have a concrete use case for cards. Right now they
are just a ki...

.. _dg.truncate.fixed:

Fixed bugs
==========

Until 20250606, the truncated text did not escape "<" and ">", causing
:ticket:`6142`. Now it works:

>>> print(tc(r"Let's replace [url] memo commands by &lt;a href&gt; tags."))
Let's replace [url] memo commands by &lt;a href&gt; tags.

>>> print(tc("100 < 500"))
100 &lt; 500
>>> print(tc(">>> print('Hello, world!')"))
&gt;&gt;&gt; print('Hello, world!')


The following snippet shows that :ticket:`5039` is fixed after 20250606. HTML
tags that are escaped in the source text must remain escaped in the result.

>>> escaped_html = """
... <p>For example
... &lt;html&gt;&lt;head&gt;&lt;base href="bar" target="_blank"&gt;&lt;/head&gt;
... &lt;body&gt;
... </p>"""
>>> print(tc(escaped_html))
... #doctest: +NORMALIZE_WHITESPACE -SKIP
For example
&lt;html&gt;&lt;head&gt;&lt;base href="bar" target="_blank"&gt;&lt;/head&gt;
&lt;body&gt;


>>> print(tc("Try<pre>rm -r /</pre>and you might regret."))
Try rm -r / and you might regret.


Some edge cases
===============

>>> print(tc("<cool>"))
<span></span>

>>> print(tc("<p></p>"))
<BLANKLINE>

>>> print(tc(""))
<BLANKLINE>

>>> print(tc(" "))
<BLANKLINE>


A surprising result:

>>> print(tc("<<<cool>>>"))
&lt;&lt;<span>&amp;gt;&amp;gt;</span>
