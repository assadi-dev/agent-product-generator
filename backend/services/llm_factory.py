from langchain_core.language_models import BaseChatModel
from backend.config import settings

# Default models per provider — overridden by LLM_MODEL env var
_DEFAULTS: dict[str, str] = {
    "anthropic":   "claude-sonnet-4-6",
    "openai":      "gpt-4.1",
    "openrouter":  "anthropic/claude-sonnet-4-6",
    "bedrock":     "anthropic.claude-sonnet-4-6-20260101-v1:0",
    "ollama":      "llama3.2",
}


def _model_name(provider: str) -> str:
    """Return the effective model name for a provider (env override or default)."""
    return settings.llm_model or _DEFAULTS[provider]


def get_llm(provider: str | None = None) -> BaseChatModel:
    """Return a configured LLM instance. Defaults to the provider set in config."""
    provider = provider or settings.llm_provider
    model = _model_name(provider)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            api_key=settings.anthropic_api_key,
            temperature=settings.agent_temperature,
            max_tokens=settings.agent_max_tokens,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=settings.openai_api_key,
            temperature=settings.agent_temperature,
            max_tokens=settings.agent_max_tokens,
        )

    if provider == "openrouter":
        # OpenRouter exposes an OpenAI-compatible API — reuse ChatOpenAI with a custom base_url.
        # Pass HTTP headers required by OpenRouter (site URL + app title are optional but recommended).
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=settings.agent_temperature,
            max_tokens=settings.agent_max_tokens,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Product Sheet Generator",
            },
        )

    if provider == "bedrock":
        # Requires langchain-aws: pip install langchain-aws
        # Auth: set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY, or use an IAM role / AWS SSO profile.
        from langchain_aws import ChatBedrock
        import boto3

        session_kwargs: dict = {"region_name": settings.aws_region}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        boto_session = boto3.Session(**session_kwargs)
        bedrock_client = boto_session.client("bedrock-runtime")

        return ChatBedrock(
            model_id=model,
            client=bedrock_client,
            model_kwargs={
                "temperature": settings.agent_temperature,
                "max_tokens": settings.agent_max_tokens,
            },
        )

    if provider == "ollama":
        # Requires langchain-ollama: pip install langchain-ollama
        # Ollama must be running locally (or at OLLAMA_BASE_URL).
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model,
            base_url=settings.ollama_base_url,
            temperature=settings.agent_temperature,
            num_predict=settings.agent_max_tokens,
        )

    raise ValueError(
        f"Unknown LLM provider: {provider!r}. "
        "Choose one of: anthropic | openai | openrouter | bedrock | ollama"
    )


def get_model_name(provider: str | None = None) -> str:
    provider = provider or settings.llm_provider
    return _model_name(provider)
