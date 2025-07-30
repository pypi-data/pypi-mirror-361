"""
Data model definitions for Ollama API.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Generate API request model"""
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="Prompt text")
    suffix: Optional[str] = Field(None, description="Text after model response")
    images: Optional[List[str]] = Field(None, description="List of base64-encoded images")
    think: Optional[bool] = Field(False, description="Whether to use thinking mode")
    format: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Response format (json or JSON schema)")
    options: Optional[Dict[str, Any]] = Field(None, description="Model parameters")
    system: Optional[str] = Field(None, description="System message")
    template: Optional[str] = Field(None, description="Prompt template")
    stream: Optional[bool] = Field(True, description="Whether to use streaming mode")
    raw: Optional[bool] = Field(False, description="Whether to use raw mode")
    keep_alive: Optional[str] = Field("5m", description="How long to keep model loaded")
    context: Optional[List[int]] = Field(None, description="Context (deprecated)")


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Role: system, user, assistant, tool")
    content: str = Field(..., description="Message content")
    images: Optional[List[str]] = Field(None, description="List of base64-encoded images")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls")
    tool_name: Optional[str] = Field(None, description="Tool name")


class ChatRequest(BaseModel):
    """Chat API request model"""
    model: str = Field(..., description="Model name")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tool definitions")
    format: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Response format (json or JSON schema)")
    options: Optional[Dict[str, Any]] = Field(None, description="Model parameters")
    stream: Optional[bool] = Field(True, description="Whether to use streaming mode")
    keep_alive: Optional[str] = Field("5m", description="How long to keep model loaded")


class EmbedRequest(BaseModel):
    """Embed API request model"""
    model: str = Field(..., description="Model name")
    input: Union[str, List[str]] = Field(..., description="Input text or list of texts")
    truncate: Optional[bool] = Field(True, description="Whether to truncate text exceeding context length")
    options: Optional[Dict[str, Any]] = Field(None, description="Model parameters")
    keep_alive: Optional[str] = Field("5m", description="How long to keep model loaded")


class GenerateResponse(BaseModel):
    """Generate API response model"""
    model: str
    created_at: str
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    done_reason: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat API response model"""
    model: str
    created_at: str
    message: ChatMessage
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    done_reason: Optional[str] = None


class EmbedResponse(BaseModel):
    """Embed API response model"""
    model: str
    embeddings: List[List[float]]
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None 