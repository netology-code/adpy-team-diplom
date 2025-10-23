from pydantic.v1 import BaseSettings


class ConfigBase(BaseSettings):
    class Config:
        env_file = '.env'

class SettingsToken(ConfigBase):
    ID_CLIENT: str
    REDIR_URL: str

class SettingsAPI(ConfigBase):
    KEY: str

class SettingSSL(ConfigBase):
    SSL_KEYFILE: str
    SSL_CERTFILE: str


settings_token = SettingsToken()
settings_api = SettingsAPI()
settings_ssl = SettingSSL()
