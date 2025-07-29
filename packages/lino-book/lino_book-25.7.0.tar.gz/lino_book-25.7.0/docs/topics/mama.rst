====================================================
Rename "master" to "main" in our repositories
====================================================

In some repositories the default branch is still called ``master`` while in
other repositories it is called ``main``.  That's because Lino started long
before 2021 (when the Git community decided to change "master" to "main", read
e.g. `The new Git default branch name
<https://about.gitlab.com/blog/2021/03/10/new-git-default-branch-name/>`__).

But we are working on for :ticket:`5597` (Rename "master" to "main" in our
repositories). Inspired by `this
<https://docs.gitlab.com/ee/user/project/repository/branches/default.html>`__
and maybe `this
<https://www.linkedin.com/pulse/technology-notes-how-tos-infrastructure-git-master-main-eldritch/>`__.

(:count:`step`) Agree with other contributors regarding the date and time for this.

(:count:`step`) Make sure that your local copy is clean::

  $ go lino
  $ git status
  $ git checkout master

(:count:`step`) Rename the existing default branch to the new name (main). The
argument -m transfers all commit history to the new branch::

  $ git branch -m master main

(:count:`step`) Push the newly created main branch upstream, and set your local
branch to track the remote branch with the same name::

  $ git push -u origin main

(:count:`step`) Change the project's default branch on the GitLab website:

- Select Settings > Repository. Expand Branch defaults. For :guilabel:`Default
  branch`, select a new default branch. `Full instructions see here
  <https://docs.gitlab.com/ee/user/project/repository/branches/default.html#change-the-default-branch-name-for-a-project>`__.

(:count:`step`) Notify your project contributors of this change, because they must
also take some steps:

- Contributors should pull the new default branch to their local copy of the
  repository.

- Contributors with open merge requests that target the old default branch
  should manually re-point the merge requests to use main instead.

(:count:`step`) Optionally tell your computer to use "main" and not "master" as
default branch name for new repositories::

  git config --global init.defaultBranch main
