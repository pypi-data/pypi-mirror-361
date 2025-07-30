"""
Model Validation Feature Demo
"""

from ollama_flow import OllamaClient, ChatMessage


def test_model_validation():
    """Test model validation functionality"""
    print("=== Model Validation Feature Demo ===")
    
    # Create client with model checking enabled
    client = OllamaClient(check_models=True)
    
    # 1. Show available models
    print("\n1. Get Available Model List:")
    try:
        models = client.list_models()
        print(f"Available models: {models}")
    except Exception as e:
        print(f"Failed to get model list: {e}")
        return
    
    # 2. Use existing model
    print("\n2. Use Existing Model:")
    if models:
        valid_model = models[0]
        print(f"Using model: {valid_model}")
        
        try:
            response = client.generate(
                model=valid_model,
                prompt="Hello!",
                stream=False
            )
            print(f"Successfully generated: {response.response[:100]}...")
        except Exception as e:
            print(f"Generation failed: {e}")
    
    # 3. Use non-existent model
    print("\n3. Use Non-existent Model:")
    invalid_model = "nonexistent-model:latest"
    print(f"Trying to use non-existent model: {invalid_model}")
    
    try:
        response = client.generate(
            model=invalid_model,
            prompt="Hello!",
            stream=False
        )
        print("Unexpectedly succeeded!")
    except ValueError as e:
        print(f"Expected model validation error: {e}")
    except Exception as e:
        print(f"Other error: {e}")


def test_model_validation_disabled():
    """Test model validation disabled functionality"""
    print("\n=== Model Validation Disabled Demo ===")
    
    # Create client with model checking disabled
    client = OllamaClient(check_models=False)
    
    invalid_model = "nonexistent-model:latest"
    print(f"Model checking disabled, trying to use non-existent model: {invalid_model}")
    
    try:
        response = client.generate(
            model=invalid_model,
            prompt="Hello!",
            stream=False
        )
        print("Unexpectedly succeeded!")
    except ValueError as e:
        print(f"Model validation error (should not appear): {e}")
    except Exception as e:
        print(f"Expected API error: {e}")


def test_cache_functionality():
    """Test cache functionality"""
    print("\n=== Cache Functionality Demo ===")
    
    client = OllamaClient()
    
    print("First time getting model list (will fetch from server):")
    try:
        models1 = client.list_models()
        print(f"Retrieved {len(models1)} models")
    except Exception as e:
        print(f"Failed to retrieve: {e}")
        return
    
    print("Second time getting model list (using cache):")
    try:
        models2 = client.list_models()
        print(f"Retrieved {len(models2)} models from cache")
    except Exception as e:
        print(f"Failed to retrieve: {e}")
        return
    
    print("Refresh cache:")
    try:
        models3 = client.refresh_models_cache()
        print(f"Retrieved {len(models3)} models after refresh")
    except Exception as e:
        print(f"Failed to refresh: {e}")


def test_all_apis():
    """Test model validation for all APIs"""
    print("\n=== All API Model Validation Demo ===")
    
    client = OllamaClient(check_models=True)
    
    # Get available models
    try:
        models = client.list_models()
        if not models:
            print("No available models")
            return
        
        valid_model = models[0]
        print(f"Using model: {valid_model}")
        
        # Test generate API
        print("\nTesting generate API:")
        try:
            response = client.generate(
                model=valid_model,
                prompt="Say hello",
                stream=False
            )
            print("✓ generate API model validation successful")
        except Exception as e:
            print(f"✗ generate API failed: {e}")
        
        # Test chat API
        print("\nTesting chat API:")
        try:
            messages = [ChatMessage(role="user", content="Hello")]
            response = client.chat(
                model=valid_model,
                messages=messages,
                stream=False
            )
            print("✓ chat API model validation successful")
        except Exception as e:
            print(f"✗ chat API failed: {e}")
        
        # Test embed API
        print("\nTesting embed API:")
        # Find embedding models
        embed_models = [m for m in models if 'embed' in m.lower() or 'minilm' in m.lower() or 'bge' in m.lower()]
        if embed_models:
            embed_model = embed_models[0]
            print(f"Using embedding model: {embed_model}")
            try:
                response = client.embed(
                    model=embed_model,
                    input="Test text"
                )
                print("✓ embed API model validation successful")
            except Exception as e:
                print(f"✗ embed API failed: {e}")
        else:
            print("No embedding models found")
    
    except Exception as e:
        print(f"Failed to get model list: {e}")


if __name__ == "__main__":
    test_model_validation()
    test_model_validation_disabled()
    test_cache_functionality()
    test_all_apis() 