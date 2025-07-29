===============
About site data
===============

Site data in Lino is either JavaScript modules or JSON objects or a combination
of both, which are loaded by the browser and act as the interface in
communication between the browser and the Lino application on the server side.

Site data is managed differently depending on the frontend that lino uses. Here,
we go over how our two major frontends (:mod:`lino.modlib.extjs` and
:mod:`lino_react.react`) manage site data.

Environment specifics
=====================

Lino stores the timestamp of the latest modification of the application instance
and site data knows about this modification timestamp, which is used in updating
the frontend. There are different methods of taking the modification timestamp
depending on the environment type (whether production or development). To be
precise, lino takes the modification timestamp from either the
:xfile:`settings.py` file's `st_mtime` (in case it is a production server) or any
of the file's (watched by :manage:`runserver` command) `st_mtime` that was
modified on the latest. The later feature is available only when the
:attr:`Site.is_demo_site` attribute is set to `True`.


NB: If the application frontend does NOT require loading any site data you should
simply set the value of the :attr:`Site.never_build_site_cache` attribute to
`True` in your :xfile:`settings.py` file.


ExtJS specifics
===============

.. _XXX_XX:

The main site data component in extjs is a JavaScript module specific to a
:term:`user type` and a `language` with a name of the following format
`lino_xxx_xx.js` where former `xxx` is a three digit string that indicate the
:term:`user type` and the later `xx` indicates the `language` code of the user
for example `en` for english.

Extjs is build in a way so that such `lino_xxx_xx.js` files are loaded in a
`script` tag on the HTML document header. In case of an update (when lino finds
a new modification timestamp) lino rebuilds such `lino_xxx_xx.js` file and
reloads the site root to reflect the code changes in the frontend immediately.


React specifics
===============

The latest build of `Lino react` is dumped into a file named :xfile:`main.js`
(the actual react application). All lino applications using `Lino react`
frontend loads the :xfile:`main.js` into a `script` tag on the HTML document
header.

Site data for `Lino react` are build into some JSON files (with .json
extension). There are two categories of such JSON files, ones we internally call
`site data`, files of the format `lino_xxx_xx.json`, and the others we
internally call `actor data`, files of the format
`Lino_applabel.Actorname_xxx_xx.json`. See the paragraph :ref:`here <XXX_XX>`
the understand what `xxx_xx` on the filenames mean. `Lino react` loads and
caches these `site data` and `actor data` files on the run. Due to the
complicated nature of how `Lino react` manages these cached data, in case of an
update (when new modification timestamp found by lino application), it is hard
to clean up the caches from the browser with application code (JavaScript).
Hence, we require two HTTP request-response cycles for cleaning up and updating
the frontend using the `Clear-Site-Data <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Clear-Site-Data>`__
response header. These HTTP request-response cycles are explained below:

- first request:

A parameter `lv` with the value of the latest modification timestamp, which is
stored in the cached JSONs, is added to every GET request by `Lino react`.

- first response:

When a difference is found by the lino application comparing `lv` from GET
request and the server's latest modification timestamp, then this response
occur, which only says that a version mismatch is found (in JSON format, like
so: {'version_mismatch': True}).

At this stage adding the `Clear-Site-Data` header to the response (potentially)
will NOT clean up the whole site for the `origin` of the GET request
(potentially) might NOT be the site root (url `/` or `scheme//host/`), which
will only clean up caches that are stored under the GET request's `origin`.

- second request:

This request is made only when the JSON response contains a key
`version_mismatch` of `True` boolean value.

A GET request made to the site root (url `/`) with a
parameter named `update_found`.

- second response:

When a lino application finds a GET request made to the site root containing the
`update_found` parameter, it adds the `Clear-Site-Data` header to the usual
response, which is able to successfully clean up the frontend for the `origin`
of the request is the site root.

PS:

    Writing this up and thinking, I have a feeling that we can do the cleaing up
    and updating on only one HTTP request-response cycle if we compute the
    difference in modification timestamps on the frontend rather then doing in
    on the backend. Maybe something for later (a TODO).

    .. blogauthor:: `8lurry <mailto:sharif@saffre-rumma.net>`__
