#-----------------------[Import Model]-------------------#
import pyotp
import requests
import time
import os
from django.core.cache import cache
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login  as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import *
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse , HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.views.decorators.http import require_http_methods
from .models import *
#------------[costum user model]------------#
user = get_user_model

#------------[Custom User Model]-------------#
class CustomUser(AbstractUser):
    number = models.CharField(max_length=10, unique=True)
    otp_key = models.CharField(max_length=32, blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.otp_key:
            self.otp_key = pyotp.random_base32()  # Generate a new OTP key for the user
        super().save(*args, **kwargs)
#----------------------[Generate OTP]------------------#
def generate_otp(user):
    totp = pyotp.TOTP(user.otp_key)
    return totp.now()  # Generate a new OTP
#-------------[OTP Verification]-------------#
def otp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        if cache.get(f'otp_attempt_{otp}'):
            messages.error(request, "Please wait 2 minutes before requesting a new OTP.")
            return render(request, 'login.html')

        try:
            user = CustomUser.objects.get(otp_key=otp)  # Check if OTP exists
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            return render(request, 'otp.html')

        # Generate and send OTP
        user_otp = generate_otp(user)
        # send_sms(user.number, user_otp)  # Uncomment and implement the send_sms function

        messages.success(request, "OTP has been sent successfully.")
    return render(request, 'otp.html')

#----------------[Login Function]----------------#
def login(request):
    if request.method == "POST":
        number = request.POST.get("number")
        password = request.POST.get("password")
        user = authenticate(request, username=number, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful.")
            return redirect("dashboard")  # Change to your home page
        else:
            messages.error(request, "Error while logging in.")
            return redirect("login")

    return render(request, 'login.html')

#-----------------[Register Function]----------------#
def register(request):
    if request.method == "POST":
        number = request.POST.get("number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if CustomUser.objects.filter(number=number).exists():
            messages.error(request, "This number is already registered. Use another number.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        user = CustomUser.objects.create_user(username=number, password=password, number=number)
        user.save()
        messages.success(request, "Registration successful. You can now log in.")
        return redirect("login")

    return render(request, 'register.html')

#-------------[Logout Function]----------------#
def logout_view(request):
    auth_logout(request)
    return JsonResponse({"status": "You have successfully logged out."})