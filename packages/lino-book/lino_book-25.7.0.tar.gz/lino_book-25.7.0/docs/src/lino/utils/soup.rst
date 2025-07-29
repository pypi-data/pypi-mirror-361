.. doctest docs/src/lino/utils/soup.rst

================================
``lino.utils.soup``
================================


.. module:: lino.utils.soup

The ``lino.utils.soup`` module defines two functions :func:`sanitize` and
:func:`truncate_comment`, which are both done with the help of `BeautifulSoup
<https://beautiful-soup-4.readthedocs.io>`__.


.. contents::
    :depth: 1
    :local:


.. include:: /../docs/shared/include/tested.rst


The ``sanitize()`` function
===========================

.. function:: sanitize

  Parse the given HTML markup `html` and return a sanitized version of if.


.. data:: ALLOWED_TAGS

  A list of tag names that are to *remain* in sanitized HTML.

  >>> from lino.utils.soup import ALLOWED_TAGS
  >>> from pprint import pprint
  >>> pprint(ALLOWED_TAGS)  #doctest: +NORMALIZE_WHITESPACE
  frozenset({'a', 'b', 'br', 'def', 'div', 'em', 'i', 'img', 'li', 'ol', 'p',
  'pre', 'span', 'strong', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead',
  'tr', 'ul'})

.. data:: ALLOWED_ATTRIBUTES

  A dictionary mapping tagnames to a list of attribute names that are to *remain*
  in sanitized HTML .

  >>> from lino.utils.soup import ALLOWED_ATTRIBUTES
  >>> pprint(ALLOWED_ATTRIBUTES, sort_dicts=True)
  ... #doctest: +SKIP
  {'a': {'href', 'title'},
   'abbr': {'title'},
   'acronym': {'title'},
   'p': {'align'},
   'span': {'class',
            'contenteditable',
            'data-denotation-char',
            'data-index',
            'data-link',
            'data-title',
            'data-value'}}

  The above snippet is skipped because :func:`pprint` displays the content of
  sets in arbitrary ordering even when `sort_dicts` is set to `True`.


Examples
--------

Here are some tests to verify whether :func:`sanitize` does what we want.

>>> from lino.utils.soup import sanitize

Sanitizing "normalizes" the html content:

>>> print(sanitize("<p>One paragraph<p>Another paragraph"))
<p>One paragraph</p><p>Another paragraph</p>

>>> print(sanitize("<pre>"))
<pre></pre>

>>> print(sanitize("<pre>\n</pre>"))
<pre>
</pre>

When content is a single ``<p>`` tag, sanitizing NO LONGER unwraps it:

>>> print(sanitize("<p>One line<br>Another line"))
<p>One line<br/>Another line</p>

>>> print(sanitize('<p align="center">One<br>two'))
<p align="center">One<br/>two</p>

Plain text becomes a single paragraph and gets wrapped into a ``<p>`` tag:

>>> print(sanitize("Foo"))
<p>Foo</p>

Characters with special meaning get escaped:

>>> print(sanitize("Foo & Bar, Inc."))
<p>Foo &amp; Bar, Inc.</p>

>>> print(sanitize("When a < b and b < c then a < c"))
<p>When a &lt; b and b &lt; c then a &lt; c</p>

But valid formatting tags are recognized and preserved:

>>> print(sanitize("When <i>a</i> <b>and</b> <i>b</i> then <i>c</i>."))
<p>When <i>a</i> <b>and</b> <i>b</i> then <i>c</i>.</p>


Here is a surprising behaviour, which shows that you still should better escape
yourself

>>> print(sanitize("About the <p> tag"))
<p>About the </p><p> tag</p>

The output is UTF-8 encoded, so we don't need to escape umlauts and accents.

>>> print(sanitize("Ein süßes Kätzchen"))
<p>Ein süßes Kätzchen</p>

>>> print(sanitize("Monsieur l'Évêque loge à l'hôtel"))
<p>Monsieur l'Évêque loge à l'hôtel</p>

Even if you escape umlauts, sanitizing will render them as UTF-8. We are in the
21st century after all:

>>> print(sanitize("Ein s&uuml;&szlig;es K&auml;tzchen"))
<p>Ein süßes Kätzchen</p>


An empty string remains an empty string:

>>> sanitize("")
''


More examples
-------------

>>> print(sanitize("<pre></pre>"))
<pre></pre>

>>> print(sanitize("<p>Foo</p>"))
<p>Foo</p>

>>> print(sanitize("One<br>two"))
<p>One<br/>two</p>

>>> print(sanitize("One<br>two</p>"))
<p>One<br/>two</p>


>>> print(sanitize("<p></p>"))
<p></p>

>>> print(sanitize(""))
<BLANKLINE>


>>> content = """
... No tag at beginning of text.
... bla bLTaQSTyI80t2t8l
... foo bar.
... And here is some <b>bold</b> text.
...
... """
>>> print(sanitize(content))
<p>No tag at beginning of text.
bla bLTaQSTyI80t2t8l
foo bar.
And here is some <b>bold</b> text.</p>


>>> content = """
... <p align="right">First paragraph</p>
... <p onclick="kill()">Second paragraph</p>
... """
>>> print(sanitize(content))
<p align="right">First paragraph</p>
<p>Second paragraph</p>


>>> content = """
... <p>Here is a code example:</p>
... <p class="ql-code-block">int i = 2;</p>
... <p>More explanations</p>
... """
>>> print(sanitize(content))
<p>Here is a code example:</p>
<p class="ql-code-block">int i = 2;</p>
<p>More explanations</p>


>>> content = """
... <!DOCTYPE html>
... <html>
...   <head>
...     <meta http-equiv="content-type" content="text/html; charset=UTF-8">
...     <title>Baby</title>
...   </head>
...   <body>
...     This is a descriptive text with <b>some</b> formatting.<br>
...     <br>
...     Here is a second paragraph.<br>
...     <br>
...   </body>
... </html>
... """

>>> print(sanitize(content))
This is a descriptive text with <b>some</b> formatting.<br/>
<br/>
    Here is a second paragraph.<br/>
<br/>



The ``truncate_comment()`` function
===================================

.. function:: truncate_comment(htmlstr, max_length=300)

    Return a single paragraph with a maximum number of visible chars.

>>> from lino.utils.soup import truncate_comment as tc


Examples
--------

>>> pasted = """<h1 style="color: #5e9ca0;">Styled comment
... <span style="color: #2b2301;">pasted from word!</span> </h1>"""

>>> print(tc(pasted))
... #doctest: +NORMALIZE_WHITESPACE
<span>Styled comment
<span style="color: #2b2301;">pasted from word!</span> </span>


>>> print(tc(pasted, 17))
... #doctest: +NORMALIZE_WHITESPACE
<span>Styled comment
<span style="color: #2b2301;">pa...</span> </span>

The first image remains but we enforce our style.

>>> from lino.utils.soup import SHORT_PREVIEW_IMAGE_HEIGHT
>>> SHORT_PREVIEW_IMAGE_HEIGHT
'8em'

>>> print(tc('<img src="foo" alt="bar"/></p>'))
<img alt="bar" src="foo" style="float:right;height:8em"/>

>>> print(tc('<IMG SRC="foo" ALT="bar"/>'))
<img alt="bar" src="foo" style="float:right;height:8em"/>

>>> two_images = """<p>First <img src="a.jpg"/> and <img src="b.jpg"/>.</p>"""
>>> tc(two_images)
'First <img src="a.jpg" style="float:right;height:8em"/> and ⌧.'


Paragraph tags are replaced by a whitespace while inline tags remain:

>>> print(tc("Try<pre>rm -r /</pre>and you might regret."))  #doctest: +SKIP
Try rm -r / and you might regret.

>>> print(tc("Try <i>rm -r /</i>and you might regret."))
Try <i>rm -r /</i>and you might regret.

Unknown tags get sanitized into a `<span>`:

>>> print(tc("Try <bad>rm -r /</bad>and you might regret."))
Try <span>rm -r /</span>and you might regret.


>>> print(tc('<p>A short paragraph</p><p><ul><li>first</li><li>second</li></ul></p>'))
A short paragraph first second

>>> print(tc('Some plain text.'))
Some plain text.

>>> print(tc('Two paragraphs of plain text.\n\n\nHere is the second paragraph.'))
Two paragraphs of plain text.
<BLANKLINE>
<BLANKLINE>
Here is the second paragraph.



Truncation
----------

>>> bold_and_italic = "<p>A <b>bold</b> and <i>italic</i> thing."
>>> lorem_ipsum = '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>'

>>> print(tc(bold_and_italic))
A <b>bold</b> and <i>italic</i> thing.

>>> print(tc(bold_and_italic, 5))
A <b>bol...</b>

>>> print(tc(bold_and_italic, 14))
A <b>bold</b> and <i>ita...</i>

The two following examples are cut at exactly the same place:

>>> print(tc(lorem_ipsum, 30))
Lorem ipsum dolor sit amet, co...

>>> print(tc('<p>Lorem <b>ipsum</b> dolor sit amet, consectetur adipiscing elit.</p>', 30))
Lorem <b>ipsum</b> dolor sit amet, co...

>>> print(tc('<p>Lorem <b>ipsum</b> dolor sit amet, consectetur adipiscing elit.</p>', 10))
Lorem <b>ipsu...</b>

>>> print(tc('<p>Lorem ipsum dolor sit amet</p><p>consectetur adipiscing elit.</p>', 30))
Lorem ipsum dolor sit amet cons...

Lorem ipsum dolor sit amet
<BLANKLINE>
cons...

>>> tc("<p>A plain paragraph with more than 20 characters.</p>", 20)
'A plain paragraph wi...'

Multiple paragraphs are summarized:

>>> tc("<p>aaaa.</p><p>bbbb.</p><p>cccc.</p><p>dddd.</p><p>eeee.</p>", 20)
'aaaa. bbbb. cccc. ddd...'

TODO: In above result there is one "d" too much at the end. Why?

>>> tc("<div>{}</div>".format(lorem_ipsum), 20)
'Lorem ipsum dolor si...'


Exploring BeautifulSoup
-----------------------

>>> from bs4 import BeautifulSoup
>>> def walk(ch, indent=0):
...    prefix = " " * indent
...    if hasattr(ch, 'tag'):
...      print(prefix + str(type(ch)) + " " + ch.name + ":")
...      for c in ch.children:
...        walk(c, indent+2)
...    else:
...      print(prefix + str(type(ch)) + " " + repr(ch.string))
...      # print(prefix+repr(ch.string))
>>> soup = BeautifulSoup(bold_and_italic, "html.parser")
>>> walk(soup)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
<class 'bs4.BeautifulSoup'> [document]:
  <class 'bs4.element.Tag'> p:
    <class 'bs4.element.NavigableString'> 'A '
    <class 'bs4.element.Tag'> b:
      <class 'bs4.element.NavigableString'> 'bold'
    <class 'bs4.element.NavigableString'> ' and '
    <class 'bs4.element.Tag'> i:
      <class 'bs4.element.NavigableString'> 'italic'
    <class 'bs4.element.NavigableString'> ' thing.'

>>> soup = BeautifulSoup(lorem_ipsum, "html.parser")
>>> walk(soup)
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
<class 'bs4.BeautifulSoup'> [document]:
  <class 'bs4.element.Tag'> p:
    <class 'bs4.element.NavigableString'> 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'



Further reading
===============

See also :doc:`/topics/truncate` and  :ref:`dg.sanitize.save` and
:doc:`/dev/bleach`.
