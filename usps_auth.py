from urllib import response
import requests
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
import certifi


# USPS OAuth credentials
CLIENT_ID = "ADaDvRQn2IRbv8QE3mNHtAzBZfskgg5nVxCMCtahAGSZoLAZ"
CLIENT_SECRET = "pnKhLAW8toSGCMCU9f2HFGHGwqftu8vkw2a1GlziF9j18mwlQHVkdBzxZJJ8574j"

# USPS token endpoint
TOKEN_URL = "https://api.usps.com/oauth2/v3/token"


# TLSAdapter definition
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

# Create global session with TLSAdapter mounted
session = requests.Session()
session.mount("https://", TLSAdapter())


# Global token cache
_access_token = None
_token_expiration = 0  # Unix timestamp when token expires

def get_usps_token():
    global _access_token, _token_expiration

    # Refresh token if expired or not yet retrieved
    if not _access_token or time.time() > _token_expiration:

        # Encode client_id:client_secret in Base64
        # credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        # encoded_credentials = base64.b64encode(credentials.encode()).decode()

        print(certifi.where())

        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "User-Agent": "PostmanRuntime/7.32.3"
        }

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "addresses"
        }

        response = session.post(TOKEN_URL, headers=headers, json=data, verify=certifi.where())
        #response = requests.post(
        #    TOKEN_URL,
        #    headers=headers,
        #     json=data
        #)

        print(response.request.headers)
        print(response.request.body)

        if response.status_code == 200:
            token_data = response.json()
            _access_token = token_data["access_token"]
            expires_in = token_data["expires_in"]
            _token_expiration = time.time() + expires_in - 60  # refresh 1 min before expiry
            print("✅ USPS token refreshed")
        else:
            print("🔴 Failed to obtain USPS token")
            print(response.status_code, response.text)
            _access_token = None

    return _access_token
