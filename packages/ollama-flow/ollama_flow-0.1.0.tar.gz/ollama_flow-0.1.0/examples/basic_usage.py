"""
Basic Usage Examples
"""

from ollama_flow import OllamaClient, ChatMessage


def basic_generate_example():
    """Basic generation example"""
    print("=== Basic Generation Example ===")
    
    client = OllamaClient()
    
    response = client.generate(
        model="qwen3:4b-q4_K_M",
        prompt="What is Python? Please give a brief answer.",
        stream=False
    )
    
    print(f"Model: {response.model}")
    print(f"Response: {response.response}")
    print(f"Generation Time: {response.eval_duration / 1e9:.2f} seconds")


def basic_chat_example():
    """Basic chat example"""
    print("\n=== Basic Chat Example ===")
    
    client = OllamaClient()
    
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Please introduce yourself.")
    ]
    
    response = client.chat(
        model="qwen3:4b-q4_K_M",
        messages=messages,
        stream=False
    )
    
    print(f"Model: {response.model}")
    print(f"Response: {response.message.content}")


def basic_embed_example():
    """Basic embedding example"""
    print("\n=== Basic Embedding Example ===")
    
    client = OllamaClient()
    
    response = client.embed(
        model="bge-m3:latest",
        input="This is a test text for generating embedding vectors."
    )
    
    print(f"Model: {response.model}")
    print(f"Embedding Dimension: {len(response.embeddings[0])}")
    print(f"First 5 values: {response.embeddings[0][:5]}")


if __name__ == "__main__":
    basic_generate_example()
    basic_chat_example()
    basic_embed_example() 