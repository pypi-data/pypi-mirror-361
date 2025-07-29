.. _dev.kids:

===============
Python for kids
===============

This section is for young future Lino developers. You'll probably need somebody
to help you with getting started.


How to install Python on a Debian-based Linux::

  $ sudo apt-get install python3 python3-tk idle3


Introduction 1 (using Turtle)
=============================

- Download the :srcref_book:`turtle1.py <docs/dev/newbies/turtle1.py>` script
  and  play with it: Try to modify it and discover what happens.

- More free games in Turtle : https://www.grantjenks.com/docs/freegames/

- Have a look at `the official turtle docs
  <https://docs.python.org/3/library/turtle.html>`__ but don't be scared if you
  do not understand much (these docs are not written for real beginners like
  you).

Introduction 2 (using tkinter)
==============================

- A "Hello world" program using tkinter: :srcref_book:`docs/dev/newbies/gui1.py`

  This uses the "grid" layout method. The widgets are arranged by placing them in a cell of the grid.
  The button spans over two cells. Numbering starts with 0 and in the top left corner.

  +------+------+------+
  |      | col0 | col1 |
  +------+------+------+
  | row0 |  L1  |  E1  |
  +------+------+------+
  | row1 |   B         |
  +------+------+------+

- The "number guessing game" using tkinter:
  :srcref_book:`docs/dev/newbies/gui2.py`. Ideas for exercises: add a counter
  and a timer so that the winner knows how many guesses and how many seconds
  they needed.

- See also `the official tkinter docs
  <https://docs.python.org/3.3/library/tkinter.html>`__ and Frederik Lundh's
  `Comprehensive list of events
  <https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm>`__
  and http://www.tutorialspoint.com/python/python_gui_programming.htm

Dive into the language
=======================

After the introduction we invite you to follow the `Python tutorial at w3schools
<https://www.w3schools.com/python/default.asp>`__. Read the texts and play with
the code examples.

To open the "Command Line" on a Windows PC, you click the Windows button (in the
lower left corner) and type "cmd" in the search field.

Continue with other `learning resources </dev/newbies/learning>`__.
