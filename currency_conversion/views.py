from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.http import require_http_methods

CONVERSION_RATES = {
    ('USD', 'EUR'): 0.85,
    ('EUR', 'USD'): 1.17,
    ('GBP', 'USD'): 1.30,
    ('USD', 'GBP'): 0.77,
    ('GBP', 'EUR'): 1.15,
    ('EUR', 'GBP'): 0.87,

}


@require_http_methods(["GET"])
def conversion(request, currency1, currency2, amount_of_currency1):
    try:
        # Convert amount to float
        amount = float(amount_of_currency1)
        if amount < 0:
            raise ValueError("Amount must be a positive number.")

        # Convert currency codes to uppercase to match the keys in CONVERSION_RATES
        currency1 = currency1.upper()
        currency2 = currency2.upper()

        key = (currency1, currency2)
        if key in CONVERSION_RATES:
            rate = CONVERSION_RATES[key]
            converted_amount = amount * rate
            return JsonResponse({
                'converted_amount': round(converted_amount, 2),
                'currency': currency2,
                'rate': rate
            })
        else:

            return HttpResponseNotFound('Conversion rate not found for the specified currencies.')

    except (ValueError, TypeError):

        return HttpResponseBadRequest('Invalid amount provided.')
