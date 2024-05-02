from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm
from .models import UserProfile



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            currency = form.cleaned_data.get('currency')
            UserProfile.objects.create(user=user, currency=currency)

            login(request, user)
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register/register.html', {'form': form})
