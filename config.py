from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    api_key: str = "dev-key-change-in-production"


settings = Settings()
