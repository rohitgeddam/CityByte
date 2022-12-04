import datetime

import pytz
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from info.helpers.places import FourSquarePlacesHelper
from info.helpers.weather import WeatherBitHelper
from search.helpers.photo import UnplashCityPhotoHelper
from suntime import Sun
from geopy.geocoders import Nominatim


@require_http_methods(["GET"])
def place_photo(request):
    photo_link = FourSquarePlacesHelper().get_place_photo(fsq_id=request.GET.get('fsq_id'))
    return redirect(photo_link)


@require_http_methods(["GET"])
def info_page(request):
    city = request.GET.get("city")
    country = request.GET.get("country")
    
    try:

        weather_info = WeatherBitHelper().get_city_weather(city=city, country=country)["data"][0]
        weather_info["ts"] = datetime.fromtimestamp(weather_info["ts"]).strftime("%m-%d-%Y, %H:%M")
    except:
        weather_info = {}

    geolocator = Nominatim(user_agent="geoapiExercises")
    place = city
    location = geolocator.geocode(place)
    latitude = location.latitude
    longitude = location.longitude
    sun = Sun(latitude, longitude)
    # time_zone = datetime.date(2022, 2,28)
    time_zone = datetime.date.today()
    # time_zone = today.strftime("%Y-%d-%m")
    print("fef",time_zone)
    try:
        sun_rise = sun.get_local_sunrise_time(time_zone)
        sun_dusk = sun.get_local_sunset_time(time_zone)
        weather_info["sunrise"]=sun_rise.strftime('%I:%M')
        weather_info["sunset"]=sun_dusk.strftime('%I:%M')
    except:
        print("No Sunrise and Sunset")
    
    dining_info = FourSquarePlacesHelper().get_places(
        city=f"{city}, {country}", categories="13065", sort="RELEVANCE", limit=5)
    airport_info = FourSquarePlacesHelper().get_places(
        city=f"{city}, {country}", categories="19040", sort="RELEVANCE", limit=5)
    outdoor_info = FourSquarePlacesHelper().get_places(
        city=f"{city}, {country}", categories="16000", sort="RELEVANCE", limit=5)
    arts_info = FourSquarePlacesHelper().get_places(
        city=f"{city}, {country}", categories="10000", sort="RELEVANCE", limit=5)

    photo_link = UnplashCityPhotoHelper().get_city_photo(city=city)

    # print(dining_info)
    return render(
        request, 'search/city_info.html',
        context={
            "weather_info": weather_info,
            "dining_info": dining_info,
            "airport_info": airport_info,
            "outdoor_info": outdoor_info,
            "arts_info": arts_info,
            "photo_link": photo_link,
        }
    )
