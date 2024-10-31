from urllib import request
from django.test import TestCase
from info.helpers.places import FourSquarePlacesHelper
from django.shortcuts import render
from info.helpers.weather import WeatherBitHelper
from datetime import datetime
import pytz
from info.models import Comment
from info.forms import CommentForm
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from search.helpers.photo import UnplashCityPhotoHelper
from urllib.request import urlopen



from info.models import ItineraryItem
from django.utils import timezone  # Added import for timezone
image_formats = ("image/png", "image/jpeg", "image/gif")



class ItineraryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="Test@123"
        )
        self.client.login(username="testuser", password="Test@123")
        self.city = "Hyderabad"
        self.spot_name = "Charminar"
        self.address = "Old City, Hyderabad 500002, Telangana"
        self.category = "Monument"

    def test_add_to_itinerary(self):
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ItineraryItem.objects.count(), 1)
        item = ItineraryItem.objects.first()
        self.assertEqual(item.user, self.user)
        self.assertEqual(item.city, self.city)
        self.assertEqual(item.spot_name, self.spot_name)
        self.assertEqual(item.address, self.address)
        self.assertEqual(item.category, self.category)

    def test_add_duplicate_to_itinerary(self):
        self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ItineraryItem.objects.count(), 1)
        self.assertContains(response, 'Already in itinerary.')

    def test_remove_from_itinerary(self):
        self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        response = self.client.post(reverse('info:remove_from_itinerary', args=[self.city, self.spot_name]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ItineraryItem.objects.count(), 0)
        self.assertContains(response, 'Removed from itinerary.')

    def test_add_multiple_items_to_itinerary(self):
        spots = [
            {"name": "KBR Park", "address": "Kbr National Park (LV Prasad Marg), Hyderabad 591226, Telangana", "category": "Park"},
            {"name": "Tank Bund", "address": "Lumbani Park, Hyderabad 472708, Telangana", "category": "Landmarks and Outdoors"},
            {"name": "Chowmahala Palace", "address": "Moti Gali, Hyderabad, Telangana", "category": "History Museum"},
        ]

        for spot in spots:
            response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, spot["name"], spot["address"], spot["category"]]))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Added to itinerary.')

        self.assertEqual(ItineraryItem.objects.count(), len(spots))
    
    def test_itinerary_item_addition_invalid_city(self):
        """Test adding an itinerary item with an invalid (empty) spot name."""
        response = self.client.post(reverse('info:add_to_itinerary', args=['Hyderabad', self.spot_name, self.address, self.category]), {
            'city': '' , 
            'address': self.address,
            'category': self.category,
        })
        self.assertEqual(response.status_code, 400)

    def test_remove_multiple_items(self):
        self.client.post(reverse('info:add_to_itinerary', args=[self.city, "KBR Park", self.address, self.category]))
        self.client.post(reverse('info:add_to_itinerary', args=[self.city, "Tank Bund", self.address, self.category]))

        response = self.client.post(reverse('info:remove_from_itinerary', args=[self.city, "KBR Park"]))
        self.assertContains(response, 'Removed from itinerary.')
        self.assertEqual(ItineraryItem.objects.count(), 1)

        response = self.client.post(reverse('info:remove_from_itinerary', args=[self.city, "Tank Bund"]))
        self.assertContains(response, 'Removed from itinerary.')
        self.assertEqual(ItineraryItem.objects.count(), 0)

    def test_itinerary_item_fields(self):
        self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        item = ItineraryItem.objects.first()
        self.assertEqual(item.user, self.user)
        self.assertEqual(item.city, self.city)
        self.assertEqual(item.spot_name, self.spot_name)
        self.assertEqual(item.address, self.address)
        self.assertEqual(item.category, self.category)

    def test_itinerary_item_addition_invalid_category(self):
        """Test adding an itinerary item with an invalid (empty) spot name."""
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, 'Park']), {
            'city': self.city , 
            'address': self.address,
            'category': '',
        })
        self.assertEqual(response.status_code, 400)

    def test_add_to_itinerary_without_login(self):
        self.client.logout()
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        self.assertEqual(response.status_code, 302)

    def test_remove_from_itinerary_without_login(self):
        self.client.logout()
        response = self.client.post(reverse('info:remove_from_itinerary', args=[self.city, self.spot_name]))
        self.assertEqual(response.status_code, 302)

    def test_view_itinerary_page(self):
        response = self.client.get(reverse('info:itinerary_page'))
        self.assertEqual(response.status_code, 200)


    def test_itinerary_item_uniqueness_per_user(self):
        self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))

        # Log out the first user
        self.client.logout()

        # Create a new user
        new_user = get_user_model().objects.create_user(username="user2", password="Test@123")
        self.client.login(username="user2", password="Test@123")

        # New user tries to add the same item
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        
        # Check if the new user was able to add the item (it should be allowed)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Added to itinerary.')
        self.assertEqual(ItineraryItem.objects.count(), 2)  # Now there should be 2 items: one for each user

    def test_itinerary_item_string_representation(self):
        item = ItineraryItem.objects.create(
            user=self.user,
            city=self.city,
            spot_name=self.spot_name,
            address=self.address,
            category=self.category,
        )
        self.assertEqual(str(item), f"{self.spot_name} in {self.city} - {self.user.username}")

    def test_itinerary_item_addition_invalid_address(self):
        """Test adding an itinerary item with an invalid (empty) spot name."""
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, 'Kbr National Park (LV Prasad Marg), Hyderabad 591226, Telangana',self.category ]), {
            'city': self.city , 
            'address': '',
            'category': self.category,
        })
        self.assertEqual(response.status_code, 400)

    def test_added_on_field(self):
        item = ItineraryItem.objects.create(
            user=self.user,
            city=self.city,
            spot_name=self.spot_name,
            address=self.address,
            category=self.category,
        )
        self.assertIsNotNone(item.added_on)
        self.assertTrue(item.added_on <= timezone.now())

    def test_itinerary_item_count(self):
        # Check that a user can have multiple unique items
        for i in range(3):
            self.client.post(reverse('info:add_to_itinerary', args=[self.city, f"Spot {i}", self.address, self.category]))
        self.assertEqual(ItineraryItem.objects.count(), 3)  # Original + 3 new

    def test_itinerary_item_category(self):
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, 'New Category']))
        item = ItineraryItem.objects.first()
        self.assertEqual(item.category, 'New Category')

    def test_itinerary_with_different_users(self):
        self.client.post(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))

        self.client.logout()
        new_user = get_user_model().objects.create_user(username="user3", password="Test@123")
        self.client.login(username="user3", password="Test@123")

        self.client.post(reverse('info:add_to_itinerary', args=[self.city, "New Spot", self.address, self.category]))

        self.assertEqual(ItineraryItem.objects.filter(user=self.user).count(), 1)
        self.assertEqual(ItineraryItem.objects.filter(user=new_user).count(), 1)

    def test_itinerary_item_addition_invalid_spot_name(self):
        """Test adding an itinerary item with an invalid (empty) spot name."""
        response = self.client.post(reverse('info:add_to_itinerary', args=[self.city, 'KBR Park', self.address, self.category]), {
            'spot_name': '', 
            'address': self.address,
            'category': self.category,
        })
        self.assertEqual(response.status_code, 400)
    
    def test_remove_itinerary_invalid_method(self):
        """Test removing an itinerary item with an invalid (non-POST) request method."""
        response = self.client.get(reverse('info:add_to_itinerary', args=[self.city, self.spot_name, self.address, self.category]))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(str(response.content, encoding='utf-8'), {'error': 'Invalid request method.'})
    
    
    
