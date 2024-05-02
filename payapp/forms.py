# payapp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from register.models import UserProfile
from .models import Transaction, MoneyRequest
from django import forms
from django.contrib.auth.forms import UserCreationForm
from register.models import UserProfile
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    currency = forms.ChoiceField(choices=UserProfile.CURRENCY_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'currency')


class TransactionForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(queryset=User.objects.none())

    class Meta:
        model = Transaction
        fields = ['recipient', 'amount']

    def __init__(self, *args, user=None, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['recipient'].queryset = User.objects.exclude(username=user.username)


class MoneyRequestForm(forms.ModelForm):
    class Meta:
        model = MoneyRequest
        fields = ['recipient', 'amount', 'reason']

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('user', None)
        super(MoneyRequestForm, self).__init__(*args, **kwargs)
        if self.sender is not None:
            self.fields['recipient'].queryset = User.objects.exclude(id=self.sender.id)

    def save(self, commit=True):
        money_request = super(MoneyRequestForm, self).save(commit=False)
        money_request.sender = self.sender
        if commit:
            money_request.save()
        return money_request


class AdminRegistrationForm(UserCreationForm):
    currency = forms.ChoiceField(choices=UserProfile.CURRENCY_CHOICES)

    class Meta:
        model = User
        fields = ('username','email', 'password1', 'password2')
