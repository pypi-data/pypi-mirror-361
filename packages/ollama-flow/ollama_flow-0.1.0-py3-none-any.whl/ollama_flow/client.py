"""
Ollama API client implementation.
"""

import json
import requests
from typing import Union, Dict, Any, Iterator, Optional, Type, List
from urllib.parse import urljoin

from .models import (
    GenerateRequest, GenerateResponse,
    ChatRequest, ChatResponse, ChatMessage,
    EmbedRequest, EmbedResponse
)
from .schemas import StructuredOutput
from pydantic import BaseModel


class OllamaClient:
    """
    Ollama API client class.
    
    Supported features:
    - Generate API (text completion)
    - Chat API (chat completion)
    - Embed API (generate embeddings)
    - Structured output
    - Streaming mode
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30, check_models: bool = True):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL of the Ollama server
            timeout: Request timeout in seconds
            check_models: Whether to check if model exists before calling
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.check_models = check_models
        self.session = requests.Session()
        self._models_cache = None  # Model list cache
        
        # Set request headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None, stream: bool = False, method: str = "POST") -> requests.Response:
        """
        Send HTTP request.
        
        Args:
            endpoint: API endpoint
            data: Request data (optional)
            stream: Whether to use streaming mode
            method: HTTP method (GET or POST)
            
        Returns:
            HTTP response object
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    stream=stream
                )
            else:
                response = self.session.post(
                    url,
                    json=data,
                    timeout=self.timeout,
                    stream=stream
                )
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def _stream_response(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """
        Handle streaming response.
        
        Args:
            response: HTTP response object
            
        Yields:
            Each JSON response object
        """
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    
    def list_models(self, refresh_cache: bool = False) -> List[str]:
        """
        Get list of available models.
        
        Args:
            refresh_cache: Whether to refresh cache
            
        Returns:
            List of model names
        """
        if self._models_cache is None or refresh_cache:
            try:
                response = self._make_request("/api/tags", method="GET")
                data = response.json()
                
                models = []
                for model_info in data.get("models", []):
                    models.append(model_info.get("name", ""))
                
                self._models_cache = models
                return models
            except Exception as e:
                raise Exception(f"Failed to get model list: {e}")
        
        return self._models_cache or []
    
    def _check_model_exists(self, model: str) -> None:
        """
        Check if model exists.
        
        Args:
            model: Model name
            
        Raises:
            ValueError: If model does not exist
        """
        if not self.check_models:
            return
        
        available_models = self.list_models()
        if model not in available_models:
            raise ValueError(
                f"Model '{model}' does not exist. Available models: {', '.join(available_models)}"
            )
    
    def refresh_models_cache(self) -> List[str]:
        """
        Refresh model cache and return latest model list.
        
        Returns:
            Latest list of model names
        """
        return self.list_models(refresh_cache=True)
    
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        suffix: Optional[str] = None,
        images: Optional[List[str]] = None,
        think: bool = False,
        format: Optional[Union[str, Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
        system: Optional[str] = None,
        template: Optional[str] = None,
        stream: bool = False,
        raw: bool = False,
        keep_alive: str = "5m",
        context: Optional[List[int]] = None
    ) -> Union[GenerateResponse, Iterator[Dict[str, Any]]]:
        """
        Generate completion (Generate API).
        
        Args:
            model: Model name
            prompt: Prompt text
            suffix: Text after model response
            images: List of base64-encoded images
            think: Whether to use thinking mode
            format: Response format (json or JSON schema)
            options: Model parameters
            system: System message
            template: Prompt template
            stream: Whether to use streaming mode
            raw: Whether to use raw mode
            keep_alive: How long to keep model loaded
            context: Context (deprecated)
            
        Returns:
            GenerateResponse or streaming response iterator
        """
        # Check if model exists
        self._check_model_exists(model)
        
        request = GenerateRequest(
            model=model,
            prompt=prompt,
            suffix=suffix,
            images=images,
            think=think,
            format=format,
            options=options,
            system=system,
            template=template,
            stream=stream,
            raw=raw,
            keep_alive=keep_alive,
            context=context
        )
        
        response = self._make_request("/api/generate", request.model_dump(exclude_none=True), stream=stream)
        
        if stream:
            return self._stream_response(response)
        else:
            data = response.json()
            return GenerateResponse.model_validate(data)
    
    def chat(
        self,
        model: str,
        messages: List[Union[ChatMessage, Dict[str, Any]]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        format: Optional[Union[str, Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        keep_alive: str = "5m"
    ) -> Union[ChatResponse, Iterator[Dict[str, Any]]]:
        """
        Chat completion (Chat API).
        
        Args:
            model: Model name
            messages: List of chat messages
            tools: Tool definitions
            format: Response format (json or JSON schema)
            options: Model parameters
            stream: Whether to use streaming mode
            keep_alive: How long to keep model loaded
            
        Returns:
            ChatResponse or streaming response iterator
        """
        # Check if model exists
        self._check_model_exists(model)
        
        # Convert message format
        chat_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                chat_messages.append(ChatMessage.model_validate(msg))
            else:
                chat_messages.append(msg)
        
        request = ChatRequest(
            model=model,
            messages=chat_messages,
            tools=tools,
            format=format,
            options=options,
            stream=stream,
            keep_alive=keep_alive
        )
        
        response = self._make_request("/api/chat", request.model_dump(exclude_none=True), stream=stream)
        
        if stream:
            return self._stream_response(response)
        else:
            data = response.json()
            return ChatResponse.model_validate(data)
    
    def embed(
        self,
        model: str,
        input: Union[str, List[str]],
        *,
        truncate: bool = True,
        options: Optional[Dict[str, Any]] = None,
        keep_alive: str = "5m"
    ) -> EmbedResponse:
        """
        Generate embeddings (Embed API).
        
        Args:
            model: Model name
            input: Input text or list of texts
            truncate: Whether to truncate text exceeding context length
            options: Model parameters
            keep_alive: How long to keep model loaded
            
        Returns:
            EmbedResponse
        """
        # Check if model exists
        self._check_model_exists(model)
        
        request = EmbedRequest(
            model=model,
            input=input,
            truncate=truncate,
            options=options,
            keep_alive=keep_alive
        )
        
        response = self._make_request("/api/embed", request.model_dump(exclude_none=True))
        data = response.json()
        return EmbedResponse.model_validate(data)
    
    # Convenience methods
    def generate_json(
        self,
        model: str,
        prompt: str,
        **kwargs
    ) -> Union[GenerateResponse, Iterator[Dict[str, Any]]]:
        """
        Generate JSON format response.
        
        Args:
            model: Model name
            prompt: Prompt text
            **kwargs: Other parameters
            
        Returns:
            GenerateResponse or streaming response iterator
        """
        return self.generate(model, prompt, format="json", **kwargs)
    
    def generate_structured(
        self,
        model: str,
        prompt: str,
        schema: Union[Type[BaseModel], Dict[str, Any]],
        **kwargs
    ) -> Union[GenerateResponse, Iterator[Dict[str, Any]]]:
        """
        Generate structured response.
        
        Args:
            model: Model name
            prompt: Prompt text
            schema: Pydantic model class or JSON schema dictionary
            **kwargs: Other parameters
            
        Returns:
            GenerateResponse or streaming response iterator
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            format_schema = StructuredOutput.from_pydantic(schema)
        else:
            format_schema = schema
            
        return self.generate(model, prompt, format=format_schema, **kwargs)
    
    def chat_json(
        self,
        model: str,
        messages: List[Union[ChatMessage, Dict[str, Any]]],
        **kwargs
    ) -> Union[ChatResponse, Iterator[Dict[str, Any]]]:
        """
        Chat generate JSON format response.
        
        Args:
            model: Model name
            messages: List of chat messages
            **kwargs: Other parameters
            
        Returns:
            ChatResponse or streaming response iterator
        """
        return self.chat(model, messages, format="json", **kwargs)
    
    def chat_structured(
        self,
        model: str,
        messages: List[Union[ChatMessage, Dict[str, Any]]],
        schema: Union[Type[BaseModel], Dict[str, Any]],
        **kwargs
    ) -> Union[ChatResponse, Iterator[Dict[str, Any]]]:
        """
        Chat generate structured response.
        
        Args:
            model: Model name
            messages: List of chat messages
            schema: Pydantic model class or JSON schema dictionary
            **kwargs: Other parameters
            
        Returns:
            ChatResponse or streaming response iterator
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            format_schema = StructuredOutput.from_pydantic(schema)
        else:
            format_schema = schema
            
        return self.chat(model, messages, format=format_schema, **kwargs)
    
    def parse_structured_response(
        self,
        response: str,
        model_class: Optional[Type[BaseModel]] = None
    ) -> Any:
        """
        Parse structured response.
        
        Args:
            response: Response string
            model_class: Optional Pydantic model class
            
        Returns:
            Parsed object
        """
        return StructuredOutput.parse_response(response, model_class)
    
    def __enter__(self):
        """Context manager enter"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.session.close() 