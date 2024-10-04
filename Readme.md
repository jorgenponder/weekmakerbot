= Purpose =

To upload week templates to a mediawiki site for pages that are stored in the cargo system. But it should work with any pages you want to upload, cargo or not.


= Install =

Install:

    pip install mwclient

= Config =

A file ```pages.py``` should contain a list of dictionaries of the pages (week templates) to upload. See ```pages.py.example``` for an example of the format. It contains a list of two dictionaries, i.e. of two pages.

Change the credentials in templatesuploader.py to fit the site's settings.

= History =

This task used to be done with pywikibot instead of mwclient, but it was just to complex to remember and handle.
