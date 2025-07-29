.. _dg.plugins.peppol.credentials:

==============================
How to set up your credentials
==============================

The :mod:`lino_xl.lib.peppol` plugin currently requires the `Flowin e-invoicing
<https://documentation.ibanity.com/einvoicing/1/products>`__  API by
:term:`Ibanity`. It is possible to add support for other :term:`Peppol access
point` providers.

Whether you want to play as a developer with the :term:`Ibanity API`, or whether
you want to configure a :term:`production site`, in both cases you need to set
up your credential files so that Lino can access the Ibanity API. Here is how to
do this.

As a developer
==============

To play with the :term:`Ibanity API` as a developer, you need a **sandbox
application** on the Ibanity server.

- We assume that you have your Lino :term:`developer environment` installed.

- Create an account on the :term:`Ibanity developer portal`.

- Create a sandbox application, activate the "Flowin e-invoicing" product,
  generate a certificate, extract the certificate files and store them into an
  arbitrary directory in your private data (e.g.
  :file:`~/Documents/ibanity/sandbox`). The directory should now contain four
  files::

    $ cd ~/Documents/ibanity/sandbox
    $ ls
    ca_chain.pem  certificate.pem  certificate.pfx  private_key.pem

- Decrypt the private key because Python's `requests
  <https://pypi.org/project/requests/>`_ module doesn't support encrypted keys::

    $ openssl rsa -in private_key.pem -out decrypted_private_key.pem

  Not sure about this but it seems that you can now throw away the
  :file:`private_key.pem` file and forget the password you used to generate it.

- Still in the same directory, create a file named :file:`credentials.txt` that
  contains a single line of text in the format ``{client_id}:{client_secret}``.
  Where `client_id` and `client_secret` are both given by the Ibanity developer
  portal. For sandbox applications the `client_secret` is always the same string
  "valid_client_secret".

- Go to your copy of the ``cosi1`` demo project and create a symbolic link named
  :file:`secrets`, which points to your private directory::

     $ go cosi1
     $ ln -s ~/Documents/ibanity/sandbox secrets

  Note that files and directories named :file:`secrets` are ignored by Git
  because they are listed in the `.gitignore
  <https://gitlab.com/lino-framework/book/-/blob/master/.gitignore>`__ file.

Now you should be able to test the documents of the peppol plugin by saying::

  $ go book
  $ doctest docs/plugins/peppol/*.rst

As a server administrator
=========================

If you want to provide Peppol access on a :term:`production site`, you need a
**live application** on the Ibanity server. It's similar to a sandbox
application but when generating the certificate, the Ibanity portal asks you to
generate an RSA key pair and a Certificate Signing Request::

    $ cd ~/Documents/ibanity/live
    $ openssl genrsa -aes256 -out private_key.pem 2048
    $ openssl req -new -sha256 -key private_key.pem -out ibanity.csr ...

And then to upload the :xfile:`ibanity.csr` file to their server.  And the zip
file with certificate files contains only two files :file:`ca_chain.pem` and
:file:`certificate.pem`. And instead of creating a symbolic link you probably
use :cmd:`scp` to upload these files to a real subdirectory :xfile:`secrets` on
your Lino server.
