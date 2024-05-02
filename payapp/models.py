from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Transaction(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3, choices=[('GBP', 'Pound'), ('USD', 'Dollar'), ('EUR', 'Euro')])
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conversion_rate = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    converted_currency = models.CharField(max_length=3, null=True, blank=True)

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount} {self.currency}"


class MoneyRequest(models.Model):
    sender = models.ForeignKey(User, related_name='money_requests_made', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='money_requests_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=
    (('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.username} requests {self.amount} from {self.receiver.username}"
