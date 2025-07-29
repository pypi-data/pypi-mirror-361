.. _dev.tours:

================
Screenshot tours
================

A **screenshot tour** is a virtual tour of a Lino site using `Selenium
<https://www.selenium.dev/documentation/en/>`__ to look around and watch into
every corner, taking screenshots on the go. Before leaving, the tour also writes
an `index.rst` file that lists the screenshot images.

Screenshot tours could become an integral part of the Lino test suite because
generating them fails when something at the web interface is broken.  They are
not yet run automatically because things seem to be more complicated than
expected.  How to test whether all Ajax requests are finished?  How to find the
elements? At the moment it seems that these tests depend much on the version of
Selenium or the browser driver. Until these problems are fixed, we run each tour
manually as described below.

Every screenshot tour is defined in a :xfile:`maketour.py` file.

Screenshot tours are done using the :mod:`lino.api.selenium` module.

Usage example::

  $ go noi1e
  $ python manage.py run maketour.py

The result of above example is published as :ref:`noi1e.tour`.

.. xfile:: maketour.py

    By convention, the default tour of a demo project is in a file named
    :xfile:`maketour.py`.

Implementation note: The tricky part was to figure out how to start a
:manage:`runserver` in background, run some arbitrary code and then terminate
the server proces. We create a :class:`subprocess.Popen` object that will
execute :manage:`runserver`, then we must call :meth:`communicate` to let it
live (but we do this in a thread in background), and finally we call
:meth:`terminate` to let it die in peace.

Running a :xfile:`maketour.py` script usually leaves a file
:file:`geckodriver.log` which might contain interesting information.

TODO: compare the generated snapshots with those of a "reviewed" result from an
earlier version.  Use `PIL.ImageChops.difference` (see `here
<https://stackoverflow.com/questions/5224433/python-pil-screenshot-comparing>`__
for ideas).  Generate a second page `diffs.rst` for every tour, to report these
differences so that a human reviewer can decide whether the new result is
acceptable or not.
