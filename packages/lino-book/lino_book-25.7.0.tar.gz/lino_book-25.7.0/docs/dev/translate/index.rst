.. _dev.translate:

==============================
How to contribute translations
==============================

Here is how you can help translating Lino into your language.

We assume that you have installed a :term:`developer environment`.

You also need to read :doc:`/contrib/legal` before you can start contributing.

.. contents::
   :local:
   :depth: 2



Basic knowledge
---------------

You are going to edit a series of :xfile:`.po` files that are part of the Lino
source code.  Each Lino repository has its own series of :xfile:`.po` files.
Their place is given by the :attr:`locale_dir` setting in the :xfile:`tasks.py`
file  (see :ref:`atelier.prjconf`). Here are some examples:

- :mod:`lino` : lino/locale
- :mod:`lino_xl` : lino_xl/lib/xl/locale
- :mod:`lino_noi` : lino_noi/lib/noi/locale
- :mod:`lino_cosi` : lino_cosi/lib/cosi/locale

If the :xfile:`.po` files do not yet exist in your language, read `Add support
for a new language`_ before going on.

If you are the first to provide translations to some source code that has new or
changed translatable strings, you must run :cmd:`inv mm` ("make message files")
in order to make sure that the  :xfile:`.po` files are in sync with the source
code.  The :cmd:`inv mm` command never deletes any messages, so you can run it
also when you aren't sure whether it has run.

To edit these :xfile:`.po` files you can use either your preferred :doc:`text
editor </dev/newbies/editor>` or a tool like Poedit_.  We recommend the latter.
On Debian you install it with :cmd:`apt-get install poedit`.

.. _Poedit: https://poedit.net/

Choose a site to work on
------------------------

Don't simply translate all the messages in the :xfile:`django.po` files because

- there are a lot of them

- translations can depend on the context. It's better that you see where a
  message is being used before you decide how to translate it.

- it's more rewarding to start with the most visible ones and and watch the
  results of your work while you are advancing.

Go to some demo project or to some local site directory (e.g. the one you
created in :ref:`dev.install`)::

  $ go first

Edit your project's :xfile:`settings.py` file so that it specifies a
:term:`language distribution` (in the :setting:`languages` setting) consisting
of

- English as first language
- your language as the second language.

For example::

  class Site(Site):
      languages = 'en es'
      # languages = 'es en'

In case you wonder: your language can't be the first language because some
:term:`demo fixtures` would probably fail because :term:`babel fields <babel
field>` require at least the site's main language to be set.

Your :xfile:`settings.py` file should look similar to this:

.. literalinclude:: settings.py

Run :manage:`prep` to initialize the demo database::

  $ pm prep

Run the development server::

  $ runserver

Point your browser to view the site. Sign in as the user in your language.

.. image:: translate_1.png
  :scale: 80


Find the texts that you want to translate
-------------------------------------------

The translatable strings on this page (`gettext` and Poedit_ call them
"messages") are for example the menu labels ("Contacts", "Products" etc), but
also content texts like "Welcome", "Hi, Rodrigo!" or "This is a Lino demo site."

Now you must find out which :xfile:`django.po` file contains these strings. For
example, you can open another terminal window and use :command:`grep` to find
the file::

  $ grep -H Contacts ~/lino/env/repositories/lino/lino/locale/es/LC_MESSAGES/*.po
  /home/repositories/work/lino/lino/locale/es/LC_MESSAGES/django.po:#~ msgid "Contacts"
  $ grep -H Contacts ~/lino/env/repositories/xl/lino_xl/lib/xl/locale/es/LC_MESSAGES/*.po
  /home/luc/repositories/xl/lino_xl/lib/xl/locale/es/LC_MESSAGES/django.po:msgid "Contacts"
  /home/luc/repositories/xl/lino_xl/lib/xl/locale/es/LC_MESSAGES/django.po:msgid "Client Contacts"
  /home/luc/repositories/xl/lino_xl/lib/xl/locale/es/LC_MESSAGES/django.po:#~ msgid "Contacts"


Translate
---------

Launch Poedit_ on the :xfile:`django.po` file for the Spanish translation::

  $ poedit lino/locale/es/LC_MESSAGES/django.po

It looks similar to this screenshot:

.. image:: poedit_es_1.png
  :scale: 60

Translate a few messages. In our example we translated the following
message::

  Hi, %(first_name)s!

into::

  ¡Hola, %(first_name)s!

Save your work in Poedit_.  Poedit will automatically compile the
:xfile:`django.po` file into a corresponding :file:`django.mo` file.

Now you should first `touch` your `settings.py` file in order to tell
:manage:`runserver` that something has changed. Open a third terminal window and
type::

  $ go first
  $ touch settings.py

This will cause the server process (which is running in the first terminal
window) to reload and to rewrite any cache files.

Refresh your browser page:

.. image:: cosi_es_hola.png
  :scale: 80

Submit your work
---------------------

When you are satisfied with your work, you must make a pull request to ask us to
integrate your changes into the public Lino repositories. More about pull
requests in :doc:`/dev/git`.


Add support for a new language
------------------------------

Lino uses the same language codes as Django.
You can see the list of available languages in
`django/conf/global_settings.py
<https://github.com/django/django/blob/master/django/conf/global_settings.py>`__.

Every repository has a list of languages for which it provides translations.
This list is in the :envvar:`languages` parameter in the repository's
:xfile:`tasks.py` file.  If your language is not yet mentioned there, then add
it.

After adding a language, you must run :cmd:`inv mm`, which will create the new
catalogue files.

And then you need to create a demo user for your language. Otherwise :cmd:`pm
prep` gives a warning::

  No demo user for language 'bn'.

There are three ways to do it:

- Do this manually by signing in as robin and changing the language field in
  robin's :term:`user settings`.  You will have to do this again and again
  after each :cmd:`pm prep`.

- Edit the `demo_users.py
  <https://gitlab.com/lino-framework/lino/-/blob/master/lino/modlib/users/fixtures/demo_users.py>`__
  file in your local copy of the lino repository and
  add a fictive root user for your language.

  And don't forget to include this change in your pull request (see `Submit your
  work`_)

- Create a local fixture that creates the user::

    $ mkdir fixtures
    $ touch fixtures/__init__.py
    $ nano fixtures/demo.py

The :file:`demo.py` file should look as follows:

.. literalinclude:: fixtures/demo.py


Workarounds
-----------

Here is a pitfall. Imagine you want to translate the following string::

  msgid "%(person)s has been unregistered from %(course)s"

Here is a translation that makes sense but is *wrong*::

  msgstr "%(personne)s a été désinscrit du %(cours)"

Here is the correct translation::

  msgstr "%(person)s a été désinscrit du %(course)s"

C.-à-d. les mots-clés entre parenthèses sont des variables,
et il *ne faut pas* les modifier.

À noter également que le ``s`` derrière la parenthèse ne sera pas
imprimé mais est obligatoire
(il indique à Python qu'il s'agit d'un remplacement de type `string`).
