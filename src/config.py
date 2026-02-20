"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Research Analyst FTE configuration."""

    # LLM API Keys
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    tavily_api_key: str = ""

    # Model Routing (LiteLLM format)
    agentic_model: str = "anthropic/claude-sonnet-4-5-20250929"
    fact_check_model: str = "gemini/gemini-2.0-flash"
    simple_model: str = "anthropic/claude-haiku-4-5-20251001"

    # Infrastructure
    redis_host: str = "localhost"
    redis_port: int = 6379
    kafka_broker: str = "localhost:9092"
    dapr_http_port: int = 3500
    dapr_grpc_port: int = 50001

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_name: str = "Research Analyst FTE"
    app_version: str = "1.0.0"

    # Workflow Defaults
    default_budget_limit_usd: float = 1.0
    approval_timeout_hours: int = 24
    max_retry_attempts: int = 3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
