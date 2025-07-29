import re
from unittest import TestCase

# from django.test import TestCase

from wikiwikiweb.templatetags import wiki_extras


class LinkifyTestCase(TestCase):


    def setUp(self):
        self.tomatch = wiki_extras.FMT_WIKINAME


    def test_regex(self):
        """Test the regex independently of the code"""

        self.assertFalse(re.search(self.tomatch, ''))
        self.assertFalse(re.search(self.tomatch, 'hello world'))
        self.assertFalse(re.search(self.tomatch, 'hello worldOnAString'))

        self.assertTrue(re.search(self.tomatch, 'WikiName'))
        self.assertTrue(re.search(self.tomatch, 'this page has a WikiName in it'))
        self.assertTrue(re.search(self.tomatch, 'this WikiPage has two WikiNames in it'))

        self.assertEqual(re.findall(self.tomatch, 'WikiName'), ['WikiName'])
        self.assertEqual(re.findall(self.tomatch, 'this WikiPage has two WikiNames in it'), ['WikiPage', 'WikiNames'])


    def test_cannot_start_with_numbers(self):
        self.assertFalse(re.search(self.tomatch, 'hello 333WorldOnAString'))

    # I'll leave this for now. I'm not convinced it's a problem
    #def test_each_capital_letter_must_be_followed_by_a_lower_case_letter(self):
    #    self.assertFalse(re.search(self.tomatch, 'WhyUsePHP'));

    def test_linkify(self):
        self.assertFalse(self._is_linked(wiki_extras.linkify(''), 'whatever'))
        self.assertTrue(self._is_linked(wiki_extras.linkify('WikiPage'), 'WikiPage'))
        self.assertTrue(self._is_linked(
                wiki_extras.linkify('This is some text linking to WikiOtherPage somehow'),
                'WikiOtherPage')
            )


    def test_youtube_urls_unmolested(self):
        """YouTube vid IDs starting with upper case were erroneously linked"""

        youtube_url = 'https://www.youtube.com/watch?v=DVPab4bTGqY'

        self.assertFalse(re.search(self.tomatch, youtube_url))
        self.assertEqual(wiki_extras.linkify(youtube_url), youtube_url)

        self.assertFalse(self._is_linked(
                wiki_extras.linkify('https://www.youtube.com/watch?v=DVPab4bTGqY'),
                'DVPab4bTGqY')
            )

    def test_facebook_urls_unmolested(self):
        """See issue #34"""

        facebook_url ='https://www.facebook.com/TheBullincolchester'

        self.assertFalse(re.search(self.tomatch, facebook_url))
        self.assertEqual(wiki_extras.linkify(facebook_url), facebook_url)

        self.assertFalse(self._is_linked(
                wiki_extras.linkify('https://www.youtube.com/watch?v=DVPab4bTGqY'),
                'DVPab4bTGqY')
            )


    def _is_linked(self, html, wikiname):
        """Don't get too specific about the HTML - that could get fragile"""

        return ('href="' in html
                and 'wikilink' in html
                and 'href="'  in html
                and '>' + wikiname + '</a>' in html)
