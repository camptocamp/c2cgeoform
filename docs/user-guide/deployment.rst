Deployment
----------

With Apache/mod_wsgi
~~~~~~~~~~~~~~~~~~~~

Install Apache and mod_wsgi:

.. code-block:: shell

   sudo apt update
   sudo apt-get install apache2 libapache2-mod-wsgi-py3

Generate the WSGI entry point and apache configuration file:

.. code-block:: shell

   make modwsgi

In your apache configuration, add:

.. code-block:: ini

   Include /.../c2cgeoform_project/.build/apache.conf
