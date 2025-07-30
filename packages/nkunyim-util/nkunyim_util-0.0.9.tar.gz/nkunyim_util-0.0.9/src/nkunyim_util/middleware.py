import base64
import binascii
import json
from typing import Optional

from django.conf import settings
from django.http import HttpRequest

from nkunyim_util.models.session_model import XanModel
from nkunyim_util.encryption.rsa_encryption import RSAEncryption



class XanAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        self.process_request(request)
        return self.get_response(request)

    def _get_xan(self, request: HttpRequest) -> Optional[XanModel]:
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
            xan_model = XanModel(**xan_data)

            if not bool(xan_model.service_name and xan_model.service_name == settings.NKUNYIM_SERVICE):
                return None

            return xan_model
        except (ValueError, KeyError, json.JSONDecodeError, binascii.Error):
            return None


    def process_request(self, request: HttpRequest):
        xan_model = self._get_xan(request)
        if xan_model:
            xan_model.is_authenticated = True
            request.xan = xan_model # type: ignore
        else:
            request.xan = None # type: ignore



class MultipleProxyMiddleware:
    FORWARDED_FOR_FIELDS = [
        "HTTP_X_FORWARDED_FOR",
        "HTTP_X_FORWARDED_HOST",
        "HTTP_X_FORWARDED_SERVER",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Rewrites the proxy headers so that only the most
        recent proxy is used.
        """
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                if "," in request.META[field]:
                    parts = request.META[field].split(",")
                    request.META[field] = parts[-1].strip()
        return self.get_response(request)
    
    