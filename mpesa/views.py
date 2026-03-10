import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
import base64
from datetime import datetime
from django.conf import settings

# Safaricom Daraja credentials (replace with sandbox/live credentials)
MPESA_SHORTCODE = '174379'
MPESA_PASSKEY = 'YOUR_PASSKEY'
MPESA_CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
MPESA_CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'
MPESA_CALLBACK_URL = 'https://yourdomain.com/api/mpesa/callback/'  # change if live

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return response.json().get('access_token')

@api_view(['POST'])
def stk_push(request):
    phone_number = request.data.get('phone')
    amount = request.data.get('amount')
    
    if not phone_number or not amount:
        return Response({"error": "Phone number and amount are required"}, status=400)
    
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()
    
    stk_push_request = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": "TestPayment",
        "TransactionDesc": "Payment for testing"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=stk_push_request,
        headers=headers
    )
    
    return Response(response.json())