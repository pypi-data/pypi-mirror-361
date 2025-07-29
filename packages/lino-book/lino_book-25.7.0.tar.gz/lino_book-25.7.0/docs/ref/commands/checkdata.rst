.. doctest docs/ref/commands/checkdata.rst

====================================================================
``checkdata`` : run high-level integrity tests
====================================================================

.. command:: pm checkdata

  Run the data checkers to find :term:`data problems <data problem>`
  and update the table of :term:`data problem messages <data problem message>`.

  If no arguments are given, run all data checkers. Otherwise every positional
  argument is expected to be a model name in the form `app_label.ModelName`, and
  only checkers for these models are being updated.

In other words, this command does the same as if a user would click on
the button with the bell ("Check data") on each database
object for which there are data checkers.

This command is defined by the :mod:`lino.modlib.checkdata` core plugin.

.. include:: /../docs/shared/include/tested.rst

>>> from lino_book.projects.cosi1.startup import *

>>> from atelier.sheller import Sheller
>>> shell = Sheller(settings.SITE.project_dir)

>>> shell("django-admin checkdata --help")  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
usage: django-admin checkdata [-h] [-l] [-f] [-p] [--version] [-v {0,1,2,3}]
                              [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback]
                              [--no-color] [--force-color] [--skip-checks]
                              [checkers ...]
<BLANKLINE>
Update the table of checkdata messages. If no arguments are given, run it on all data
checkers. Otherwise every positional argument is expected to be a model name in the form
`app_label.ModelName`, and only these models are being updated.
<BLANKLINE>
positional arguments:
  checkers              the checkers to run
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -l, --list            Don't check, just show a list of available checkers.
  -f, --fix             Fix any repairable problems.
  -p, --prune           Remove all existing problem messages first.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output,
                        3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main".
                        If this isn't provided, the DJANGO_SETTINGS_MODULE environment
                        variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Display a full stack trace on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.


>>> shell("django-admin checkdata -l")  #doctest: +NORMALIZE_WHITESPACE
=================================== ========================================================
 Wert                                Text
----------------------------------- --------------------------------------------------------
 accounting.VoucherChecker           Check integrity of numbered vouchers
 countries.PlaceChecker              Check data of geographical places
 finan.FinancialVoucherItemChecker   Check for invalid account/partner combination
 memo.PreviewableChecker             Check for previewables needing update
 phones.ContactDetailsOwnerChecker   Check for mismatches between contact details and owner
 printing.CachedPrintableChecker     Check for missing target files
 sepa.BankAccountChecker             Check for partner mismatches in bank accounts
 system.BleachChecker                Find unbleached html content
 uploads.UploadChecker               Check metadata of upload files
 uploads.UploadsFolderChecker        Find orphaned files in uploads folder
 vat.VatColumnsChecker               Check VAT columns configuration
 vat.VatIdChecker                    Validate VAT id from online registry
=================================== ========================================================
