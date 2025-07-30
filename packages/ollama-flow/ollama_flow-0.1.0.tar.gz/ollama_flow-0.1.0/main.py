"""
Ollama Flow Usage Examples
"""

from ollama_flow import OllamaClient, ChatMessage, StructuredOutput
from pydantic import BaseModel, Field
from typing import List


class PersonInfo(BaseModel):
    """Person information model"""
    name: str = Field(..., description="Name")
    age: int = Field(..., description="Age")
    occupation: str = Field(..., description="Occupation")
    skills: List[str] = Field(..., description="List of skills")


def main():
    print("=== Ollama Flow Usage Examples ===")
    
    # Create client
    client = OllamaClient(base_url="http://localhost:11434", timeout=60)
    
    try:
        # Example 1: Basic generation
        print("\n1. Basic Generation Example:")
        response = client.generate(
            model="qwen3:4b-q4_K_M",
            prompt="Explain what machine learning is?",
            stream=False,
            think=False
        )
        print(f"Response: {response.response}")
        
        # Example 2: Chat conversation
        print("\n2. Chat Conversation Example:")
        messages = [
            ChatMessage(role="user", content="Hello! Who are you?")
        ]
        chat_response = client.chat(
            model="qwen3:4b-q4_K_M",
            messages=messages,
            stream=False,
            think=False
        )
        print(f"Response: {chat_response.message.content}")
        
        # Example 3: Structured output
        print("\n3. Structured Output Example:")
        structured_response = client.generate_structured(
            model="qwen3:4b-q4_K_M",
            prompt="Introduce a fictional software engineer character. Please respond in JSON format.",
            schema=PersonInfo,
            stream=False,
            think=False
        )
        print(f"Structured Response: {structured_response.response}")
        
        # Parse structured response
        person_data = client.parse_structured_response(
            structured_response.response,
            PersonInfo
        )
        print(f"Parsed Data: {person_data}")
        
        # Example 4: JSON mode
        print("\n4. JSON Mode Example:")
        json_response = client.generate_json(
            model="qwen3:4b-q4_K_M",
            prompt="List three programming languages and their features. Please respond in JSON format.",
            stream=False,
            think=False
        )
        print(f"JSON Response: {json_response.response}")
        
        # Example 5: Generate embeddings
        print("\n5. Generate Embeddings Example:")
        embed_response = client.embed(
            model="bge-m3:latest",
            input="This is a test text"
        )
        print(f"Embedding Dimension: {len(embed_response.embeddings[0])}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure Ollama service is running and required models are installed.")


if __name__ == "__main__":
    main()
