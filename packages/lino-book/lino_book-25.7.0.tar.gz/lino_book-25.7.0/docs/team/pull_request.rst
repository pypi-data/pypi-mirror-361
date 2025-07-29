.. _team.howto.submit:

============================
How to submit a pull request
============================

.. _dev.patch:

Send a patch
============

The easiest and most basic way of contributing a code change is to send a patch.
Here is how to do that.

- Go to the project root directory and type::

    $ git diff > mypatch.txt

- Send the file :file:`mypatch.txt` or its content via e-mail to a committer
  (somebody who has write permission to the public code repositories).

A disadvantage of this method is that you won't be visible as the contributor in
the history of the repository.

.. _dev.fork:

Use a fork
==========

Read more:

- https://www.atlassian.com/git/tutorials/git-forks-and-upstreams

The following would be our recommended way of making pull requests.

.. rubric:: Create a fork of the repositories you are going to work on.

- Go to https://gitlab.com/lino-framework/xxx  (where ``xxx`` is the nickname of
  the Lino repository, like "lino", "xl", "book", "noi", etc...)

- Sign in (if you didn't already)
- Click the "Fork" button and answer the questions GitLab asks you
- The URL of your fork will be something like https://gitlab.com/joedoe/xxx

.. rubric:: Point your local repository to use your fork

- Make sure that you have no local changes in your clone of the repository. If
  you have already local work done, be careful to not lose your changes. Say
  :cmd:`git diff > mypatch.txt` to have a patch just in case. Say :cmd:`git
  stash` to move your changes aside. Say :cmd:`git status` to see whether your
  copy is clean.

- Update the ``origin`` remote of your clone so that if syncs to your fork
  rather than the official lino repository::

    $ git remote set-url origin git@gitlab.com:joedoe/xxx.git

- Add an ``upstream`` remote to your local copy so that it points to your fork::

    $ git remote add upstream git@gitlab.com:lino-framework/xxx.git

- Verify that your remotes are correct::

    $ git remote -v
    origin	git@gitlab.com:joedoe/xxx.git (fetch)
    origin	git@gitlab.com:joedoe/xxx.git (push)
    upstream	git@gitlab.com:lino-framework/xxx.git (fetch)
    upstream	git@gitlab.com:lino-framework/xxx.git (push)

How to pull changes from upstream to your fork
==============================================

The official upstream repositories are under active development, so you probably
want to merge the latest changes into your fork as often as possible. Here is
how to do this::

  git fetch upstream
  git merge upstream/master

You probably also want to execute any work in feature branches, as they might
later become pull requests.

.. _pull_request.submit:

Submit a pull request
=====================

- Work in your local clone of that repository. For help, see: :ref:`git basics <git.basics>`.

- Publish your local changes to your public repository using :cmd:`git commit`
  and :cmd:`git push`.

- Run :cmd:`git request-pull`

See also :doc:`/topics/mama`.

.. _dev.request_pull:

Using :cmd:`git request-pull`
=============================

The problem with using GitHub pull requests is that this approach partly relies
on :term:`proprietary software`. Some more thoughts about this:

- `How to make pull requests *without* a GitHub account?
  <https://stackoverflow.com/questions/9630774/how-to-make-pull-requests-without-a-github-account>`__
  (2012-03-09)

- `Why Linus Thorvalds doesn't do GitHub pull requests.
  <https://github.com/torvalds/linux/pull/17#issuecomment-5654674>`__
  (2012-05-11)

- The `git request-pull <https://git-scm.com/docs/git-request-pull>`__
  command.


Pushing directly to master branch?
==================================

Hell is when people push directly to master branch. That's at least what `this
thread on Reddit
<https://www.reddit.com/r/ProgrammerHumor/comments/dh87ae/dante_would_be_proud/>`__
suggests. The resulting discussion is interesting. Obviously there are different
religious schools about the topic. Well-educated project managers seem to be
horrified and ask "Who lets people push to master without a pull request and
code review?", but others have obviously been in that "hell", and they report
quite positive things about it:

- It depends on what the workflow for git is. If you CI/CD deploys to production
  on a push to master, well you shouldn't push to master obviously. If "master"
  is the bleeding edge branch that may be broken from time to time, then it's
  not that big of a big deal. For example, Google does it that way in Flutter.
  Master is only "Usually functional, though sometimes we accidentally break
  things.". After testing, master gets merged into "dev", then "beta", then
  "stable".

- We push to master in my current role and I have in all my jobs for the last
  10+ years. We do ci/cd, feature toggles and automated testing. Pairing is how
  we do code reviews. Honestly nothing wrong with it 🙂
