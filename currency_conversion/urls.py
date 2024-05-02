# currency_conversion/urls.py

from django.urls import path
from . import views
from .views import conversion

urlpatterns = [
    path('<str:currency1>/<str:currency2>/<int:amount_of_currency1>/', views.conversion, name='conversion'),
]
