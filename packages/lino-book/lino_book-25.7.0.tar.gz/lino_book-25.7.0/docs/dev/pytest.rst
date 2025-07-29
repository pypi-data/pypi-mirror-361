==============================
Choosing the ``pytest`` runner
==============================

A repository can specify a :envvar:`test_command` setting in its
:xfile:`tasks.py` file. The default value runs :cmd:`python -m unittest discover
-s tests` (unless there is no directory named :file:`tests`, in which case it
does nothing).

In the :ref:`book` repository we use :command:`pytest` instead of the default.
So before saying :cmd:`inv test` in `book` you must install the following Python
packages::

  $ pip install pytest pytest-html pytest-forked pytest-env


We do not use any pytest-specific features in order to remain testable with
other test runners. The only reason for using :command:`pytest` is that its
reporting is more convenient: when a testcase fails, it shows the filename of
the failure immediately, while unittest shows only an ``F`` instead of a dot
(``.``).

We need `pytest-forked <https://pypi.org/project/pytest-forked/>`__ (which adds
the ``--forked`` option) because otherwise pytest would run all doctests in a
single process. They must run in separate subprocesses because you cannot unload
Django settings once they have been loaded.

We do *not* use `pytest-xdist <https://github.com/pytest-dev/pytest-xdist>`__
because each test must run in a subprocess, but we set
``--numprocesses`` to 1 because running multiple tests at the same time
can cause side effects.
