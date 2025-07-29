.. doctest docs/topics/utils.rst

==============
Lino utilities
==============

We have :mod:`lino.core.utils` and :mod:`lino.utils`. The latter is
theoretically for things that don't require Django.

.. contents::
   :depth: 1
   :local:

.. currentmodule:: lino.utils

Import and setup execution context for demonstration purposes.

>>> from lino import startup
>>> startup('lino.projects.std.settings_test')
>>> from lino.utils import *
>>> from pprint import pprint

Nested dictionaries
===================

Using :class:`AttrDict` for managing nested dictionary like objects:

>>> a = AttrDict()
>>> a.define('foo', 1)
>>> a.define('bar', 'baz', 2)
>>> a == {"bar": {"baz": 2}, "foo": 1}
True
>>> print(a.foo)
1
>>> print(a.bar.baz)
2
>>> print(a.resolve('bar.baz'))
2
>>> print(a.bar)
{'baz': 2}
>>> pprint(a)
{'bar': {'baz': 2}, 'foo': 1}

You can set an existing attribute directly:

>>> a.foo = 3
>>> pprint(a)
{'bar': {'baz': 2}, 'foo': 3}

Also nested attributes:

>>> a.bar.baz = 4
>>> pprint(a)
{'bar': {'baz': 4}, 'foo': 3}

But you may not define new attributes this way:

>>> a.newattr = 3
Traceback (most recent call last):
...
AttributeError: AttrDict instance has no key 'newattr' (keys are foo, bar)


Inline If
=========

Given three arguments to the :func:`iif`, where the first argument is a
condition, returns the second argument if the condition holds otherwise returns
the second argument.

Examples:

>>> print("Hello, %s world!" % iif(1+1==2, "real", "imaginary"))
Hello, real world!
>>> iif(True, "true")
'true'
>>> iif(False, "true")


Join words
==========

Usage example of the function :func:`join_words`:

>>> print(join_words('This','is','a','test'))
This is a test

>>> print(join_words('This','is','','another','test'))
This is another test

>>> print(join_words(None, None, None, 'Third', 'test'))
Third test


Making summaries
================

The :class:`SumCollector` class is used for managing sums of values over some
attribute.

Usage examples:

>>> sc = SumCollector()
>>> sc.collect("a", 12)
>>> sc.collect("b", 23)
>>> sc.collect("a", 34)

>>> sc #doctest: +SKIP
OrderedDict({'a': 46, 'b': 23})
>>> print("{"+', '.join([f"{k}: {v}" for k, v in sc.items()])+"}")
{a: 46, b: 23}

We used a little hack to represent `sc` so that our doctest passes on Python
3.12.3 and 3.12.9, see https://github.com/python/cpython/issues/101446


>>> sc = SumCollector()
>>> sc.collect("a", 12)
>>> sc.collect("a", None)
>>> sc.collect("a", 5)
>>> sc.a
17

>>> from lino.utils.quantities import Duration
>>> sc = SumCollector()
>>> sc.collect("a", Duration("0:30"))
>>> sc.collect("a", Duration("0:35"))
>>> sc.collect("b", Duration("0:00"))
>>> sc.a
Duration('1:05')
>>> sc.b
Duration('0:00')

Working with Chooser
====================

Following examples illustrates the usages of re.pattern (regular expression
patterns) `choosers.GFK_HACK` to extract useful information about a
:mod:`lino.utils.choosers` choice from a javascript action tag created by lino:

>>> import json
>>> from lino.utils.choosers import GFK_HACK
>>> s = ('<a href="javascript:Lino.pcsw.Clients.detail.run(' +
... 'null,{ &quot;record_id&quot;: 116 })">BASTIAENSEN Laurent (116)</a>')
>>> print(json.dumps(GFK_HACK.match(s).groups()))
["pcsw.Clients", "116"]

>>> s = ('<a href="javascript:Lino.cal.Guests.detail.run(' +
... 'null,{ &quot;record_id&quot;: 6 })">Gast #6 ("Termin #51")</a>')
>>> print(json.dumps(GFK_HACK.match(s).groups()))
["cal.Guests", "6"]


Analyzing a python package
==========================

.. currentmodule:: lino.utils.code

.. function:: codefiles_imported(pattern='*')

    Yield a list of the source files corresponding to the currently
    imported modules that match the given pattern

.. function:: codefiles(module_name)

    Yield a list of the source files of the specified module or package.

    This inspects the file system and yields all source files found, including
    those in subdirectories. It does not import them all.

.. function:: codetime(*packages)

    Return the modification time of the youngest source code in the specified
    packages.

    Used e.g. by :mod:`lino.modlib.extjs` to avoid generating .js files if not
    necessary.

    Inspired by the code_changed() function in `django.utils.autoreload`.



.. function:: analyze_rst(*packages)

  Return a statical description of the given packages in reSTructuredText.

>>> from lino.utils.code import analyze_rst
>>> print(analyze_rst('lino', 'lino_xl', 'lino_noi'))
... #doctest: +SKIP
========== ============ =========== =============== =============
 name       code lines   doc lines   comment lines   total lines
---------- ------------ ----------- --------------- -------------
 lino       38k          22k         9k              84k
 lino_xl    42k          13k         10k             77k
 lino_noi   1.0k         0.4k        0.7k            3k
 total      81k          35k         20k             164k
========== ============ =========== =============== =============
<BLANKLINE>

Above snippet is not tested because the numbers change often.

This function is used to generate our
`Statistics page <https://www.lino-framework.org/stats.html>`__.


Using the Cycler
================

Usage examples of the :class:`cycler.Cycler` class, when instantiating, it takes
an iterable or some arbitrary values (while latter, the :class:`cycler.Cycler`
converts them into an iterable) then iterates over them in loops:

>>> def myfunc():
...     yield "a"
...     yield "b"
...     yield "c"

>>> c = Cycler(myfunc())
>>> s = ""
>>> for i in range(10):
...     s += c.pop()
>>> print(s)
abcabcabca


When you print a :class:`Cycler` instance, it reports its current position and
the number of loops it has done so far. This can help e.g. for  understanding
what's going on in a fixture.

>>> c
Cycler(1 of 3 in loop 4)


An empty Cycler or a Cycler on an empty list will endlessly pop None values:

>>> c = Cycler()
>>> print(c.pop(), c.pop(), c.pop())
None None None

>>> c = Cycler([])
>>> print(c.pop(), c.pop(), c.pop())
None None None

>>> c = Cycler(None)
>>> print(c.pop(), c.pop(), c.pop())
None None None




Using Counter in jinja
======================

Setting up a jinja environment:

  You can add the `Counter` class either to your local context or to the
  `global namespace
  <http://jinja.pocoo.org/docs/dev/api/#global-namespace>`__.

  >>> from jinja2 import Environment
  >>> from lino.utils.jinja import *
  >>> env = Environment()
  >>> env.globals.update(Counter=Counter)


Basic usage in a template:

  Using the `Counter` in your template is easy: You instantiate a
  template variable of type :class:`Counter`, and then call that counter
  each time you want a new number.  For example:

  >>> s = """
  ... {%- set art = Counter() -%}
  ... Easy as {{art()}}, {{art()}} and {{art()}}!
  ... """

  Here is how this template will render :

  >>> print(env.from_string(s).render())
  Easy as 1, 2 and 3!


Counter parameters:

  When defining your counter, you can set optional parameters.

  >>> s = """
  ... {%- set art = Counter(start=17, step=2) -%}
  ... A funny counter: {{art()}}, {{art()}} and {{art()}}!
  ... """
  >>> print(env.from_string(s).render())
  A funny counter: 19, 21 and 23!


Resetting a counter:

  When calling your counter, you can pass optional parameters. One of
  them is `value`, which you can use to restart numbering, or to start
  numbering at some arbitrary place:

  >>> s = """
  ... {%- set art = Counter() -%}
  ... First use: {{art()}}, {{art()}} and {{art()}}
  ... Reset: {{art(value=1)}}, {{art()}} and {{art()}}
  ... Arbitrary start: {{art(value=10)}}, {{art()}} and {{art()}}
  ... """
  >>> print(env.from_string(s).render())
  First use: 1, 2 and 3
  Reset: 1, 2 and 3
  Arbitrary start: 10, 11 and 12


Nested counters:

  Counters can have another counter as parent. When a parent increases,
  all children are automatically reset to their start value.


  >>> s = """
  ... {%- set art = Counter() -%}
  ... {%- set par = Counter(art) -%}
  ... = Article {{art()}}
  ... == # {{par()}}
  ... == # {{par()}}
  ... = Article {{art()}}
  ... == # {{par()}}
  ... == # {{par()}}
  ... == # {{par()}}
  ... Article {{art()}}.
  ... == # {{par()}}
  ... """
  >>> print(env.from_string(s).render())
  = Article 1
  == # 1
  == # 2
  = Article 2
  == # 1
  == # 2
  == # 3
  Article 3.
  == # 1

Generating JavaScript from python
=================================

Some examples of generating JavaScript from python using the
:mod:`lino.utils.jsgen` module:

>>> from lino.utils.jsgen import *
>>> class TextField(Component):
...    declare_type = DECLARE_VAR
>>> class Panel(Component):
...    declare_type = DECLARE_VAR
>>> fld1 = TextField(fieldLabel="Field 1", name='fld1', xtype='textfield')
>>> fld2 = TextField(fieldLabel="Field 2", name='fld2', xtype='textfield')
>>> fld3 = TextField(fieldLabel="Field 3", name='fld3', xtype='textfield')
>>> p1 = Panel(title="Panel", name='p1', xtype='panel', items=[fld2, fld3])
>>> main = Component(title="Main", name='main', xtype='form', items=[fld1, p1])
>>> d = dict(main=main, wc=[1, 2, 3])

>>> for ln in declare_vars(d):
...   print(ln)
var fld13 = { "fieldLabel": "Field 1", "xtype": "textfield" };
var fld24 = { "fieldLabel": "Field 2", "xtype": "textfield" };
var fld35 = { "fieldLabel": "Field 3", "xtype": "textfield" };
var p16 = { "items": [ fld24, fld35 ], "title": "Panel", "xtype": "panel" };


>>> print(py2js(d))
{ "main": { "items": [ fld13, p16 ], "title": "Main", "xtype": "form" }, "wc": [ 1, 2, 3 ] }


Checking shell command output
=============================

The :mod:`lino.utils.mdbtools` provides a function
:func:`mdbtools.check_output` either from the python package
`subprocess <https://docs.python.org/3/library/subprocess.html>`_ or it's own defined
function (in case `check_output` is not available in `subprocess`).

Here are some examples of using :func:`check_output`:

>>> from lino.utils.mdbtools import check_output, STDOUT
>>> check_output(["ls", "-l", "/dev/null"])
... #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
b'crw-rw-rw- 1 root root 1, ... /dev/null\n'

The stdout argument is not allowed as it is used internally.
To capture standard error in the result, use stderr=STDOUT.

>>> check_output(["/bin/sh", "-c",
...               "ls -l non_existent_file ; exit 0"],
...              stderr=STDOUT)
b"ls: cannot access 'non_existent_file': No such file or directory\n"


Reading .ods files
==================

The following code reads a file :srcref:`odsreader_sample.ods` and prints a line
of text for each row of data leveraging the class :class:`odsreader.OdsReader`:

>>> from lino.utils.odsreader import OdsReader, srcpath
>>> class Sample(OdsReader):
...     filename = srcpath('odsreader_sample.ods')
...     headers = ["N°", "Prénom", "Last name", "Country", "City", "Language"]
...     column_names = 'no first_name last_name country city language'.split()
...
>>> for row in Sample().rows():
...     print( "%(first_name)s %(last_name)s from %(city)s" % row)
Rudi Rutté from Eupen
Romain Raffault from Liège
Rando Roosi from Tallinn
Rik Rozenbos from Antwerpen
Robin Rood from London

(Note: these are fictive person names from :mod:`lino.modlib.users.fixtures.demo`).


Working with ranges
===================

The following examples demonstrates the usage of some functions provided by the
:mod:`lino.utils.ranges` module.

Using the :func:`ranges.constrain` function to constrain a range into some given
value:

>>> from lino.utils.ranges import constrain, encompass, overlap
>>> constrain(-1, 2, 5)
2
>>> constrain(1, 2, 5)
2
>>> constrain(0, 2, 5)
2
>>> constrain(2, 2, 5)
2
>>> constrain(3, 2, 5)
3
>>> constrain(5, 2, 5)
5
>>> constrain(6, 2, 5)
5
>>> constrain(10, 2, 5)
5

Using the :func:`ranges.encompass` function to check if a given ranges
encompasses another:

>>> encompass((1, 4), (2, 3))
True
>>> encompass((1, 3), (2, 4))
False
>>> encompass((None, None), (1, 4))
True
>>> encompass((1, None), (1, 4))
True
>>> encompass((2, None), (1, None))
False
>>> encompass((1, None), (2, None))
True
>>> encompass((1, 4), (1, 4))
True
>>> encompass((1, 2), (1, None))
False

Using the :func:`ranges.overlap` function to check if two ranges overlap
eachother:

>>> overlap(1,2,3,4)
False
>>> overlap(3,4,1,2)
False
>>> overlap(1,3,2,4)
True
>>> overlap(2,4,1,3)
True
>>> overlap(1,4,2,3)
True
>>> overlap(2,3,1,4)
True


>>> overlap(1,None,3,4)
True
>>> overlap(3,4,1,None)
True


>>> overlap(1,2,3,None)
False
>>> overlap(3,None,1,2)
False

>>> overlap(None,2,3,None)
False
>>> overlap(3,None,None,2)
False

>>> overlap(1,3,2,None)
True

Touching but non-overlapping examples:

>>> overlap(1,2,2,3)
False
>>> overlap(2,3,1,2)
False


Converting HTML to text
=======================

>>> from lino.utils.html import html2text

>>> html2text("<p>Hello, <em>world!</em></p>")
'Hello, _world!_\n\n'

The following output changed 20240226, :func:`html2text` now removes the blank
space after ``<strong>``:

>>> html2text("<p>Lorem ipsum <strong>dolor sit amet</strong>, consectetur "
... "adipiscing elit.</p>")
'Lorem ipsum **dolor sit amet** , consectetur adipiscing elit.\n\n'



The ``nextref`` function
========================

The :func:`lino.utils.nextref` function is e.g. used by
:meth:`lino.mixins.ref.Referrable.get_next_row`.

>>> from lino.utils import nextref

>>> nextref("1A")
'2A'
>>> nextref("123 foo")
'124 foo'
>>> nextref("123")
'124'
>>> nextref("1-A")
'2-A'
>>> nextref("1-123")
'2-123'

Return `None` when the string contains no digits:

>>> nextref("A")
>>> nextref("")
