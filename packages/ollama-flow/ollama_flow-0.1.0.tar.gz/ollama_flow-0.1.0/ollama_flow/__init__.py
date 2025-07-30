"""
Ollama Flow - A Python library for the Ollama API.

Main features:
- Support for generate, chat, embed endpoints
- Structured output support
- Streaming mode support
"""

from .client import OllamaClient
from .models import GenerateRequest, ChatRequest, EmbedRequest, ChatMessage
from .schemas import StructuredOutput

__version__ = "0.1.0"
__all__ = ["OllamaClient", "GenerateRequest", "ChatRequest", "EmbedRequest", "ChatMessage", "StructuredOutput"] 