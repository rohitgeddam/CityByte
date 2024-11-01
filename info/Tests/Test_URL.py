from django.test import SimpleTestCase
from django.urls import reverse, resolve
from info.views import profile_page


class TestUrls(SimpleTestCase):
    """
    Test URL resolution for the 'info' application.
    """
    def test_profile_page(self):
        """
        Test that the 'profile_page' URL resolves to the correct view.
        """
        url = reverse("profile_page")
        self.assertEquals(resolve(url).func, profile_page)
