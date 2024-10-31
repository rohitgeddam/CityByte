import os
import time

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@csrf_exempt
def sign_in(request):
    return render(request, "login.html")


@csrf_exempt
def auth_receiver(request):
    print(request.POST)
    token = request.POST["credential"]

    time.sleep(1)  # delay is needed in order to ensure creation of token before retrieving user's data

    try:
        user_data = id_token.verify_oauth2_token(token, requests.Request(), os.environ["GOOGLE_OAUTH2_ID"])
    except ValueError:
        return HttpResponse(status=403)

    # Get the user's email, first, and last name
    email = user_data.get("email")
    first_name = user_data.get("given_name")
    last_name = user_data.get("family_name")

    # Get or create the user
    user, created = User.objects.get_or_create(
        username=email, defaults={"email": email, "first_name": first_name, "last_name": last_name}
    )

    #  Log the user in
    login(request, user)
    request.session["user_data"] = user_data

    return redirect("main_page")


def sign_out(request):
    try:
        del request.session["user_data"]
    except Exception as e:
        print(f"Error Logging Out - Exception: {e}")

    try:
        logout(request)
    except Exception as e:
        print(f"Error Logging Out 2 - Exception: {e}")

    return redirect("sign_in")
