from django.contrib import admin
from .models import CitySearchRecord, Comment, FavCityEntry


# Registering models to make them accessible in the Django admin interface
admin.site.register(CitySearchRecord)
admin.site.register(FavCityEntry)
admin.site.register(Comment)
