import base64
import binascii
import json
from typing import Optional, Tuple

from django.conf import settings
from django.http import HttpRequest
from nkunyim_iam.encryption.rsa_encryption import RSAEncryption



class XANAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        self.process_request(request)
        return self.get_response(request)

    def get_app_nat(self, request: HttpRequest) -> Optional[Tuple[str, str, str]]:
        header = request.META.get('HTTP_XAN_AUTHORIZATION')
        if not header:
            return None

        try:
            # Strip prefix/suffix or encoding markers
            cipher_token = header[2:-1]
            cipher_text = base64.b64decode(cipher_token)

            # Decrypt token
            plain_text = RSAEncryption().decrypt(cipher_text)
            xan_data = json.loads(plain_text)

            # Validate expected structure
            if not bool('client_id' in xan_data and 'service_name' in xan_data and 'nation_code' in xan_data):
                return None

            client_id = str(xan_data['client_id'])
            service_name = str(xan_data['service_name']).upper()
            nation_code = str(xan_data['nation_code']).upper()
            if not bool(client_id and service_name and service_name == settings.NKUNYIM_SERVICE):
                return None

            return client_id, service_name, nation_code
        except (ValueError, KeyError, json.JSONDecodeError, binascii.Error):
            return None


    def process_request(self, request: HttpRequest):
        result = self.get_app_nat(request)
        if result:
            client_id, service_name, nation_code = result
            request.client_id = client_id # type: ignore
            request.service_name = service_name # type: ignore
            request.nation_code = nation_code # type: ignore
        else:
            request.client_id = None # type: ignore
            request.service_name = None # type: ignore
            request.nation_code = None # type: ignore
