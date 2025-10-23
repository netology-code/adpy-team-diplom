from pydantic.v1 import BaseSettings


class Base(BaseSettings):
    class Config:
        env_file = '.env'


class AuthSettings(Base):
    AUTH_URL: str
    AUTH_TOKEN: str

auth_settings = AuthSettings()