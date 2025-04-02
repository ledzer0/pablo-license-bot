import requests
import os

TOYYIBPAY_SECRET_KEY = os.getenv("TOYYIBPAY_SECRET_KEY")
TOYYIBPAY_CATEGORY_CODE = os.getenv("TOYYIBPAY_CATEGORY_CODE")
TOYYIBPAY_BASE_URL = "https://toyyibpay.com"

def create_payment_link(bill_name, bill_description, amount, return_url, callback_url, user_email, user_phone):
    """
    Create a payment link using ToyyibPay API.

    :param bill_name: Name of the bill (max 30 characters)
    :param bill_description: Description of the bill (max 100 characters)
    :param amount: Amount in cents (e.g., 100 for RM1.00)
    :param return_url: URL to redirect after payment
    :param callback_url: URL for payment status callback
    :param user_email: Payer's email address
    :param user_phone: Payer's phone number
    :return: Payment URL or None if failed
    """
    data = {
        "userSecretKey": TOYYIBPAY_SECRET_KEY,
        "categoryCode": TOYYIBPAY_CATEGORY_CODE,
        "billName": bill_name[:30],
        "billDescription": bill_description[:100],
        "billPriceSetting": 1,
        "billPayorInfo": 1,
        "billAmount
