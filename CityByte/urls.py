from django.contrib import admin
from django.urls import path, include
from search.views import main_page
from info.views import info_page, profile_page, addTofav
from .views import SignUpView
from . import views

urlpatterns = [
    path("", main_page, name="main_page"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("accounts/login/", views.sign_in, name="sign_in"),
    path("sign-out/", views.sign_out, name="sign_out"),
    path("auth-receiver", views.auth_receiver, name="auth_receiver"),
    path("profile/", profile_page, name="profile_page"),
    path("city", info_page, name="info_page"),
    path("admin/", admin.site.urls),
    path("api/search/", include(("search.urls", "search"), namespace="search")),
    path("api/info/", include(("info.urls", "info"), namespace="info")),
    path("api/addToFav/", addTofav, name="addToFav"),
]
