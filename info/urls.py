from django.urls import path
from info.views import place_photo
from info.views import add_to_itinerary, remove_from_itinerary, itinerary_page

urlpatterns = [

    # URL pattern for viewing or uploading a photo of a place, mapped to the place_photo view
    path("place/photo", place_photo, name="place_photo"),

    # URL pattern for adding a place to the itinerary with dynamic parameters for city, spot_name, address, and category
    path('itinerary/add/<str:city>/<str:spot_name>/<str:address>/<str:category>/', add_to_itinerary, name='add_to_itinerary'),
    
    # URL pattern for removing a place from the itinerary, requiring the city and spot_name as parameters
    path('itinerary/remove/<str:city>/<str:spot_name>/', remove_from_itinerary, name='remove_from_itinerary'),
    
    # URL pattern to view the full itinerary, routed to the itinerary_page view
    path('itinerary/', itinerary_page, name='itinerary_page'),
]

