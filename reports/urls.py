# reports/urls.py
from django.urls import path
from .views import build_master

urlpatterns = [
    path('build-master/', build_master, name='build_master'),
]