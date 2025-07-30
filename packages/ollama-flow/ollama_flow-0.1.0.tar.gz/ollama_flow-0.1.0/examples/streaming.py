"""
Streaming Mode Examples
"""

from ollama_flow import OllamaClient, ChatMessage
import time


def generate_streaming_example():
    """Generate streaming example"""
    print("=== Generate Streaming Example ===")
    
    client = OllamaClient()
    
    print("Generating response...")
    print("Response content: ", end="", flush=True)
    
    response_stream = client.generate(
        model="llama3.2",
        prompt="Please explain what artificial intelligence is in detail and give examples of its application areas.",
        stream=True
    )
    
    full_response = ""
    for chunk in response_stream:
        if chunk.get("done", False):
            print(f"\n\n=== Statistics ===")
            print(f"Total time: {chunk.get('total_duration', 0) / 1e9:.2f} seconds")
            print(f"Load time: {chunk.get('load_duration', 0) / 1e9:.2f} seconds")
            print(f"Generation time: {chunk.get('eval_duration', 0) / 1e9:.2f} seconds")
            print(f"Generated tokens: {chunk.get('eval_count', 0)}")
            if chunk.get('eval_count', 0) > 0 and chunk.get('eval_duration', 0) > 0:
                tokens_per_sec = chunk.get('eval_count', 0) / (chunk.get('eval_duration', 0) / 1e9)
                print(f"Generation speed: {tokens_per_sec:.2f} tokens/sec")
            break
        else:
            response_text = chunk.get("response", "")
            print(response_text, end="", flush=True)
            full_response += response_text
    
    print(f"\nFull response length: {len(full_response)} characters")


def chat_streaming_example():
    """Chat streaming example"""
    print("\n=== Chat Streaming Example ===")
    
    client = OllamaClient()
    
    messages = [
        ChatMessage(role="system", content="You are a helpful programming assistant."),
        ChatMessage(role="user", content="Please explain what decorators are in Python and provide a practical example.")
    ]
    
    print("Generating response...")
    print("Response content: ", end="", flush=True)
    
    response_stream = client.chat(
        model="llama3.2",
        messages=messages,
        stream=True
    )
    
    full_response = ""
    for chunk in response_stream:
        if chunk.get("done", False):
            print(f"\n\n=== Statistics ===")
            print(f"Total time: {chunk.get('total_duration', 0) / 1e9:.2f} seconds")
            print(f"Load time: {chunk.get('load_duration', 0) / 1e9:.2f} seconds")
            print(f"Generation time: {chunk.get('eval_duration', 0) / 1e9:.2f} seconds")
            print(f"Generated tokens: {chunk.get('eval_count', 0)}")
            break
        else:
            message = chunk.get("message", {})
            response_text = message.get("content", "")
            print(response_text, end="", flush=True)
            full_response += response_text
    
    print(f"\nFull response length: {len(full_response)} characters")


def interactive_chat_example():
    """Interactive chat example"""
    print("\n=== Interactive Chat Example ===")
    print("Type 'quit' or 'exit' to end the conversation")
    
    client = OllamaClient()
    
    # Initialize conversation history
    conversation_history = [
        ChatMessage(role="system", content="You are a friendly chat assistant. Please keep your responses concise.")
    ]
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        # Add user message to conversation history
        conversation_history.append(ChatMessage(role="user", content=user_input))
        
        print("Assistant: ", end="", flush=True)
        
        # Generate response
        response_stream = client.chat(
            model="llama3.2",
            messages=conversation_history,
            stream=True
        )
        
        assistant_response = ""
        for chunk in response_stream:
            if chunk.get("done", False):
                break
            else:
                message = chunk.get("message", {})
                response_text = message.get("content", "")
                print(response_text, end="", flush=True)
                assistant_response += response_text
        
        # Add assistant response to conversation history
        conversation_history.append(ChatMessage(role="assistant", content=assistant_response))
        
        print()  # New line


def streaming_with_progress():
    """Streaming example with progress display"""
    print("\n=== Streaming with Progress Display ===")
    
    client = OllamaClient()
    
    print("Generating response...")
    
    response_stream = client.generate(
        model="llama3.2",
        prompt="Write a short essay about sustainable development, approximately 200 words.",
        stream=True
    )
    
    start_time = time.time()
    char_count = 0
    
    print("Progress: ", end="", flush=True)
    
    for chunk in response_stream:
        if chunk.get("done", False):
            elapsed_time = time.time() - start_time
            print(f"\n\n=== Completed ===")
            print(f"Total characters: {char_count}")
            print(f"Total time: {elapsed_time:.2f} seconds")
            print(f"Average speed: {char_count / elapsed_time:.2f} chars/sec")
            break
        else:
            response_text = chunk.get("response", "")
            char_count += len(response_text)
            
            # Show progress dots
            if char_count % 10 == 0:
                print(".", end="", flush=True)
    
    print("\nGeneration completed!")


if __name__ == "__main__":
    generate_streaming_example()
    chat_streaming_example()
    streaming_with_progress()
    
    # Interactive chat (commented out to avoid waiting for input in automated tests)
    # interactive_chat_example() 