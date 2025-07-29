from django.contrib.auth.models import User
from django.test import TestCase

from wikiwikiweb.models import WikiPage, WikiSpace


class TrivialModelTestCase(TestCase):

    fixtures = ['basic-db.json']

    def test_I_exist(self):
        self.assertEqual(1+2, 3)

    def test_to_str(self):

        user = User.objects.create_user(username='zebedee')

        wikiname = 'LedZeppelin'

        space = WikiSpace.objects.create(name=wikiname)
        self.assertEqual(space.__str__(), wikiname)

        page = WikiPage.objects.create(name=wikiname, space=space, created_by=user, updated_by=user)
        self.assertEqual(page.__str__(), wikiname)
