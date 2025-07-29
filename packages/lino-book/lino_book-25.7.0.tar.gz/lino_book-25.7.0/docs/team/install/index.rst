===========================================
[obsolete] Set up a contributor environment
===========================================

After having :doc:`installed a developer environment </dev/install/index>`, you
may opt to "upgrade" into a "contributor environment" before actually diving
into Lino.

No longer used:

  contributor environment

    An extended :term:`developer environment` suitable for developers who plan
    to potentially contribute to the :ref:`Lino framework <lf>`.  A bit more
    work to install, but more future-proof.

The main new thing as a contributor is that you have a local clone of each Lino
code repository because you are going to do local modifications and submit pull
requests.  Getlino does the work of cloning and installing them as editable
(with `pip install -e`) into your virtualenv.

.. highlight:: console

Run getlino to clone Lino repositories
======================================

We are going to throw away your developer virtualenv and replace it by a new
one::

  $ mv ~/lino/env ~/lino/old_env
  $ python3 -m venv ~/lino/env
  $ source ~/lino/env/bin/activate
  $ pip install -U pip setuptools

Note that after moving a virtualenv to another directory you cannot use it
anymore. Python virtualenvs are not designed to support renaming.  But you may
rename it back to its old name in case you want to go back.

You are now in a new virgin Python virtualenv.  You can say :cmd:`pip freeze` to
verify.

Note that this virgin virtualenv is now your :term:`default environment` because
you created it under the same location as your first virtualenv.

Before going on you should delete the getlino configuration file that was
created when :ref:`installing your Lino developer environment <dev.install>`::

  $ rm ~/.getlino.conf
  $ sudo rm /etc/getlino/getlino.conf
