from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CareerAI API"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str = ""

    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    openai_api_key: str = ""
    ai_mock_mode: bool = True

    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()