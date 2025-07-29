.. doctest docs/apps/cms/db.rst
.. _cms.topics.db:

================================
Database structure of Lino CMS
================================

This document describes the database structure.

.. contents::
  :local:


.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_book.projects.cms1.settings')
>>> from lino.api.doctest import *

>>> analyzer.show_db_overview()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
32 plugins: lino, about, printing, system, linod, jinja, bootstrap3, publisher, react, cms, social_django, users, office, xl, countries, contacts, groups, uploads, contenttypes, gfks, topics, albums, sources, blogs, memo, comments, help, search, checkdata, inbox, staticfiles, sessions.
39 models:
============================== ================================ ========= =======
 Name                           Default table                    #fields   #rows
------------------------------ -------------------------------- --------- -------
 albums.Album                   albums.Albums                    5         12
 blogs.Entry                    blogs.Entries                    15        5
 blogs.EntryType                blogs.EntryTypes                 6         0
 checkdata.Message              checkdata.Messages               6         1
 comments.Comment               comments.Comments                12        596
 comments.CommentType           comments.CommentTypes            4         0
 comments.Reaction              comments.Reactions               6         0
 contacts.Company               contacts.Companies               22        12
 contacts.CompanyType           contacts.CompanyTypes            7         16
 contacts.Partner               contacts.Partners                20        81
 contacts.Person                contacts.Persons                 27        69
 contacts.Role                  contacts.Roles                   4         3
 contacts.RoleType              contacts.RoleTypes               5         5
 contenttypes.ContentType       gfks.ContentTypes                3         39
 countries.Country              countries.Countries              6         10
 countries.Place                countries.Places                 9         81
 groups.Group                   groups.Groups                    7         3
 groups.Membership              groups.Memberships               4         6
 help.SiteContact               help.SiteContacts                8         3
 linod.SystemTask               linod.SystemTasks                25        3
 memo.Mention                   memo.Mentions                    5         234
 publisher.Page                 publisher.Pages                  16        90
 sessions.Session               users.Sessions                   3         ...
 social_django.Association      social_django.AssociationTable   7         0
 social_django.Code             social_django.CodeTable          5         0
 social_django.Nonce            social_django.NonceTable         4         0
 social_django.Partial          social_django.PartialTable       6         0
 social_django.UserSocialAuth   users.SocialAuths                7         0
 sources.Author                 sources.Authors                  10        5
 sources.License                sources.Licenses                 4         2
 sources.Source                 sources.Sources                  9         6
 system.SiteConfig              system.SiteConfigs               3         1
 topics.Tag                     topics.Tags                      4         0
 topics.Topic                   topics.Topics                    4         0
 uploads.Upload                 uploads.Uploads                  14        30
 uploads.UploadType             uploads.UploadTypes              8         0
 uploads.Volume                 uploads.Volumes                  4         3
 users.Authority                users.Authorities                3         0
 users.User                     users.AllUsers                   21        6
============================== ================================ ========= =======
<BLANKLINE>
