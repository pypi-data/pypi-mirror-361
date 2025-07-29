from typing import Any, ClassVar

from pydantic import Field, field_validator, model_validator

from memos.configs.base import BaseConfig


class BaseEmbedderConfig(BaseConfig):
    """Base configuration class for embedding models."""

    model_name_or_path: str = Field(..., description="Model name or path")
    embedding_dims: int | None = Field(
        default=None, description="Number of dimensions for the embedding"
    )


class OllamaEmbedderConfig(BaseEmbedderConfig):
    api_base: str = Field(default="http://localhost:11434", description="Base URL for Ollama API")


class SenTranEmbedderConfig(BaseEmbedderConfig):
    """Configuration class for Sentence Transformer embeddings."""

    trust_remote_code: bool = Field(
        default=True,
        description="Whether to trust remote code when loading the model",
    )


class EmbedderConfigFactory(BaseConfig):
    """Factory class for creating embedder configurations."""

    backend: str = Field(..., description="Backend for embedding model")
    config: dict[str, Any] = Field(..., description="Configuration for the embedding model backend")

    backend_to_class: ClassVar[dict[str, Any]] = {
        "ollama": OllamaEmbedderConfig,
        "sentence_transformer": SenTranEmbedderConfig,
    }

    @field_validator("backend")
    @classmethod
    def validate_backend(cls, backend: str) -> str:
        """Validate the backend field."""
        if backend not in cls.backend_to_class:
            raise ValueError(f"Invalid backend: {backend}")
        return backend

    @model_validator(mode="after")
    def create_config(self) -> "EmbedderConfigFactory":
        config_class = self.backend_to_class[self.backend]
        self.config = config_class(**self.config)
        return self
