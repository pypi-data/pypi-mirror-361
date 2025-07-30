"""
Structured Output Examples
"""

from ollama_flow import OllamaClient, ChatMessage, StructuredOutput
from pydantic import BaseModel, Field
from typing import List, Optional
import json


class Product(BaseModel):
    """Product information model"""
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Price")
    category: str = Field(..., description="Category")
    description: str = Field(..., description="Description")
    features: List[str] = Field(..., description="Feature list")
    in_stock: bool = Field(..., description="Whether in stock")


class BookSummary(BaseModel):
    """Book summary model"""
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author")
    genre: str = Field(..., description="Genre")
    main_themes: List[str] = Field(..., description="Main themes")
    rating: int = Field(..., description="Rating (1-10)")
    summary: str = Field(..., description="Summary")


class WeatherInfo(BaseModel):
    """Weather information model"""
    location: str = Field(..., description="Location")
    temperature: float = Field(..., description="Temperature")
    humidity: int = Field(..., description="Humidity percentage")
    condition: str = Field(..., description="Weather condition")
    wind_speed: Optional[float] = Field(None, description="Wind speed")


def pydantic_schema_example():
    """Structured output example using Pydantic model"""
    print("=== Pydantic Model Structured Output Example ===")
    
    client = OllamaClient()
    
    # Generate product information
    response = client.generate_structured(
        model="llama3.2",
        prompt="Create product information for a smartphone. Please respond in JSON format.",
        schema=Product,
        stream=False
    )
    
    print(f"Raw response: {response.response}")
    
    # Parse structured response
    try:
        product = client.parse_structured_response(response.response, Product)
        print(f"\nParsed product information:")
        print(f"Name: {product.name}")
        print(f"Price: ${product.price}")
        print(f"Category: {product.category}")
        print(f"Description: {product.description}")
        print(f"Features: {', '.join(product.features)}")
        print(f"In Stock: {'Yes' if product.in_stock else 'No'}")
    except Exception as e:
        print(f"Parsing error: {e}")


def json_schema_example():
    """Structured output example using JSON Schema dictionary"""
    print("\n=== JSON Schema Structured Output Example ===")
    
    client = OllamaClient()
    
    # Custom JSON Schema
    person_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "occupation": {"type": "string"},
            "hobbies": {"type": "array", "items": {"type": "string"}},
            "married": {"type": "boolean"}
        },
        "required": ["name", "age", "occupation"]
    }
    
    response = client.generate_structured(
        model="llama3.2",
        prompt="Create personal information for a fictional character. Please respond in JSON format.",
        schema=person_schema,
        stream=False
    )
    
    print(f"Raw response: {response.response}")
    
    # Parse response
    try:
        person_data = json.loads(response.response)
        print(f"\nParsed character information:")
        print(f"Name: {person_data.get('name', 'N/A')}")
        print(f"Age: {person_data.get('age', 'N/A')}")
        print(f"Occupation: {person_data.get('occupation', 'N/A')}")
        print(f"Hobbies: {', '.join(person_data.get('hobbies', []))}")
        print(f"Married: {'Yes' if person_data.get('married', False) else 'No'}")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")


def chat_structured_example():
    """Structured output example in chat mode"""
    print("\n=== Chat Mode Structured Output Example ===")
    
    client = OllamaClient()
    
    messages = [
        ChatMessage(role="system", content="You are a book recommendation assistant."),
        ChatMessage(role="user", content="Recommend a science fiction novel and provide detailed information. Please respond in JSON format.")
    ]
    
    response = client.chat_structured(
        model="llama3.2",
        messages=messages,
        schema=BookSummary,
        stream=False
    )
    
    print(f"Raw response: {response.message.content}")
    
    # Parse structured response
    try:
        book = client.parse_structured_response(response.message.content, BookSummary)
        print(f"\nRecommended book:")
        print(f"Title: {book.title}")
        print(f"Author: {book.author}")
        print(f"Genre: {book.genre}")
        print(f"Main themes: {', '.join(book.main_themes)}")
        print(f"Rating: {book.rating}/10")
        print(f"Summary: {book.summary}")
    except Exception as e:
        print(f"Parsing error: {e}")


def json_mode_example():
    """JSON mode example"""
    print("\n=== JSON Mode Example ===")
    
    client = OllamaClient()
    
    response = client.generate_json(
        model="llama3.2",
        prompt="List three programming languages and their main features. Please respond in JSON format.",
        stream=False
    )
    
    print(f"Raw response: {response.response}")
    
    # Parse JSON response
    try:
        data = json.loads(response.response)
        print(f"\nParsed data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")


if __name__ == "__main__":
    pydantic_schema_example()
    json_schema_example()
    chat_structured_example()
    json_mode_example() 