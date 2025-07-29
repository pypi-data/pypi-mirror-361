.. _dev.release:

====================
Release Lino to PyPI
====================

Here we go for releasing a new version of Lino to the world. This usually
involves several packages. We usually do such a series of releases when some
:term:`production site` needs an upgrade and hence the list of packages we
release depends on what we need for that site.

.. contents::
   :depth: 2
   :local:


Overview
===========

- We assume that you have `configured your environment <Configure your
  environment>`_.

- Check you have a clean working copy of all projects maintained by
  the Synodalsoft team::

    $ pp git pull

- Check that all test suites are passing and all doc trees are building::

    $ pp inv prep test clean -b bd

- (Currently not used:) For every demo project that has a
  :xfile:`test_restore.py` file in its test suite, run :manage:`makemigdump` and
  add the new version to the :attr:`tested_versions
  <lino.utils.djangotest.RestoreTestCase.tested_versions>` in the
  :xfile:`test_restore.py` file. See :doc:`migtests` for details.

- Decide which packages to release.  In each package you can say :cmd:`git log`
  to decide whether there are relevant changes since the last release to pypi.

- Update the release notes and the changelog in the book.

- For each package you want to release, read `Release a package`_.

.. _dg.howto.release:

Release a package
========================

Repositories with a ``pyproject.toml``
--------------------------------------

- See current version::

    hatch version

- Increase micro, minor or major part of version number ("major" if year has
  changed since last version, "minor" if month has changed, otherwise "micro").
  In case of doubt specify yourself a version number::

    hatch version micro # or minor or major

- Install the new version in your :term:`virtualenv`, remove existing dist
  files, build new ones & check them::

    rm dist/* ; python -m build; twine check dist/* ; pip install -e .

- If everything went well, publish it::

    twine upload dist/*; git ci -am "release to pypi"; git push


Repositories with a ``setup.py``
--------------------------------

- Update the `version` in the :xfile:`setup_info.py` file. See
  :doc:`versioning` for details.

- Create a source tarball and then publish it to PyPI::

    $ inv sdist release -b

- Commit and push the new version number::

    $ git ci -am "release to pypi" && git push



Configure your environment
==========================

Of course you need maintainer's permission on PyPI for the repositories to which
you want to write.

You also need to configure your :xfile:`~/.pypirc` file::

    [distutils]
        index-servers = pypi

    [pypi]
        username = __token__
        password = pypi-SomeLongString

The `twine` software package should be installed on your Linux distro. To check
if you have `twine` installed on your machine, run::

    $ twine --version

If you do not have `twine` installed on your machine, you can install it using
`aptitude` or `snap` package manager (depending on your distro there maybe few
other package managers that indexes `twine`), run the following command to
install it using `aptitude`::

    $ sudo apt install twine
