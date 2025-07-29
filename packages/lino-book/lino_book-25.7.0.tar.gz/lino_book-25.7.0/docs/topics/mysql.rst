.. doctest docs/topics/mysql.rst
.. _dg.topics.mysql:

==========================================
How to set up a site with a MySQL database
==========================================

All the :term:`demo sites <demo site>` of your developer environment use sqlite
as their database engine because that's more easy to manage. But when working on
a MySQL-specific issue you might want to run a development server (using
:manage:`runserver`) that uses a MySQL database. Here is how to do this.


.. contents::
    :depth: 1
    :local:

- We assume that you have installed your :term:`developer environment`.

- Open a terminal and become ``root``::

    $ sudo su

- Activate your developer environment while being ``root``::

    # source /home/joe/lino/env/bin/activate  (replace "joe" by your username)

- Run :cmd:`getlino configure` as ``root`` with command-line option
  ``--db-engine mysql`` and answer all configuration options with :kbd:`ENTER`
  to keep all other configuration options unchanged::

    # getlino configure --db-engine mysql
    Running as root.
    This is getlino version 24.5.0 running on Ubuntu 22.04.4 LTS (ubuntu jammy).
    This will write to configuration file /home/joe/lino/env/.getlino.conf
    - sites_base (Base directory for Lino sites on this server) [/home/joe/lino]:
    - local_prefix (Prefix for local server-wide importable packages) [lino_local]:
    - shared_env (Root directory of your shared virtualenv) [/home/joe/lino/env]:
    - repos_base (Base directory for shared code repositories) [/home/joe/lino/env/repositories]:
    - clone (Clone all contributor repositories and install them to the shared-env) [True]:
    - webdav (Whether to enable webdav on new sites) [True]:
    - backups_base (Base directory for backups) [/var/backups/lino]:
    - log_base (Base directory for log files) [/var/log/lino]:
    - usergroup (User group for files to be shared with the web server) [www-data]:
    - supervisor_dir (Directory for supervisor config files) [/etc/supervisor/conf.d]:
    - env_link (link to virtualenv (relative to project dir)) [env]:
    - repos_link (link to code repositories (relative to virtualenv)) [repositories]:
    - appy (Whether this server provides appypod and LibreOffice) [True]:
    - redis (Whether this server provides redis) [False]:
    - devtools (Whether to install development tools (build docs and run tests)) [True]:
    - server_domain (Domain name of this server) [localhost]:
    - https (Whether this server uses secure http) [False]:
    - ldap (Whether this server works as an LDAP server) [False]:
    - monit (Whether this server uses monit) [False]:
    - web_server (Which web server to use here.) (nginx, apache, ) []:
    - db_engine (Default database engine for new sites.) (mysql, postgresql, sqlite3) [mysql]:
    - db_port (Default database port to use for new sites.) []:
    - db_host (Default database host name for new sites.) [localhost]:
    - db_user (Default database user name for new sites. Leave empty to use the project name.) []:
    - db_password (Default database password for new sites. Leave empty to generate a secure password.) []:
    - admin_name (The full name of the server administrator) [Joe Doe]:
    - admin_email (The email address of the server administrator) [joe@example.com]:
    - time_zone (The TIME_ZONE to set on new sites) [Europe/Brussels]:
    - linod (Whether new sites use linod) [True]:
    - languages (The languages to set on new sites) [en]:
    - front_end (The front end to use on new sites) (lino.modlib.extjs, lino_react.react, lino_openui5.openui5) [lino_react.react]:
    Write above options to /home/joe/lino/env/.getlino.conf ? [y or n] Yes

  Hit :kbd:`y` to let getlino write your config file::

    Wrote config file /home/joe/lino/env/.getlino.conf
    Start installing Lino according to above settings? [y or n] Yes

  Hit :kbd:`y` and answer all remaining questions with :kbd:`ENTER`. (More
  precisely you can say No to some questions if you understand what they mean.
  For example you don't need to clone and install your repositories any more.
  The important thing is to install the system packages and the python package
  for mysql, and start the mysql service.)

- Run :cmd:`getlino startsite` as ``root``::

    # getlino startsite cosi second

  (Replace "cosi" by the nickname of the application you want to test, replace
  "second" by any name that does not yet exist under your :envvar:`sites_base`
  directory. The output should be something like this::

    Running as root.
    This is getlino version 24.5.0 running on Ubuntu 22.04.4 LTS (ubuntu jammy).
    Preparing to create cosi site in /home/joe/lino/lino_local/second
    Shared virtualenv [/home/joe/lino/env]:
    User credentials (for mysql on localhost:):
    - user name [second]:
    - user password [jVPmcd3N7K4]:
    - port [3306]:
    - host name [localhost]:
    Site's secret key [ugh_xDB00E7sT_jX-hqccA51Ssc]:
    Okay to create cosi site in /home/joe/lino/lino_local/second? [y or n]

  Answer all questions with :kbd:`ENTER` or :kbd:`y`.

- Hit :kbd:`Ctrl+D` to terminate your ``root`` session and become back yourself.

- Go to the project directory and run :manage:`runserver`::

    $ go second
    $ runserver

- Sign in as ``robin`` with password ``1234`` (unlike a :term:`demo site` this
  site does not show a list of clickable users because
  :attr:`lino.core.site.Site.is_demo_site` is not set to `True`).

- As with any demo site, you can modify the :xfile:`settings.py` and re-run
  :cmd:`pm prep` at any time.
