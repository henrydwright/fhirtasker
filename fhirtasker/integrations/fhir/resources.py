from typing import Optional

from fhir.resources.R4B.patient import Patient

from fhirtasker.integrations.fhir.client import get_fhir_client, FHIRClient

class ActiveBase():
    """
    Base class with functionality to save to, or download from server versions
    """
    _sync_id: Optional[str] = None
    _resource_type: Optional[str] = None 
    _fhir_client: Optional[FHIRClient] = None

    _resource_string: Optional[str]

    def __init__(self, id: str, resource_type: str):
        self._sync_id = id
        self._fhir_client = get_fhir_client()
        self._resource_type = resource_type

    def _sync_resource_string(self):
        self._resource_string = self._fhir_client.get_resource_content(f"{self._resource_type}/{self._sync_id}", none_on_404=False)


class ActivePatient(ActiveBase):
    """
    Patient with added ability to save or refresh from server version
    """

    patient : Optional[Patient]

    def __init__(self, id: str):
        super().__init__(id, "Patient")

    def refresh(self):
        """Replaces local copy of resource with one from server"""
        self._sync_resource_string()
        self.patient = Patient.parse_raw(self._resource_string)





