Admin Guide
===========


.. _label-admin-quickstart:
Admin Quickstart
~~~~~~~~~~~~~~~~

The final steps to getting your new WikiWikWeb functioning can be performed in the Django admin:

1) Create at least one WikiSpace. The name should conform to the :ref:`label-user-wikiname` conventions.

2) Create at least one WikiPage within each WikiSpace. The name **must** conform to the :ref:`label-user-wikiname` conventions, otherwise the WikiPage will not be linkable.

3) For each WikiSpace created, assign one page as the home page. This page is displayed embedded with the WikiSpace start page. It is the first thng user see when entering the WikiSpace, and is editable just like any other WikiPage.

Any further pages will be created by users simply by linking to them using :ref:`label-user-wikiname`.