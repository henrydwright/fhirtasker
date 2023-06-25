from pydantic import BaseSettings

class APIAuthSettings(BaseSettings):
    class Config:
        env_prefix = "AUTH_"

    base_url: str
    client_id: str
    client_secret: str

_auth_settings = APIAuthSettings()

def get_auth_settings() -> APIAuthSettings:
    return _auth_settings