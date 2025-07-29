"""Configuration settings for the MCP Cordra server."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CordraConfig(BaseSettings):
    """Configuration for connecting to a Cordra repository."""

    model_config = SettingsConfigDict(
        env_prefix="CORDRA_",
        case_sensitive=False,
    )

    base_url: str = Field(
        default="https://localhost:8443",
        description="Base URL of the Cordra repository",
    )
    username: str | None = Field(
        default=None, description="Username for Cordra authentication"
    )
    password: str | None = Field(
        default=None, description="Password for Cordra authentication"
    )
    verify_ssl: bool = Field(
        default=True, description="Whether to verify SSL certificates"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
