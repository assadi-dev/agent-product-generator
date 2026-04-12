from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # ignore unknown env vars (ex: STREAMLIT_SERVER_PORT)
    )

    # LLM — provider selection
    llm_provider: Literal["anthropic", "openai", "openrouter", "bedrock", "ollama"] = Field(
        default="anthropic", alias="LLM_PROVIDER"
    )
    # Optional model override (each provider has a sensible default if left empty)
    llm_model: str = Field(default="", alias="LLM_MODEL")

    # Anthropic
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    # OpenRouter (OpenAI-compatible, just a different base_url + key)
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")

    # Amazon Bedrock
    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_secret_key: str = Field(default="dev-secret", alias="API_SECRET_KEY")
    cors_origins: list[str] = Field(default=["http://localhost:8501"], alias="CORS_ORIGINS")

    # Streamlit
    streamlit_backend_url: str = Field(default="http://localhost:8000", alias="STREAMLIT_BACKEND_URL")

    # Agent
    agent_max_iterations: int = Field(default=5, alias="AGENT_MAX_ITERATIONS")
    agent_temperature: float = Field(default=0.7, alias="AGENT_TEMPERATURE")
    agent_max_tokens: int = Field(default=4096, alias="AGENT_MAX_TOKENS")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")


settings = Settings()
