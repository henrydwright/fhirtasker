from pydantic import BaseSettings

class FHIRSettings(BaseSettings):
    class Config:
        env_prefix = "FHIR_"
    
    base_url: str

_fhir_settings = FHIRSettings()

def get_fhir_settings() -> FHIRSettings:
    return _fhir_settings