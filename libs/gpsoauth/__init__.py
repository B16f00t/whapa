"""A python client library for Google Play Services OAuth."""
from __future__ import annotations

from collections.abc import MutableMapping
from importlib.metadata import version
import ssl
from typing import Any, Iterable

import requests
from urllib3.poolmanager import PoolManager  # type: ignore
from urllib3.util import ssl_

from . import google

__version__ = version(__package__)

# The key is distirbuted with Google Play Services.
# This one is from version 7.3.29.
B64_KEY_7_3_29 = (
    b"AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3"
    b"iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pK"
    b"RI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/"
    b"6rmf5AAAAAwEAAQ=="
)

ANDROID_KEY_7_3_29 = google.key_from_b64(B64_KEY_7_3_29)

AUTH_URL = "https://android.clients.google.com/auth"
USER_AGENT = "GoogleAuth/1.4"

# Google is very picky about list of used ciphers. Changing this list most likely
# will cause BadAuthentication error.
CIPHERS = [
    "ECDHE+AESGCM",
    "ECDHE+CHACHA20",
    "DHE+AESGCM",
    "DHE+CHACHA20",
    "ECDH+AES",
    "DH+AES",
    "RSA+AESGCM",
    "RSA+AES",
    "!aNULL",
    "!eNULL",
    "!MD5",
    "!DSS",
]


class SSLContext(ssl.SSLContext):
    """SSLContext wrapper."""

    def set_alpn_protocols(self, alpn_protocols: Iterable[str]) -> None:
        """
        ALPN headers cause Google to return 403 Bad Authentication.
        """


class AuthHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        """
        Secure settings from ssl.create_default_context(), but without
        ssl.OP_NO_TICKET which causes Google to return 403 Bad
        Authentication.
        """
        context = SSLContext()
        context.set_ciphers(ssl_.DEFAULT_CIPHERS)
        context.verify_mode = ssl.CERT_REQUIRED
        context.options &= ~ssl_.OP_NO_TICKET
        self.poolmanager = PoolManager(*args, ssl_context=context, **kwargs)


def _perform_auth_request(
    data: dict[str, int | str | bytes], proxies: MutableMapping[str, str] | None = None
) -> dict[str, str]:
    session = requests.session()
    session.mount(AUTH_URL, AuthHTTPAdapter())
    if proxies:
        session.proxies = proxies
    session.headers={"User-Agent": USER_AGENT, 'Content-type': 'application/x-www-form-urlencoded'}

    res = session.post(AUTH_URL, data=data, verify=True)

    return google.parse_auth_response(res.text)


def perform_master_login(
    email: str,
    password: str,
    android_id: str,
    service: str = "ac2dm",
    device_country: str = "us",
    operator_country: str = "us",
    lang: str = "en",
    sdk_version: int = 17,
    proxy: MutableMapping[str, str] | None = None,
    client_sig: str = "38918a453d07199354f8b19af05ec6562ced5788",
) -> dict[str, str]:
    """
    Perform a master login, which is what Android does when you first add
    a Google account.
    Return a dict, eg::
        {
            'Auth': '...',
            'Email': 'email@gmail.com',
            'GooglePlusUpgrade': '1',
            'LSID': '...',
            'PicasaUser': 'My Name',
            'RopRevision': '1',
            'RopText': ' ',
            'SID': '...',
            'Token': 'oauth2rt_1/...',
            'firstName': 'My',
            'lastName': 'Name',
            'services': 'hist,mail,googleme,...'
        }
    """

    data: dict[str, int | str | bytes] = {
        "accountType": "HOSTED_OR_GOOGLE",
        "Email": email,
        "has_permission": 1,
        "add_account": 1,
        "EncryptedPasswd": google.construct_signature(
            email, password, ANDROID_KEY_7_3_29
        ),
        "service": service,
        "source": "android",
        "androidId": android_id,
        "device_country": device_country,
        "operatorCountry": operator_country,
        "lang": lang,
        "sdk_version": sdk_version,
        "client_sig": client_sig,
        "callerSig": client_sig,
        "droidguard_results": "dummy123"
    }

    return _perform_auth_request(data, proxy)


def perform_master_login_oauth(
    email: str,
    oauth_token: str,
    android_id: str,
    service: str = "ac2dm",
    device_country: str = "us",
    operator_country: str = "us",
    lang: str = "en",
    sdk_version: int = 28,
    proxy: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """
    Perform a master login, which is what Android does when you first add
    a Google account.

    Return a dict, eg::

        {
            'Auth': '...',
            'Email': 'email@gmail.com',
            'GooglePlusUpgrade': '1',
            'LSID': '...',
            'PicasaUser': 'My Name',
            'RopRevision': '1',
            'RopText': ' ',
            'SID': '...',
            'Token': 'oauth2rt_1/...',
            'firstName': 'My',
            'lastName': 'Name',
            'services': 'hist,mail,googleme,...'
        }
    """

    data: dict[str, int | str | bytes] = {
        "lang": lang,
        "google_play_services_version": 19629032,
        "sdk_version": sdk_version,
        "device_country": device_country,
        "Email": email,
        "service": service,
        "get_accountid": 1,
        "ACCESS_TOKEN": 1,
        "callerPkg": "com.google.android.gms",
        "add_account": 1,
        "Token": oauth_token,
        "callerSig": "38918a453d07199354f8b19af05ec6562ced5788",
    }

    return _perform_auth_request(data, proxy)


def perform_oauth(
    email: str,
    master_token: str,
    android_id: str,
    service: str,
    app: str,
    client_sig: str,
    device_country: str = "us",
    operator_country: str = "us",
    lang: str = "en",
    sdk_version: int = 17,
    proxy: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """
    Use a master token from master_login to perform OAuth to a specific Google service.

    Return a dict, eg::

        {
            'Auth': '...',
            'LSID': '...',
            'SID': '..',
            'issueAdvice': 'auto',
            'services': 'hist,mail,googleme,...'
        }

    To authenticate requests to this service, include a header
    ``Authorization: GoogleLogin auth=res['Auth']``.
    """

    data: dict[str, int | str | bytes] = {
        "accountType": "HOSTED_OR_GOOGLE",
        "Email": email,
        "has_permission": 1,
        "EncryptedPasswd": master_token,
        "service": service,
        "source": "android",
        "androidId": android_id,
        "app": app,
        "client_sig": client_sig,
        "device_country": device_country,
        "operatorCountry": operator_country,
        "lang": lang,
        "sdk_version": sdk_version,
    }

    return _perform_auth_request(data, proxy)
