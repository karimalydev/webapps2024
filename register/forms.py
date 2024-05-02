from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    currency = forms.ChoiceField(choices=UserProfile.CURRENCY_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'currency')
