User Guide
==========


.. _label-user-markdown:
Markdown
^^^^^^^^

WikiPages are formatted using Markdown. Markdown is simple, widely-used and well documented markup language designed to make it easy to create HTML pages. There are many Markdown references online, for example https://www.markdownguide.org/basic-syntax/

``django-wikiwikiweb`` uses one extra bit of syntax to make things work, which is that if you enter a word conforming to :ref:`label-user-wikiname`, it will automatically become a link.

To create a WikiPage, simply mention it in your page text, and ``django-wikiwikiweb`` will convert it into a link. Once a user clicks the link, if the WikiPage has yet to have any content aded, the edit form will be shown instead of any page content, thereby inviting the reader to contribute.

To "delete" a WikiPage, simply stop linking to it.



.. _label-user-wikiname:
WikiName Syntax
^^^^^^^^^^^^^^^

To follow in greater detail, but:

i) begins with an upper case letter
ii) must contain at least one further upper case letter
iii) consists of only upper case letters, lower case letters, and numbers

Examples of good WikiNames are **WikiName**, **WikiPage** and **ThatSortOfThing** .
