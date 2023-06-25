from datetime import datetime
from typing import Optional

import requests

from fhirtasker import app
from fhirtasker.integrations.auth.api.settings import APIAuthSettings, get_auth_settings

class APIAuthClient():
    _settings : APIAuthSettings
    _cache_token : Optional[str]
    _cache_expiry : Optional[datetime]
    _resource: str
    _audience: str

    def __init__(self, resource: str, audience: str):
        self._settings = get_auth_settings()
        self._cache_token = None
        self._cache_expiry = None
        self._resource = resource
        self._audience = audience

    def _fetch_new_token(self) -> None:
        app.logger.info("Fetching new OAuth Token")
        oauth_token_request = requests.post(url = f"{self._settings.base_url}/oauth2/token", 
                                    data = {
                                        "grant_type": "client_credentials",
                                        "resource": self._resource,
                                        "audience": self._audience,
                                        "client_id": self._settings.client_id,
                                        "client_secret": self._settings.client_secret
                                    },
                                    headers={
                                        "content-type": "application/x-www-form-urlencoded"
                                    })
        if oauth_token_request.status_code == 200:
            oauth_response = oauth_token_request.json()
            self._cache_token = oauth_response['access_token']
            self._cache_expiry = datetime.utcfromtimestamp(int(oauth_response['expires_on']))
            app.logger.info(f"New API token expires at {self._cache_expiry.isoformat()}Z")
        else:
            app.logger.error(f"API authentication failed with status code {oauth_token_request.status_code}")

    def get_token(self) -> Optional[str]:
        if self._cache_token and datetime.utcnow() < self._cache_expiry:
            app.logger.info(f"Old API token valid until {self._cache_expiry.isoformat()}Z")
            return self._cache_token
        else:
            self._fetch_new_token()
            return self._cache_token
