.. _dev.git:

===============
Git cheat sheet
===============

.. contents::
   :local:


.. highlight:: bash


Cloning a repository
--------------------

When you clone a repository from GitLab or GitHub, the :cmd:`git clone` command
adds a *remote* named "origin", pulls down all Git data, creates a pointer named
`origin/master` to the remote's master branch, and a pointer `master` to your
own local master branch, starting at the same place as origin’s master branch.

For some repositories you must replace "master" by "main" in above paragraph.
See :doc:`/topics/mama`.


Branching
---------

My summary after reading the `Branching
<https://git-scm.com/book/en/Git-Branching>`_ chapter of Scott Chacon's
Pro Git book:

- *master* : the default branch that will be selected after cloning your repo.
  The name is purely conventional and has no special meaning for Git itself. In
  2021 it was changed to "main".

- *HEAD* : pointer to the "current branch" (the one that is checked out).

- Create a new branch called "20141022":  ``git branch 20141022``
- Select a branch : ``git checkout 20141022``
- Shortcut to create and select : ``git checkout -b 20141022``

- Starting and selecting a branch will not modify your local modifications.

- List all branches: ``git branch``

- See which branches are already merged into HEAD : ``git branch --merged``

- See all the branches that contain work you haven’t yet merged :
  ``git branch --merged``


- Merge a branch into current branch:  ``git merge 20141022``

.. _conflict_resolve_guide:

- In case of a merge conflict, start reading at `Basic Merge Conflicts <https://git-scm.com/book/en/Git-Branching-Basic-Branching-and-Merging#Basic-Merge-Conflicts>`_

- Delete a branch: ``git branch -d 20141022``

- Common names for *long-term branches*: *develop*, *proposed*, *next*.



Remote branches
---------------

When you want to share a branch with the world, you need to push it to a remote
to which you have write access. For example::

  $ git checkout -b myfeature  # create a local branch
  $ git push origin myfeature  # make it public
  $ # ... add files and commit changes

- Remote branches : ``(remote)/(branch)``

.. _pull_vs_fetch:

.. rubric:: Pull vs fetch

When pulling such a remote branch, keep in mind the subtle difference between
:cmd:`git pull` and :cmd:`git fetch`, where the following command::

  $ git pull origin myfeature

will pull the content of the remote branch and merge it with the current local
branch. On the other hand, the following command::

  $ git fetch origin myfeature

will pull the content of the remote branch but will NOT merge it with the
current branch. In such a case it is safer to use the later command.

Later the user can safely checkout the content of the fetched branch by using
the following command::

  $ git checkout myfeature

TODO: Continue to read
https://git-scm.com/book/en/Git-Branching-Remote-Branches


Multiple remotes
----------------

A use case for multiple remotes may arise in scenarios such as
when a user needs to manage a personal copy of some repository or
where the user does not have write access to the original repository.

In such a case the user may make a fork of the original repository
using the git hosted frontend.

Let's take our `lino <https://gitlab.com/lino-framework/lino>`__ repository
as an example where I as user on gitlab having the username *8lurry*
shell make a fork and will modify the code base for my personal use case
while keeping my fork up-to-date with the original repository from lino-framework.

- I make a fork of the repository lino from the webinterface
  https://gitlab.com/lino-framework/lino (remote name: *upstream*), where the forked
  repository is pointed to by *https://gitlab.com/8lurry/lino (remote name: origin)*.

In the following section I will show how I keep my remote *origin* up-to-date with
the remote *upstream* while having my personal modification on it as well and for
simplicity we assume that we only work on branches from different ref pointer
named only *master*.

.. rubric:: I open up a terminal window on my personal computer and do the following:

- Clone my remote *origin* repository::

    $ git clone git@gitlab.com:8lurry/lino.git

- Any further instructions below will be done within the lino directory.
  So, I *cd* into lino::

    $ cd lino

- I set the remote *upstream* to my local repository::

    $ git remote add upstream git@gitlab.com:lino-framework/lino.git

- From time to time when I need to update my local repository from the *upstream*
  I do::

    $ git pull upstream master

See :ref:`pull vs fetch <pull_vs_fetch>` to understand what the above command does.
Also while the above command gets the changes from the upstream it still keeps my
personal modifications intact.

- In case of a merge conflict arise I refer to :ref:`resolve guide <conflict_resolve_guide>`
- To make the updates available at my remote *origin* I do::

    $ git push

.. _git.basics:

.. rubric:: Git basics

- When I do some modifications to my local repository I add the changes to the git HEAD
  by calling::

    $ git add -u

- After reviewing more I confirm my changes while giving it my_message about the changes::

    $ git commit -m "my_message"

- I publish my changes to the remote *origin* by calling::

    $ git push

In case (somebody from the so called *upstream* remote asks you to or) you by yourself
need to make your changes contained in the remote *origin* available to the remote
*upstream* (while you don't have *write permission* to the *upstream*) you can make
a pull request by following the instructions given :ref:`here <pull_request.submit>`


Make a pull request
-------------------

- https://git-scm.com/book/en/Distributed-Git-Contributing-to-a-Project
- https://help.github.com/articles/creating-a-pull-request
- See more in: :ref:`team.howto.submit`



Contributing pull requests to foreign projects
----------------------------------------------

Most projects don't use the "shared repository model" (several users
writing to a repo) but the "fork & pull" model as explained in `Using
pull requests <https://help.github.com/categories/collaborating/>`_).

Example: I have a fork of Ahmet's ablog project.  Ahmet made changes
in ablog and asked me to test them.  So I need to merge his changes
into the local copy of my fork.

So if I want to contribute to Ahmet's ablog project, I need to fork
the project on GitHub (using their web interface) and then get a clone
of this fork::

    $ git clone git@github.com:lsaffre/ablog.git

Now I make my changes::

    $ e ablog/__init__.py

When I decided that I want to share my local changes, I create a
branch, commit it and push it to *my* repo::

    $ git checkout -b feed_encoding
    $ git add -u
    $ git commit -m "Added encoding utf-8 to file atom.xml"
    $ git push origin feed_encoding

Now their web interface sees my branch and allows me to turn it into a
pull request.


Merge from upstream
--------------------

Every local project repository has a set of *tracked repositories*,
also called "remotes".  The default remote (the place from where my
local repo has been taken) is called **origin**.

List all remotes::

  $ git remote -v
  origin   git@github.com:lsaffre/ablog.git (fetch)
  origin   git@github.com:lsaffre/ablog.git (push)

First I must add Ahmet's repo as a new remote, which is usually called
**upstream**::

    $ git remote add upstream git@github.com:abakan/ablog.git

My local repo now has two remotes::

    $ git remote -v
    origin	git@github.com:lsaffre/ablog.git (fetch)
    origin	git@github.com:lsaffre/ablog.git (push)
    upstream	git@github.com:abakan/ablog.git (fetch)
    upstream	git@github.com:abakan/ablog.git (push)


Now I can fetch all changes from the upstream repository::

    $ git fetch upstream

Before continuing, make sure where you want the changes from upstream
to go. Usually you want them to go to `master`, so you must select
this branch::

    $ git checkout master

And finally I can merge them into my local repo::

    $ git merge upstream/master

`fetch upstream` looks up the specified remote, fetches any data from
it that you don’t yet have, and updates your local database, moving
your ``upstream/master`` pointer to its new position.


How to update the most recent commit message
--------------------------------------------

You can rewrite the most recent commit message with ``amend``::

  $  git commit --amend -m "new commit message"

This will change the commit id, i.e. actually you are creating a new commit that
replaces the old one.


TODO:

- How to return back to my local changes?

- What was this?

  ::

    $ git pull upstream master



Merge from upstream while local branch active
---------------------------------------------

I had started a branch in my local copy of ablog::

    $ git status
    On branch trans_estonian
    nothing to commit, working directory clean
    $ git push origin trans_estonian
    Everything up-to-date



Accept a pull request
---------------------

Example: cuchac posted a pull request for a branch which he named
``export_excel_datetime`` (on his fork of project `lino`).

Check that there are no local changes in my repo::

    $ go lino
    $ git status
    On branch master
    Your branch is up-to-date with 'origin/master'.
    nothing to commit, working directory clean

Check out his branch into a new branch ``inbox`` in order to test the
changes::

    $ git checkout -b inbox master
    $ git pull git@github.com:cuchac/lino.git export_excel_datetime
    remote: Counting objects: 6, done.
    remote: Compressing objects: 100% (3/3), done.
    remote: Total 6 (delta 4), reused 5 (delta 3)
    Unpacking objects: 100% (6/6), done.
    From github.com:cuchac/lino
     * branch            export_excel_datetime -> FETCH_HEAD
    Merge made by the 'recursive' strategy.
     lino/modlib/export_excel/models.py | 21 +++++++++++++++++++--
     1 file changed, 19 insertions(+), 2 deletions(-)

Test the changes::

    $ inv test
    [localhost] local: python setup.py -q test
    ...........................................
    ----------------------------------------------------------------------
    Ran 43 tests in 36.290s

    OK

    Done.

Reactivate master and merge the changes::

    $ git checkout master
    M	docs/tutorials/pisa/pisa.Person-1.pdf
    Switched to branch 'master'
    Your branch is up-to-date with 'origin/master'.

    $ git merge --no-ff inbox
    Merge made by the 'recursive' strategy.
     lino/modlib/export_excel/models.py | 21 +++++++++++++++++++--
     1 file changed, 19 insertions(+), 2 deletions(-)

Note: is the ``--no-ff`` option necessary?

Push everything to the master::

    $ git push origin master
    Counting objects: 43, done.
    Delta compression using up to 4 threads.
    Compressing objects: 100% (11/11), done.
    Writing objects: 100% (11/11), 1.39 KiB | 0 bytes/s, done.
    Total 11 (delta 8), reused 0 (delta 0)
    To git@github.com:lsaffre/lino.git
       988adf9..55961b9  master -> master

And finally delete the ``inbox`` branch::

    $ git branch -v --merged
      inbox  bfd3f39 Merge branch 'export_excel_datetime' of github.com:cuchac/lino into inbox
    * master 55961b9 Merge branch 'inbox'

    $ git branch -d inbox
    Deleted branch inbox (was bfd3f39).

How to fetch a remote pull request
----------------------------------

::

    git fetch origin pull/999/head:my-branch
    git checkout my-branch

Where ``999`` is the number of the pull request and ``my-branch`` the name of
the branch.




Bibliography
------------

- `Git branches tutorial
  <https://www.atlassian.com/git/tutorial/git-branches>`_

- `stackoverflow
  <https://stackoverflow.com/questions/6286571/git-fork-is-git-clone>`_

- `Collaboration on Github
  <http://www.eqqon.com/index.php/Collaborative_Github_Workflow>`_)

- GitHub help:
  `Fork a repo <https://help.github.com/articles/fork-a-repo/>`_,
  `Syncing a fork <https://help.github.com/articles/syncing-a-fork>`_.
