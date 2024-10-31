from django.urls import path
from info.views import place_photo
from info.views import add_to_itinerary, remove_from_itinerary, itinerary_page

urlpatterns = [
    path("place/photo", place_photo, name="place_photo"),
    path('itinerary/add/<str:city>/<str:spot_name>/<str:address>/<str:category>/', add_to_itinerary, name='add_to_itinerary'),
    path('itinerary/remove/<str:city>/<str:spot_name>/', remove_from_itinerary, name='remove_from_itinerary'),
    path('itinerary/', itinerary_page, name='itinerary_page'),
]

