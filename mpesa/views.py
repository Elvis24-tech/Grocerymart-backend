from django.http import JsonResponse
from rest_framework.decorators import api_view
import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64
import os

# Load M-Pesa credentials from .env
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL')

# Sandbox URLs
MPESA_OAUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
MPESA_STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"


def get_access_token():
    """Get OAuth access token from Safaricom"""
    response = requests.get(MPESA_OAUTH_URL, auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    response.raise_for_status()
    return response.json()['access_token']


def generate_password(timestamp):
    """Generate password for STK Push"""
    data_to_encode = MPESA_SHORTCODE + MPESA_PASSKEY + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode())
    return encoded_string.decode('utf-8')


@api_view(['POST'])
def stk_push(request):
    """
    Trigger M-Pesa STK Push
    POST JSON body: {"phone": "2547XXXXXXXX", "amount": 100}
    """
    data = request.data
    phone = data.get('phone')
    amount = data.get('amount')

    if not phone or not amount:
        return JsonResponse({"error": "Phone and amount are required"}, status=400)

    # Timestamp in format YYYYMMDDHHMMSS
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = generate_password(timestamp)
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": "DjangoAppPayment",
        "TransactionDesc": "Payment from Django app"
    }

    try:
        response = requests.post(MPESA_STK_PUSH_URL, json=payload, headers=headers)
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def stk_callback(request):
    """
    Handle M-Pesa callback
    """
    print("Callback received:", request.data)
    return JsonResponse({"status": "success"})