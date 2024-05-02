import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction as db_transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from register.models import UserProfile
from .models import Transaction, MoneyRequest
from .forms import TransactionForm, MoneyRequestForm, AdminRegistrationForm
from decimal import Decimal
from django.contrib.auth.models import User
import thriftpy2

timestamp_thrift = thriftpy2.load("timestamp_service.thrift", module_name="timestamp_thrift")
from thriftpy2.rpc import make_client


@login_required
def transfer_money(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            with db_transaction.atomic():
                sender_profile = request.user.userprofile
                recipient = form.cleaned_data['recipient']
                recipient_profile = recipient.userprofile
                amount = form.cleaned_data['amount']

                if sender_profile.balance >= amount:
                    if sender_profile.currency != recipient_profile.currency:
                        # Call the conversion service
                        conversion_url = f"https://127.0.0.1:8000/conversion/{sender_profile.currency}/{recipient_profile.currency}/{amount}/"
                        response = requests.get(conversion_url, verify=False)
                        if response.status_code == 200:
                            data = response.json()
                            converted_amount = data['converted_amount']
                            conversion_rate = data['rate']
                        else:
                            # Handle conversion error
                            form.add_error(None, 'Currency conversion failed.')
                            return render(request, 'payapp/transfer_money.html', {'form': form})
                    else:
                        converted_amount = amount
                        conversion_rate = 1

                    # Deduct from sender and add to recipient
                    sender_profile.balance -= amount
                    converted_amount = Decimal(converted_amount).quantize(Decimal('0.01'))

                    recipient_profile.balance += converted_amount
                    sender_profile.save()
                    recipient_profile.save()

                    # Record the transaction
                    current_timestamp = get_current_timestamp()  # Get current timestamp from Thrift server
                    Transaction.objects.create(
                        sender=request.user,
                        recipient=recipient,
                        amount=amount,
                        currency=sender_profile.currency,
                        converted_amount=converted_amount,
                        conversion_rate=conversion_rate,
                        converted_currency=recipient_profile.currency,
                        timestamp=current_timestamp  # Save the timestamp
                    )

                    return redirect('transaction_history')
                else:
                    form.add_error(None, 'Insufficient balance.')
        # If the form is not valid or the sender does not have enough balance
        return render(request, 'payapp/transfer_money.html', {'form': form})
    else:
        # GET request case: initialize the form
        form = TransactionForm(user=request.user)
        return render(request, 'payapp/transfer_money.html', {'form': form})


@login_required
def transaction_history(request):
    currency_symbols = {
        'USD': '$',
        'GBP': '£',
        'EUR': '€',
    }
    if request.user.is_superuser:
        sent_transactions = Transaction.objects.order_by('-timestamp')
        received_transactions = Transaction.objects.order_by('-timestamp')
        user_currency_symbol = currency_symbols.get('GBP', '')
    else:
        sent_transactions = Transaction.objects.filter(sender=request.user).order_by('-timestamp')
        received_transactions = Transaction.objects.filter(recipient=request.user).order_by('-timestamp')
        user_currency_symbol = currency_symbols.get(request.user.userprofile.currency, '')

    # Calculate the total balance
    balance_amount = sum([trans.amount for trans in received_transactions], Decimal('0.00'))

    incoming_requests = MoneyRequest.objects.filter(recipient=request.user, status='pending').values('id', 'amount',
                                                                                                     'converted_amount',
                                                                                                     'sender__username',
                                                                                                     'reason')

    context = {
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions,
        'currency_symbol': user_currency_symbol,
        'balance_amount': balance_amount,
        'incoming_requests': incoming_requests,
    }

    return render(request, 'payapp/transaction_history.html', context)


@login_required
def request_money(request):
    if request.method == 'POST':
        form = MoneyRequestForm(request.POST)
        if form.is_valid():
            money_request = form.save(commit=False)
            money_request.sender = request.user  # The one who makes the request
            money_request.recipient = form.cleaned_data['recipient']

            if money_request.sender.userprofile.currency != money_request.recipient.userprofile.currency:
                # Call the conversion service
                conversion_url = f"https://127.0.0.1:8000/conversion/{money_request.sender.userprofile.currency}/{money_request.recipient.userprofile.currency}/{money_request.amount}/"
                response = requests.get(conversion_url, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    money_request.converted_amount = data['converted_amount']
                else:
                    messages.error(request, 'Currency conversion failed.')
                    return redirect('transaction_history')
            else:
                money_request.converted_amount = money_request.amount

            money_request.save()
            messages.success(request, 'Money request made successfully.')
            return redirect('transaction_history')
    else:
        form = MoneyRequestForm()

    return render(request, 'payapp/request_money.html', {'form': form})


@login_required
def accept_request(request, request_id):
    money_request = get_object_or_404(MoneyRequest, pk=request_id, recipient=request.user)
    if request.method == 'POST':
        with db_transaction.atomic():
            sender_profile = money_request.sender.userprofile
            recipient_profile = request.user.userprofile

            if sender_profile.currency != recipient_profile.currency:
                conversion_url = f"https://127.0.0.1:8000/conversion/{sender_profile.currency}/{recipient_profile.currency}/{int(money_request.amount)}/"
                response = requests.get(conversion_url, verify=False)
                if response.status_code == 200:
                    data = response.json()

                    converted_amount = Decimal(data['converted_amount']).quantize(Decimal('0.01'))
                    money_request.converted_amount = converted_amount
                    conversion_rate = Decimal(data['rate']).quantize(Decimal('0.000001'))
                else:
                    messages.error(request, 'Currency conversion failed.')
                    return redirect('transaction_history')
            else:
                converted_amount = money_request.amount
                conversion_rate = Decimal('1')

            if recipient_profile.balance >= converted_amount:

                recipient_profile.balance -= converted_amount
                sender_profile.balance += money_request.amount

                recipient_profile.save()
                sender_profile.save()

                Transaction.objects.create(
                    sender=recipient_profile.user,
                    recipient=sender_profile.user,
                    amount=converted_amount,
                    currency=recipient_profile.currency,
                    converted_amount=money_request.amount,
                    conversion_rate=conversion_rate,
                    converted_currency=sender_profile.currency
                )

                money_request.status = 'accepted'
                money_request.save()

                messages.success(request, 'Request accepted and amount transferred.')
                return redirect('transaction_history')
            else:
                messages.error(request, 'Not enough balance to fulfill the request.')
                return redirect('transaction_history')


@login_required
def decline_request(request, request_id):
    money_request = get_object_or_404(MoneyRequest, pk=request_id, recipient=request.user)
    if request.method == 'POST':
        money_request.status = 'declined'
        money_request.save()
        return redirect('transaction_history')


@login_required()
def create_superadmin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.save()
            messages.success(request, 'Admin user created successfully.')
            return redirect('transaction_history')
    else:
        form = AdminRegistrationForm()
    return render(request, 'payapp/create_admin.html', {'form': form})


@login_required
def admin_dashboard(request):
    users = UserProfile.objects.all()
    print(users)
    return render(request, 'payapp/users.html', {'users': users})


def get_current_timestamp():
    client = make_client(timestamp_thrift.TimestampService, '127.0.0.1', 10000)
    try:
        return client.getCurrentTimestamp()
    finally:
        client.close()
