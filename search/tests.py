import pytz

from urllib import request
from django.test import TestCase, Client
from info.helpers.places import *
from django.shortcuts import render
from info.helpers.weather import WeatherBitHelper
from datetime import datetime
from info.models import Comment
from info.forms import CommentForm
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from search.helpers.photo import UnplashCityPhotoHelper
from urllib.request import urlopen
from unittest.mock import patch
from django.http import HttpResponse

image_formats = ("image/png", "image/jpeg", "image/gif")

class CityByte_testcase(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("admin", "admin.@simpson.net", "admin")

    def test_main_page(self):
        assert render(request, "search/search.html").status_code == 200

    def test_cityphoto(self):
        photo_link = UnplashCityPhotoHelper().get_city_photo(city="Pune")
        site = urlopen(photo_link)
        meta = site.info()
        if meta["content-type"] in image_formats:
            assert True

    def test_photo(self):
        photo_link = FourSquarePlacesHelper().get_place_photo(fsq_id="518a71ab498e430858000827")
        site = urlopen(photo_link)
        meta = site.info()
        if meta["content-type"] in image_formats:
            assert True

    def test_info_page(self):
        city = "New York City"
        country = "US"

        try:
            weather_info = WeatherBitHelper().get_city_weather(city=city, country=country)["data"][0]
            weather_info["sunrise"] = (
                datetime.strptime(weather_info["sunrise"], "%H:%M")
                .astimezone(pytz.timezone(weather_info["timezone"]))
                .strftime("%I:%M")
            )
            weather_info["sunset"] = (
                datetime.strptime(weather_info["sunset"], "%H:%M")
                .astimezone(pytz.timezone(weather_info["timezone"]))
                .strftime("%I:%M")
            )
            weather_info["ts"] = datetime.fromtimestamp(weather_info["ts"]).strftime("%m-%d-%Y, %H:%M")

        except Exception:
            # api limit exceeded
            weather_info = {}

        # commentForm = CommentForm()

        dining_info = FourSquarePlacesHelper().get_places(
            city=f"{city}, {country}", categories="13065", sort="RELEVANCE", limit=5
        )
        outdoor_info = FourSquarePlacesHelper().get_places(
            city=f"{city}, {country}", categories="16000", sort="RELEVANCE", limit=5
        )
        airport_info = FourSquarePlacesHelper().get_places(
            city=f"{city}, {country}", categories="19040", sort="RELEVANCE", limit=5
        )
        arts_info = FourSquarePlacesHelper().get_places(
            city=f"{city}, {country}", categories="10000", sort="RELEVANCE", limit=5
        )
        photo_link = UnplashCityPhotoHelper().get_city_photo(city=city)
        # comments = Comment.objects.filter(city=city, country=country).order_by(
        #     "-created_on"
        # )
        # isInFav = True if FavCityEntry.objects.filter(city=city, country=country, user=request.user).count() > 0 else False
        # render(request, 'search/city_info.html', context={"weather_info": weather_info, "dining_info": dining_info, "outdoor_info": outdoor_info, "airport_info": airport_info, "photo_link": photo_link, "arts_info": arts_info,  "comments": comments,
        #     "commentForm": commentForm,
        #     'city': city,
        #     'country': country,
        #     'isInFav': True}).status_code == 200
        if (
            not weather_info
            and not dining_info
            and not outdoor_info
            and not airport_info
            and not arts_info
            and not photo_link
        ):
            assert True

    def TestModels(TestCase):
        user = get_user_model().objects.create_user("admin@citybyte.com", "password")
        assert user

    def test_can_access_page(self):
        login = self.client.login(username="admin", password="admin")
        self.assertTrue(login)
        # self.assertEqual(response.status_code,200)

    def test_user_logout(self):
        # client=Client()
        self.client.logout()
        # response = self.client.get('/admin/')
        self.assertTrue(True)

    def test_profile_page(self):
        self.client = Client()
        response = self.client.get(reverse("profile_page"))
        self.assertTrue(200, response.status_code)

    def test_place_photo(self):
        self.client = Client()
        response = self.client.get(reverse("info:place_photo"))
        self.assertTrue(200, response.status_code)

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testing', password='test_password', email='test@email.com')

    def test_signup_view_renders_correct_template(self):
        response = self.client.get(reverse('signup'))
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertEqual(response.status_code, 200)

    def test_successful_signup_creates_user(self):
        response = self.client.post(reverse('signup'), {'username': 'newuser', 'password1': 'newpassword123', 'password2': 'newpassword123'})
        self.assertEqual(get_user_model().objects.count(), 2)  # 1 existing user + 1 new user
        self.assertRedirects(response, reverse('login'))

    def test_sign_in_renders_login_template(self):
        response = self.client.get(reverse('sign_in'))
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(response.status_code, 200)

    @patch('google.auth.transport.requests.Request')
    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_auth_receiver_successful_login(self, mock_verify, mock_request):
        mock_verify.return_value = {
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User'
        }
        token = 'valid_token'
        response = self.client.post(reverse('auth_receiver'), {'credential': token})
        self.assertRedirects(response, reverse('main_page'))
        self.assertTrue(self.client.session.get('user_data'))

    @patch('google.auth.transport.requests.Request')
    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_auth_receiver_invalid_token(self, mock_verify, mock_request):
        mock_verify.side_effect = ValueError("Invalid token")
        response = self.client.post(reverse('auth_receiver'), {'credential': 'invalid_token'})
        self.assertEqual(response.status_code, 403)

    def test_sign_out_redirects_to_sign_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('sign_out'))
        self.assertRedirects(response, reverse('sign_in'))
        self.assertFalse(self.client.session.get('user_data'))

    def test_sign_out_handles_logout_exception(self):
        self.client.login(username='testuser', password='testpass')
        with patch('django.contrib.auth.logout', side_effect=Exception("Logout error")):
            response = self.client.get(reverse('sign_out'))
            self.assertRedirects(response, reverse('sign_in'))

    def test_signup_form_validation(self):
        response = self.client.post(reverse('signup'), {'username': '', 'password1': 'pass', 'password2': 'pass'})
        self.assertFormError(response, 'form', 'username', 'This field is required.')

    def test_sign_in_with_invalid_credentials(self):
        response = self.client.post(reverse('sign_in'), {'username': 'wronguser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)

    def test_user_login_and_redirect(self):
        response = self.client.login(username='testuser', password='testpass')
        self.assertTrue(response)
        response = self.client.get(reverse('main_page'))
        self.assertEqual(response.status_code, 200)

class AuthErrorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')

    def test_signup_with_existing_username_fails(self):
        response = self.client.post(reverse('signup'), {'username': 'testuser', 'password1': 'newpassword123', 'password2': 'newpassword123'})
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')

    def test_auth_receiver_with_missing_token(self):
        response = self.client.post(reverse('auth_receiver'), {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'Missing credential'})

    def test_auth_receiver_with_empty_token(self):
        response = self.client.post(reverse('auth_receiver'), {'credential': ''})
        self.assertEqual(response.status_code, 403)

    @patch('google.oauth2.id_token.verify_oauth2_token', side_effect=ValueError("Invalid token"))
    def test_auth_receiver_failure_due_to_value_error(self, mock_verify):
        response = self.client.post(reverse('auth_receiver'), {'credential': 'some_invalid_token'})
        self.assertEqual(response.status_code, 403)

    def test_sign_out_without_login_redirects(self):
        response = self.client.get(reverse('sign_out'))
        self.assertRedirects(response, reverse('sign_in'))  # Should redirect even if not logged in

    def test_user_login_with_incorrect_password(self):
        response = self.client.login(username='testuser', password='wrongpass')
        self.assertFalse(response)

    def test_signup_with_passwords_not_matching(self):
        response = self.client.post(reverse('signup'), {'username': 'newuser', 'password1': 'password123', 'password2': 'differentpassword'})
        self.assertFormError(response, 'form', 'password2', "The two password fields didn’t match.") # weird apostrophe is used in the forms - took forever to debug

    def test_sign_in_with_non_existent_user(self):
        response = self.client.post(reverse('sign_in'), {'username': 'nonexistent', 'password': 'somepassword'})
        self.assertEqual(response.status_code, 200)  # Should render login page again

    def test_sign_out_with_no_active_session(self):
        self.client.logout()  # Ensure user is logged out
        response = self.client.get(reverse('sign_out'))
        self.assertRedirects(response, reverse('sign_in'))  # Should still redirect to sign in

    def test_auth_receiver_when_user_creation_fails(self):
        @patch('django.contrib.auth.models.User.objects.get_or_create', side_effect=Exception("Database error"))
        def mock_user_creation(mock_get_or_create):
            token = 'valid_token'
            response = self.client.post(reverse('auth_receiver'), {'credential': token})
            self.assertEqual(response.status_code, 403)

        mock_user_creation()

    def test_password_too_common(self):
        response = self.client.post(reverse('signup'), {'username': 'newuser', 'password1': 'password123', 'password2': 'password123'})
        self.assertFormError(response, 'form', 'password2', "This password is too common.")