from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    CURRENCY_CHOICES = (
        ('GBP', 'Pound'),
        ('USD', 'Dollar'),
        ('EUR', 'Euro'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')

    def __str__(self):
        return self.user.username
