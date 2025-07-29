.. _gh2gl:

============================
Moving from GitHub to GitLab
============================

Until 2021 our repositories were hosted on `GitHub
<https://github.com/lino-framework>`__. In March 2021 we started to move to
`GitLab <https://gitlab.com/lino-framework>`__.

The following repositories are now maintained on GitLab:

- 2021-03-11 : :ref:`cg`, :ref:`book` and :ref:`atelier`
- 2021-04-12 : lino, xl, noi, cosi, voga, avanti, welfare, weleup, welcht
- 2021-04-25 : presto, react, amici, tera
- 2021-04-30 : getlino, algus, openui5, care, vilma
- 2021-05-21 : pronto
- 2022-08-17 : rstgen

- todo: eidreader, blog, mercato, ext6, cd, tt, patrols, logos

How to update the remote setting of your clone
==============================================

If you have a clone of one of these repositories, you must update its ``remote``
setting::

  $ git remote rm origin
  $ git remote add origin git@gitlab.com:lino-framework/XXX.git
  $ git fetch
  $ git branch --set-upstream-to=origin/master master

If :cmd:`git fetch` says "git@gitlab.com: Permission denied (publickey). fatal:
Could not read from remote repository.", then you might want to say::

  $ git remote add origin https://gitlab.com/lino-framework/XXX.git


Where ``XXX`` is the **nickname** of the repository. See
https://gitlab.com/lino-framework for the list of repository nicknames.

See https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes in
case you wonder what a remote is.

How to see the remotes of your clone::

  $ git remote -v


How to move a repo from GitHub to GitLab
========================================

Here is my cheat sheet for moving repositories from GH to GL.

Change the remote and push to the new upstream::

  $ git pull
  $ git remote rm origin
  $ git remote add origin git@gitlab.com:lino-framework/XXX.git
  $ git push -u git@gitlab.com:lino-framework/XXX.git master

Add a :xfile:`.gitlab-ci.yml` file (copy from a repo that is already on GL)::

  $ cp ../cosi/.gitlab-ci.yml .
  $ git add .gitlab-ci.yml

Update URLs in the :xfile:`setup_info.py` and the main :xfile:`__init__.py`.

Run :cmd:`inv bd` to update the :xfile:`README.rst` file and then push your
first changes on GitLab::

  $ inv bd
  $ git ci -am "moved from GitHub to GitLab"
  $ git push

Visit https://gitlab.com/lino-framework/XXX/edit#js-general-project-settings
and change visibility from "private" to "public" (this can't be done using
the CLI as explained `here
<https://stackoverflow.com/questions/57395399/gitlab-default-project-visibility-when-creating-projects-from-terminal)>`__)
in the GitLab project settings.


Visit https://github.com/lino-framework/XXX/blob/master/README.rst
and use the web UI to add a warning to the :xfile:`README.rst` file::

  Warning: This repository has moved to https://gitlab.com/lino-framework/XXX

Update the known repositories in :mod:`getlino.utils`.

Finally:

- Tell GitHub to archive the repository.
- Run :cmd:`inv check`
- Run :cmd:`pp -l` and check the project urls.
- Release to PyPI.

Why avoid GitHub?
=================


"GitHub has warped Git — creating add-on features that turn a distributed,
egalitarian, and FOSS system into a centralized, proprietary site. And, all
those add-on features are controlled by a single, for-profit company. By staying
on GitHub, established FOSS communities bring newcomers to this proprietary
platform — expanding GitHub's reach. and limiting the imaginations of the next
generation of FOSS developers." -- https://sfconservancy.org/GiveUpGitHub/
