.. _book.contrib.https:

===================================================
Simulate a HTTPS server on your development machine
===================================================

It can happen that you want to simulate a :term:`production server` on your
development environment.

Here is how to do this::

  $ sudo su
  # getlino configure --web-server nginx --no-appy --no-redis --no-monit --db-user lino db-password lino
  # getlino startsite noi a

Now you can start http://a.localhost in your browser.

You can activate https on this server using a self-signed certificate. For this,
edit your :file:`/etc/nginx/sites-enabled/a.conf`::

  upstream django_a {
     ...
  }

  server {
    server_name a.localhost;
    ...

    listen [::]:443 ssl;
    listen 443 ssl;

    ssl_certificate /path/to/fullkey.pem; # managed by Certbot
    ssl_certificate_key /path/to/key/privkey.pem; # managed by Certbot
    # include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

  }

  server {
      if ($host = a.lino-framework.org) {
          return 301 https://$host$request_uri;
      }
      listen      80;
      listen [::]:80 ;
      server_name a.localhost;
      return 404;
  }


Now the http://a.localhost in your browser should redirect to
https://a.localhost

The only difference with a real certificate is that you will need to manually
instruct your browser to trust this certificate.
