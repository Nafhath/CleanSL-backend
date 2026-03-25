from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    APP_AUTH_SECRET: str = ""
    ACCESS_TOKEN_EXPIRE_HOURS: int = 12
    APP_NAME: str = "CleanSL Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
