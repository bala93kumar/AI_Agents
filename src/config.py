"""Configuration management for the AI Agent"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration"""
    api_key: str
    api_version: str
    azure_endpoint: str
    deployment_name: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000

    @classmethod
    def from_env(cls) -> "AzureOpenAIConfig":
        """Load configuration from environment variables"""
        return cls(
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
            model_name=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
        )


@dataclass
class DatabricksConfig:
    """Databricks configuration using PAT tokens"""
    workspace_url: str
    pat_token: str
    cluster_id: Optional[str] = None

    @classmethod
    def from_env(cls) -> "DatabricksConfig":
        """Load configuration from environment variables"""
        return cls(
            workspace_url=os.getenv("DATABRICKS_WORKSPACE_URL", ""),
            pat_token=os.getenv("DATABRICKS_PAT_TOKEN", ""),
            cluster_id=os.getenv("DATABRICKS_CLUSTER_ID"),
        )


@dataclass
class EmailConfig:
    """Email notification configuration"""
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """Load configuration from environment variables"""
        return cls(
            smtp_server=os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "587")),
            sender_email=os.getenv("EMAIL_SENDER", ""),
            sender_password=os.getenv("EMAIL_PASSWORD", ""),
            enabled=os.getenv("EMAIL_ENABLED", "false").lower() == "true",
        )


@dataclass
class AgentConfig:
    """Main agent configuration"""
    azure_openai: AzureOpenAIConfig
    databricks: DatabricksConfig
    email: EmailConfig
    log_level: str = "INFO"
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load all configuration from environment variables"""
        return cls(
            azure_openai=AzureOpenAIConfig.from_env(),
            databricks=DatabricksConfig.from_env(),
            email=EmailConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
        )
