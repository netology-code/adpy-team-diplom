from pydantic.v1 import BaseSettings


class Base(BaseSettings):
    class Config:
        env_file = '.env'


class AuthSettings(Base):
    AUTH_URL: str
    AUTH_TOKEN: str


class BotSettings(Base):
    BOT_TOKEN: str


bot_settings = BotSettings()
auth_settings = AuthSettings()