from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    openai_org: str = SettingsConfigDict()
    openai_project: str = SettingsConfigDict()
    openai_key: str = SettingsConfigDict()
    openai_assistant: str = SettingsConfigDict()
