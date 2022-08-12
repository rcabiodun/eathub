from django.conf import settings
import requests

class PayStack:
    PAYSTACK_SECRET_KEY = "sk_test_7731c88b0b5e13e70f73211704179bd06f354efe"
    base_url='https://api.paystack.co'

    def verify_payment(self, ref, *args, **kwargs):
        path = '/transaction/verify/{0}'.format(ref)

        headers = {
            "Authorization": "Bearer {0}".format(self.PAYSTACK_SECRET_KEY),
            'Content-Type': 'application/json',

        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data['data']
        if response.status_code == 302 :
            response_data = response.json()
            return response_data['status'], response_data['data']
        response_data = response.json()
        return response_data['status'],response_data["message"]
