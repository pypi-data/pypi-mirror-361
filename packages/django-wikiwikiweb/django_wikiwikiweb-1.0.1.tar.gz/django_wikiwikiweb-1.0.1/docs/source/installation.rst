============
Installation
============

.. note::

    The development team are always happy to hear suggestions for how to streamline this process.

Download
~~~~~~~~

The preferred way to get hold of ``django-wikiwikiweb`` is via ``pip``::

    $ pip install django-wikiwikiweb

This may be a good time to add ``django-wikiwikiweb`` to your project's ``requirements.txt``.

The ``django-wikiwikiweb`` source code is also available via `the project's GitHub repository <https://github.com/simonharris/django-wikiwikiweb>`_.

Initial Configuration
~~~~~~~~~~~~~~~~~~~~~

There are a few changes to make to your project's configuration files.


App Settings
^^^^^^^^^^^^

In your project's ``settings.py``:

1) add the app and its dependencies to ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'wikiwikiweb',
        'markdownify',
        'simple_history',
        'django_bootstrap5',
    ]


2) enable the ``django-simple-history`` middleware by adding the following entry to ``MIDDLEWARE``::

    MIDDLEWARE = [
        ...
        'simple_history.middleware.HistoryRequestMiddleware',
    ]


3) enable the ``django-wikiwikweb`` context processor by adding the following to entry to ``TEMPLATES``::

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                   ...
                   'wikiwikiweb.context_processors.site_wide_context',
                ],
            },
        },
    ]


App URLs
^^^^^^^^^^

In your project's root ``urls.py``:

4) include the ``django-wikiwikiweb`` URL routes file in your ``urlpatterns``::

    urlpatterns = [
        # To run under a path:
        path('wiki/', include('wikiwikiweb.urls')),
        ...
        # OR it will also run just fine as a standalone site:
        #path('', include('wikiwikiweb.urls')),
        ...
        # Don't forget Django's own routes for login/logout
        path('accounts/', include('django.contrib.auth.urls')),
    ]



Database Migrations
^^^^^^^^^^^^^^^^^^^

5) finally, apply the database migrations to create the tables needed by ``django-wikiwikiweb``:


.. code-block:: console

    $ python manage.py migrate wikiwikiweb


You should now be good to go. Upon starting the Django server, you should now have an empty Wiki under ``/wiki/``, or wherever you chose for it to live. A WikiWikiWeb section should now be available under the Django admin site. Visit the :ref:`label-admin-quickstart` guide for Wiki admins to get started.


Optional Settings
^^^^^^^^^^^^^^^^^


There are a small number of optional settings to consider:

i) ``django-wikiwikiweb`` integrates with the Django auth system (i.e. user management and authentication) to some extent, in that it uses login and logout links which reference the auth URLs. Thus, if you don't already, you may wish to add definitions for the constants ``LOGIN_REDIRECT_URL`` and ``LOGOUT_REDIRECT_URL`` in ``settings.py``.


ii) ``django-wikiwikiweb`` uses ``django-markdownify`` to format pages (see :ref:`label-user-markdown`). You may wish to allow more (or fewer) HTML tags to be generated than ``django-markdownify`` allows by default. This is done via the ``MARKDOWNIFY`` constant in ``settings.py``. The settings allowed by ``django-markdownify`` are very well documented on the project's own documentation site: https://django-markdownify.readthedocs.io/en/latest/settings.html










