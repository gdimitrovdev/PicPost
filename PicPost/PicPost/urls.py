from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    #redirect to urls.py in App folder on load
    path('', include('App.urls')),
]
