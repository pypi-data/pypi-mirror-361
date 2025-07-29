.. doctest docs/topics/formatting.rst

================
About formatting
================

.. contents::
   :depth: 1
   :local:

.. currentmodule:: lino.utils

Import execution context for demonstration purposes.

>>> from lino.utils import *

Miscellanous string conversion
==============================

Conversion between str and hex examples using :func:`str2hex` and
:func:`hex2str` functions:

>>> str2hex('-L')
'2d4c'

>>> hex2str('2d4c')
'-L'

>>> hex2str('')
''
>>> str2hex('')
''

The following examples demonstrates the use of the functions :func:`camelize`
and :func:`uncamel`:

>>> camelize("ABC DEF")
'Abc Def'
>>> camelize("ABC def")
'Abc def'
>>> camelize("eID")
'eID'
>>> uncamel('EventsByClient')
'events_by_client'
>>> uncamel('Events')
'events'
>>> uncamel('HTTPResponseCodeXYZ')
'http_response_code_xyz'


Formatting currencies
=====================

The following examples demonstrate the use of the function :func:`moneyfmt`
which converts a decimal value into money format:

>>> d = Decimal('-1234567.8901')
>>> print(moneyfmt(d, curr='$'))
-$1,234,567.89
>>> print(moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-'))
1.234.568-
>>> print(moneyfmt(d, curr='$', neg='(', trailneg=')'))
($1,234,567.89)
>>> print(moneyfmt(Decimal(123456789), sep=' '))
123 456 789.00
>>> print(moneyfmt(Decimal('-0.02'), neg='<', trailneg='>'))
<0.02>


Converting HTML to odf
======================

This section provides some examples of using the module
:mod:`lino.utils.html2odf` to convert HTML into odf document and also discusses
about some incapabilities of the module.

Examples:

>>> from lino.utils.html2odf import *
>>> from etgen.html import E, tostring
>>> def test(e):
...     print (tostring(e))
...     print (toxml(html2odf(e)))
>>> test(E.p("This is a ", E.b("first"), " test."))
... #doctest: +NORMALIZE_WHITESPACE
<p>This is a <b>first</b> test.</p>
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">This
is a <text:span text:style-name="Strong Emphasis">first</text:span>
test.</text:p>

>>> test(E.p(E.b("This")," is another test."))
... #doctest: +NORMALIZE_WHITESPACE
<p><b>This</b> is another test.</p>
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><text:span
text:style-name="Strong Emphasis">This</text:span> is another test.</text:p>

>>> test(E.p(E.strong("This")," is another test."))
... #doctest: +NORMALIZE_WHITESPACE
<p><strong>This</strong> is another test.</p>
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><text:span
text:style-name="Strong Emphasis">This</text:span> is another test.</text:p>

>>> test(E.p(E.i("This")," is another test."))
... #doctest: +NORMALIZE_WHITESPACE
<p><i>This</i> is another test.</p>
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><text:span
text:style-name="Emphasis">This</text:span> is another test.</text:p>

>>> test(E.td(E.p("This is another test.")))
... #doctest: +NORMALIZE_WHITESPACE
<td><p>This is another test.</p></td>
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">This
is another test.</text:p>

>>> test(E.td(E.p(E.b("This"), " is another test.")))
... #doctest: +NORMALIZE_WHITESPACE
<td><p><b>This</b> is another test.</p></td>
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><text:span
text:style-name="Strong Emphasis">This</text:span> is another test.</text:p>

>>> test(E.ul(E.li("First item"),E.li("Second item")))
... #doctest: +NORMALIZE_WHITESPACE
<ul><li>First item</li><li>Second item</li></ul>
<text:list xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
text:style-name="podBulletedList"><text:list-item><text:p
text:style-name="podBulletItem">First item</text:p></text:list-item><text:list-item><text:p
text:style-name="podBulletItem">Second item</text:p></text:list-item></text:list>

N.B.: the above chunk is obviously not correct since Writer doesn't display it.
(How can I debug a generated odt file?
I mean if my content.xml is syntactically valid but Writer ...)
Idea: validate it against the ODF specification using lxml

Here is another HTML fragment which doesn't yield a valid result:

>>> from lxml import etree
>>> html = '<td><div><p><b>Bold</b></p></div></td>'
>>> print(toxml(html2odf(etree.fromstring(html))))
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"/>


:func:`html2odf.html2odf` converts bold text to a span with a style named
"Strong Emphasis". That's currently a hard-coded name, and the caller
must make sure that a style of that name is defined in the document.

The text formats `<i>` and `<em>` are converted to a style "Emphasis".

Edge case:

>>> print (toxml(html2odf("Plain string")))
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Plain string</text:p>

>>> print (toxml(html2odf(u"Ein schöner Text")))
<text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">Ein schöner Text</text:p>


The following is an example for :ticket:`788`. Conversion fails if a
sequence of paragraph-level items are grouped using a div:

>>> test(E.div(E.p("Two numbered items:"),
...    E.ol(E.li("first"), E.li("second"))))
... #doctest: +NORMALIZE_WHITESPACE +IGNORE_EXCEPTION_DETAIL +ELLIPSIS
Traceback (most recent call last):
...
IllegalText: The <text:section> element does not allow text


>>> from lxml import etree
>>> test(etree.fromstring('<ul type="disc"><li>First</li><li>Second</li></ul>'))
<ul type="disc"><li>First</li><li>Second</li></ul>
<text:list xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="podBulletedList"><text:list-item><text:p text:style-name="podBulletItem">First</text:p></text:list-item><text:list-item><text:p text:style-name="podBulletItem">Second</text:p></text:list-item></text:list>


>>> test(E.p(E.dl(E.dt("Foo"), E.dl("A foobar without bar."))))
Traceback (most recent call last):
...
NotImplementedError: <dl> inside <text:p>


Converting HTML into XHTML
==========================

The following examples demonstrates the use of the function
:func:`html2xhtml.html2xhtml` to convert HTML document into XHTML document:

>>> from lino.utils.html2xhtml import *
>>> print(html2xhtml('''\
... <p>Hello,&nbsp;world!<br>Again I say: Hello,&nbsp;world!</p>
... <img src="foo.org" alt="Foo">'''))
... #doctest: +NORMALIZE_WHITESPACE -SKIP
<p>Hello,&nbsp;world!<br />
Again I say: Hello,&nbsp;world!</p>
<img src="foo.org" alt="Foo" />

Above test is currently skipped because tidylib output can slightly
differ (``alt="Foo">`` versus ``alt="Foo" >``) depending on the
installed version of tidylib.


>>> html = '''\
... <p style="font-family: &quot;Verdana&quot;;">Verdana</p>'''
>>> print(html2xhtml(html))
<p style="font-family: &quot;Verdana&quot;;">Verdana</p>

>>> print(html2xhtml('A &amp; B'))
A &amp; B

>>> print(html2xhtml('a &lt; b'))
a &lt; b

A `<div>` inside a `<span>` is not valid XHTML.
Neither is a `<li>` inside a `<strong>`.

But how to convert it?  Inline tags must be "temporarily" closed
before and reopended after a block element.

>>> print(html2xhtml('<p>foo<span class="c">bar<div> oops </div>baz</span>bam</p>'))
<p>foo<span class="c">bar</span></p>
<div><span class="c">oops</span></div>
<span class="c">baz</span>bam

>>> print(html2xhtml('''<strong><ul><em><li>Foo</li></em><li>Bar</li></ul></strong>'''))
<ul>
<li><strong><em>Foo</em></strong></li>
<li><strong>Bar</strong></li>
</ul>

In HTML it was tolerated to not end certain tags.
For example, a string "<p>foo<p>bar<p>baz" converts
to "<p>foo</p><p>bar</p><p>baz</p>".

>>> print(html2xhtml('<p>foo<p>bar<p>baz'))
<p>foo</p>
<p>bar</p>
<p>baz</p>
