from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    api_key: str = "dev-key-change-in-production"
    openai_api_key: str | None = None  # Set in .env for AI teacher responses


settings = Settings()
