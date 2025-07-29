"""
Various web page clicks

TODO:
 - This will grow rapidly, so look into ways of splitting up
 - The hardcoded URLs are fragile
"""

from django.contrib.auth.models import User
from django.test import TestCase

from wikiwikiweb.models import WikiPage


class TestBasicCalls(TestCase):
    """General control flow through site"""

    # TODO: can we move the files nearer?
    fixtures = ['basic-db.json']

    #
    # Potential TODO:
    #  - force Space for create page - done but lacks test
    #  - check rev matches WikiName for archive stuff (not urgent, just seems odd right now) See #11
    #  -
    #

    def setUp(self):
        self._test_user = 'testuser'
        self._test_pass = 'testpass123'
        self._sess_key_space = 'sess_space_key'

    # Home page ---------------------------------------------------------------

    def test_homepage_load(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/home.html')

    # WikiPage pages-----------------------------------------------------------

    # View page

    def test_success_for_real_wikipage(self):
        response = self.client.get('/AvrilLavigne')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page.html')

    # Create page

    def test_require_login_for_create_not_logged_in(self):
        response = self.client.get('/ThisNoExist')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                        '/accounts/login/?next=/ThisNoExist', # Seems fragile
                        fetch_redirect_response=False)

    def test_get_create_form_if_logged_in(self):
        self._populate_session()

        response = self.client.get('/ImaginaryPage')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page_create.html')

    # TODO: test invalid form data

    def test_create_form_post(self):
        self._populate_session()

        newpagename = 'MyNewPage' # nb. not in fixture db

        # nb. 'name' will soon be retired, see #18
        formdata = {'name': 'This name is a red herring',
                    'content': 'Some page content',
                    'edit_reason': 'Created1'}

        newpageurl = '/' + newpagename

        response = self.client.post(newpageurl, data=formdata)
        self.assertRedirects(response,
                        newpageurl + '?success=created',
                        fetch_redirect_response=False)

        newpage = WikiPage.objects.get(pk=newpagename)

        self.assertEqual(newpage.created_by, self._get_user(self._test_user))
        self.assertEqual(newpage.updated_by, self._get_user(self._test_user))

    # Edit page

    def test_get_edit_form_if_logged_in(self):
        self._populate_session()

        response = self.client.get('/AvrilLavigne/edit')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page_edit.html')

    def test_edit_form_post(self):
        self._populate_session()

        editpagename = 'JoniMitchell' # nb. is in fixture db; created by user 4/otheruser

        formdata = {
                    'content': 'Some edited page content',
                    'edit_reason': 'Edited1'
                    }

        viewpageurl = '/' + editpagename
        editpageurl = viewpageurl + '/edit'

        response = self.client.post(editpageurl, data=formdata)
        self.assertRedirects(response,
                            viewpageurl + '?success=updated',
                            fetch_redirect_response=False)

        newpage = WikiPage.objects.get(pk=editpagename)

        # check this hasn't changed...
        self.assertEqual(newpage.created_by, self._get_user('otheruser'))

        # ...but this has
        self.assertEqual(newpage.updated_by, self._get_user(self._test_user))

    # Archive pages -----------------------------------------------------------

    def test_success_for_real_archivepage(self):
        """Checks for #22"""

        response = self.client.get('/JacksonBrowne/86')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/wiki_page_archive.html')

    def test_for_mismatched_revision_id(self):
        """Checks for #11"""

        # 86 would be JacksonBrowne, not AvriLavigne
        response = self.client.get('/AvriLavigne/86')
        self.assertEqual(response.status_code, 404)

    # WikiSpace pages ---------------------------------------------------------

    def test_success_for_real_wikispace(self):
        response = self.client.get('/space:ThreeHundredSongs')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/space.html')

    def test_selectspace_form_post(self):

        session = self.client.session
        self.assertFalse(session.get(self._sess_key_space))

        targetpage = '/search?q=Kylie'
        selectpage = '/space/select'

        formdata = {
                    'space_choice': 1,
                    'next': targetpage
                }

        response = self.client.post(selectpage, data=formdata)
        self.assertRedirects(response,
                        targetpage,
                        fetch_redirect_response=False)

    # Search page -------------------------------------------------------------

    def test_request_search_with_space_in_session(self):

        self._populate_session()

        response = self.client.get('/search?q=avril')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/search.html')

    def test_request_search_with_no_space(self):

        session = self.client.session
        self.assertFalse(session.get(self._sess_key_space))

        response = self.client.get('/search?q=Avril+Lavigne')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/space/select?next=/search?q=Avril+Lavigne')

    # User page ---------------------------------------------------------------

    def test_success_for_real_userpage(self):
        response = self.client.get('/user:testuser')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wiki/user.html')

    # Private methods ----------------------------------------------------------

    def _populate_session(self):
        """Ensure user logged in, and valid WikiSpace in session"""

        self.client.login(username=self._test_user, password=self._test_pass)

        session = self.client.session
        session[self._sess_key_space] = 'ThreeHundredSongs'
        session.save()

    def _get_user(self, username):
        return User.objects.get(username=username)
