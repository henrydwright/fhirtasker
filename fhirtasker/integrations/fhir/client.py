from typing import Optional, Union

import requests

from fhir.resources.R4B.operationoutcome import OperationOutcome

from fhirtasker import app
from fhirtasker.integrations.fhir.settings import get_fhir_settings
from fhirtasker.integrations.auth.api.client import APIAuthClient

class FHIRClientOperationError(Exception):
    """
    Error raised when any content-returning operation cannot successfully be completed (e.g. due to server error (500))
    """
    status_code: int
    operation_outcome: Optional[OperationOutcome]

    def __init__(self, 
                 msg: str, 
                 status_code: int, 
                 operation_outcome: Optional[OperationOutcome] = None):
        self.status_code = status_code
        self.operation_outcome = operation_outcome
        super(msg)

class FHIRClient():
    _settings = None
    _auth_client = None

    def __init__(self):
        self._settings = get_fhir_settings()
        self._auth_client = APIAuthClient(self._settings.base_url, self._settings.base_url)
        
    def _handle_standard_response(self,
                                  response: requests.Response,
                                  none_on_404: Optional[bool] = True) -> Optional[str]:
        if response.status_code == 200:
            return response.content
        elif none_on_404 and response.status_code == 404:
            return None
        else:
            try:
                outcome = OperationOutcome.parse_raw(response.content)
                raise FHIRClientOperationError(str(outcome), response.status_code, outcome)
            except (Exception):
                raise FHIRClientOperationError("Error occurred, content was:" + response.content, response.status_code)

    def get_resource(self, relative_path : str) -> requests.Response:
        token = self._auth_client.get_token()
        app.logger.info(f"Fetching resource at path: '{relative_path}'")
        response = requests.get(url=f"{self._settings.base_url}/{relative_path}", 
                            headers={
                                "Authorization": f"Bearer {token}",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                                "Accept": "*/*"
                            })
        return response
    
    def get_resource_content(self, 
                             relative_path : str,
                             none_on_404: bool = True) -> Optional[str]:
        response = self.get_resource(relative_path=relative_path)
        return self._handle_standard_response(response, none_on_404)

    def search(self,
               resource_type: str,
               query_params: dict,
               none_on_404: bool = True):
        search_params = []
        for k, v in query_params.items():
            search_params.append(k + "=" + v)
        search_string = "?" + "&".join(search_params)
        response = self.get_resource(resource_type + search_string)
        return self._handle_standard_response(response, none_on_404)
        
_fhir_client = FHIRClient()

def get_fhir_client():
    return _fhir_client


