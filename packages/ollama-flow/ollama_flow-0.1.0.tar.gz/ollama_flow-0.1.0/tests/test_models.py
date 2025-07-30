"""
數據模型單元測試
"""

import pytest
from typing import List, Optional, Union
from pydantic import ValidationError

from ollama_flow.models import (
    ChatMessage, 
    GenerateRequest, 
    GenerateResponse,
    ChatRequest,
    ChatResponse,
    EmbedRequest,
    EmbedResponse
)


class TestChatMessage:
    """ChatMessage 模型測試"""
    
    def test_valid_user_message(self):
        """測試有效的用戶訊息"""
        message = ChatMessage(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"
        
    def test_valid_assistant_message(self):
        """測試有效的助手訊息"""
        message = ChatMessage(role="assistant", content="How can I help you?")
        assert message.role == "assistant"
        assert message.content == "How can I help you?"
        
    def test_valid_system_message(self):
        """測試有效的系統訊息"""
        message = ChatMessage(role="system", content="You are a helpful assistant.")
        assert message.role == "system"
        assert message.content == "You are a helpful assistant."
        
    def test_invalid_role(self):
        """測試角色字段接受任何字符串"""
        # ChatMessage 接受任何字符串作為角色，包括自定義角色
        message = ChatMessage(role="custom_role", content="Test")
        assert message.role == "custom_role"
        assert message.content == "Test"
        
    def test_empty_content(self):
        """測試空內容"""
        message = ChatMessage(role="user", content="")
        assert message.content == ""
        
    def test_missing_role(self):
        """測試缺少角色"""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(content="Hello")
        
        assert "Field required" in str(exc_info.value)
        
    def test_missing_content(self):
        """測試缺少內容"""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(role="user")
        
        assert "Field required" in str(exc_info.value)
        
    def test_to_dict(self):
        """測試轉換為字典"""
        message = ChatMessage(role="user", content="Hello")
        message_dict = message.model_dump()
        
        # 檢查必要的字段
        assert message_dict["role"] == "user"
        assert message_dict["content"] == "Hello"
        # 可能包含其他可選字段，但設為 None
        
    def test_from_dict(self):
        """測試從字典創建"""
        message_dict = {"role": "assistant", "content": "Hi there!"}
        message = ChatMessage(**message_dict)
        
        assert message.role == "assistant"
        assert message.content == "Hi there!"


class TestGenerateRequest:
    """GenerateRequest 模型測試"""
    
    def test_minimal_request(self):
        """測試最小請求"""
        request = GenerateRequest(model="llama3.2", prompt="Hello")
        assert request.model == "llama3.2"
        assert request.prompt == "Hello"
        assert request.stream is True  # 默認值為 True
        
    def test_full_request(self):
        """測試完整請求"""
        request = GenerateRequest(
            model="llama3.2",
            prompt="Hello world",
            stream=True,
            format="json",
            options={"temperature": 0.7, "top_p": 0.9},
            system="You are helpful",
            template="Custom template",
            context=[1, 2, 3],
            raw=True
        )
        
        assert request.model == "llama3.2"
        assert request.prompt == "Hello world"
        assert request.stream is True
        assert request.format == "json"
        assert request.options == {"temperature": 0.7, "top_p": 0.9}
        assert request.system == "You are helpful"
        assert request.template == "Custom template"
        assert request.context == [1, 2, 3]
        assert request.raw is True
        
    def test_missing_model(self):
        """測試缺少模型"""
        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(prompt="Hello")
        
        assert "Field required" in str(exc_info.value)
        
    def test_missing_prompt(self):
        """測試缺少提示"""
        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(model="llama3.2")
        
        assert "Field required" in str(exc_info.value)
        
    def test_invalid_options_type(self):
        """測試無效的選項類型"""
        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(model="llama3.2", prompt="Hello", options="invalid")
        
        assert "Input should be a valid dictionary" in str(exc_info.value)
        
    def test_to_dict(self):
        """測試轉換為字典"""
        request = GenerateRequest(
            model="llama3.2",
            prompt="Hello",
            stream=True,
            options={"temperature": 0.8}
        )
        
        request_dict = request.model_dump(exclude_none=True)
        
        assert request_dict["model"] == "llama3.2"
        assert request_dict["prompt"] == "Hello"
        assert request_dict["stream"] is True
        assert request_dict["options"] == {"temperature": 0.8}
        # 確認 None 值被排除
        assert "system" not in request_dict


class TestGenerateResponse:
    """GenerateResponse 模型測試"""
    
    def test_minimal_response(self):
        """測試最小回應"""
        response = GenerateResponse(
            model="llama3.2",
            created_at="2024-01-01T00:00:00Z",
            response="Hello world!",
            done=True
        )
        
        assert response.model == "llama3.2"
        assert response.response == "Hello world!"
        assert response.done is True
        
    def test_full_response(self):
        """測試完整回應"""
        response = GenerateResponse(
            model="llama3.2",
            created_at="2024-01-01T00:00:00Z",
            response="Hello world!",
            done=True,
            context=[1, 2, 3],
            total_duration=1000000000,
            load_duration=500000000,
            prompt_eval_count=10,
            prompt_eval_duration=200000000,
            eval_count=20,
            eval_duration=800000000
        )
        
        assert response.model == "llama3.2"
        assert response.response == "Hello world!"
        assert response.done is True
        assert response.context == [1, 2, 3]
        assert response.total_duration == 1000000000
        assert response.load_duration == 500000000
        assert response.prompt_eval_count == 10
        assert response.prompt_eval_duration == 200000000
        assert response.eval_count == 20
        assert response.eval_duration == 800000000
        
    def test_streaming_response(self):
        """測試串流回應"""
        response = GenerateResponse(
            model="llama3.2",
            created_at="2024-01-01T00:00:00Z",
            response="Hello",
            done=False
        )
        
        assert response.model == "llama3.2"
        assert response.response == "Hello"
        assert response.done is False
        
    def test_missing_required_fields(self):
        """測試缺少必要欄位"""
        with pytest.raises(ValidationError) as exc_info:
            GenerateResponse(response="Hello", done=True)
        
        assert "Field required" in str(exc_info.value)


class TestChatRequest:
    """ChatRequest 模型測試"""
    
    def test_minimal_request(self):
        """測試最小請求"""
        messages = [ChatMessage(role="user", content="Hello")]
        request = ChatRequest(model="llama3.2", messages=messages)
        
        assert request.model == "llama3.2"
        assert len(request.messages) == 1
        assert request.messages[0].role == "user"
        assert request.messages[0].content == "Hello"
        assert request.stream is True  # 默認值為 True
        
    def test_multiple_messages(self):
        """測試多個訊息"""
        messages = [
            ChatMessage(role="system", content="You are helpful"),
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there!"),
            ChatMessage(role="user", content="How are you?")
        ]
        request = ChatRequest(model="llama3.2", messages=messages)
        
        assert len(request.messages) == 4
        assert request.messages[0].role == "system"
        assert request.messages[1].role == "user"
        assert request.messages[2].role == "assistant"
        assert request.messages[3].role == "user"
        
    def test_with_options(self):
        """測試帶選項的請求"""
        messages = [ChatMessage(role="user", content="Hello")]
        request = ChatRequest(
            model="llama3.2",
            messages=messages,
            stream=True,
            options={"temperature": 0.7}
        )
        
        assert request.stream is True
        assert request.options == {"temperature": 0.7}
        
    def test_empty_messages(self):
        """測試空訊息列表"""
        request = ChatRequest(model="llama3.2", messages=[])
        assert len(request.messages) == 0
        
    def test_missing_model(self):
        """測試缺少模型"""
        messages = [ChatMessage(role="user", content="Hello")]
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(messages=messages)
        
        assert "Field required" in str(exc_info.value)
        
    def test_missing_messages(self):
        """測試缺少訊息"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(model="llama3.2")
        
        assert "Field required" in str(exc_info.value)
        
    def test_invalid_message_type(self):
        """測試無效的訊息類型"""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(model="llama3.2", messages=["invalid"])
        
        assert "Input should be a valid dictionary" in str(exc_info.value)


class TestChatResponse:
    """ChatResponse 模型測試"""
    
    def test_minimal_response(self):
        """測試最小回應"""
        message = ChatMessage(role="assistant", content="Hello!")
        response = ChatResponse(
            model="llama3.2",
            created_at="2024-01-01T00:00:00Z",
            message=message,
            done=True
        )
        
        assert response.model == "llama3.2"
        assert response.message.role == "assistant"
        assert response.message.content == "Hello!"
        assert response.done is True
        
    def test_full_response(self):
        """測試完整回應"""
        message = ChatMessage(role="assistant", content="Hello!")
        response = ChatResponse(
            model="llama3.2",
            created_at="2024-01-01T00:00:00Z",
            message=message,
            done=True,
            total_duration=1000000000,
            load_duration=500000000,
            prompt_eval_count=10,
            prompt_eval_duration=200000000,
            eval_count=20,
            eval_duration=800000000
        )
        
        assert response.model == "llama3.2"
        assert response.message.role == "assistant"
        assert response.message.content == "Hello!"
        assert response.done is True
        assert response.total_duration == 1000000000
        assert response.eval_count == 20
        
    def test_streaming_response(self):
        """測試串流回應"""
        message = ChatMessage(role="assistant", content="Hello")
        response = ChatResponse(
            model="llama3.2",
            created_at="2024-01-01T00:00:00Z",
            message=message,
            done=False
        )
        
        assert response.done is False
        
    def test_missing_required_fields(self):
        """測試缺少必要欄位"""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(message=ChatMessage(role="assistant", content="Hello"), done=True)
        
        assert "Field required" in str(exc_info.value)


class TestEmbedRequest:
    """EmbedRequest 模型測試"""
    
    def test_single_input(self):
        """測試單一輸入"""
        request = EmbedRequest(model="all-minilm", input="Hello world")
        
        assert request.model == "all-minilm"
        assert request.input == "Hello world"
        
    def test_multiple_inputs(self):
        """測試多個輸入"""
        inputs = ["Hello world", "How are you?", "Goodbye"]
        request = EmbedRequest(model="all-minilm", input=inputs)
        
        assert request.model == "all-minilm"
        assert request.input == inputs
        assert len(request.input) == 3
        
    def test_with_options(self):
        """測試帶選項的請求"""
        request = EmbedRequest(
            model="all-minilm",
            input="Hello world",
            options={"truncate": True}
        )
        
        assert request.options == {"truncate": True}
        
    def test_missing_model(self):
        """測試缺少模型"""
        with pytest.raises(ValidationError) as exc_info:
            EmbedRequest(input="Hello world")
        
        assert "Field required" in str(exc_info.value)
        
    def test_missing_input(self):
        """測試缺少輸入"""
        with pytest.raises(ValidationError) as exc_info:
            EmbedRequest(model="all-minilm")
        
        assert "Field required" in str(exc_info.value)
        
    def test_empty_input(self):
        """測試空輸入"""
        request = EmbedRequest(model="all-minilm", input="")
        assert request.input == ""
        
    def test_empty_list_input(self):
        """測試空列表輸入"""
        request = EmbedRequest(model="all-minilm", input=[])
        assert request.input == []


class TestEmbedResponse:
    """EmbedResponse 模型測試"""
    
    def test_single_embedding(self):
        """測試單一嵌入"""
        embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        response = EmbedResponse(model="all-minilm", embeddings=embeddings)
        
        assert len(response.embeddings) == 1
        assert len(response.embeddings[0]) == 5
        assert response.embeddings[0][0] == 0.1
        assert response.embeddings[0][4] == 0.5
        
    def test_multiple_embeddings(self):
        """測試多個嵌入"""
        embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ]
        response = EmbedResponse(model="all-minilm", embeddings=embeddings)
        
        assert len(response.embeddings) == 3
        assert response.embeddings[0] == [0.1, 0.2, 0.3]
        assert response.embeddings[1] == [0.4, 0.5, 0.6]
        assert response.embeddings[2] == [0.7, 0.8, 0.9]
        
    def test_empty_embeddings(self):
        """測試空嵌入列表"""
        response = EmbedResponse(model="all-minilm", embeddings=[])
        assert len(response.embeddings) == 0
        
    def test_missing_embeddings(self):
        """測試缺少嵌入"""
        with pytest.raises(ValidationError) as exc_info:
            EmbedResponse()
        
        assert "Field required" in str(exc_info.value)
        
    def test_invalid_embedding_type(self):
        """測試無效的嵌入類型"""
        with pytest.raises(ValidationError) as exc_info:
            EmbedResponse(embeddings=["invalid"])
        
        assert "Input should be a valid list" in str(exc_info.value)
        
    def test_mixed_dimension_embeddings(self):
        """測試不同維度的嵌入"""
        embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5]  # 不同維度
        ]
        response = EmbedResponse(model="all-minilm", embeddings=embeddings)
        
        # 模型應該接受不同維度的嵌入
        assert len(response.embeddings[0]) == 3
        assert len(response.embeddings[1]) == 2


class TestModelSerialization:
    """測試模型序列化"""
    
    def test_chat_message_json(self):
        """測試 ChatMessage JSON 序列化"""
        message = ChatMessage(role="user", content="Hello")
        json_str = message.model_dump_json()
        
        assert '"role":"user"' in json_str
        assert '"content":"Hello"' in json_str
        
    def test_generate_request_json(self):
        """測試 GenerateRequest JSON 序列化"""
        request = GenerateRequest(
            model="llama3.2",
            prompt="Hello",
            stream=True,
            options={"temperature": 0.7}
        )
        
        json_str = request.model_dump_json(exclude_none=True)
        
        assert '"model":"llama3.2"' in json_str
        assert '"prompt":"Hello"' in json_str
        assert '"stream":true' in json_str
        assert '"temperature":0.7' in json_str
        
    def test_model_from_json(self):
        """測試從 JSON 創建模型"""
        json_data = '{"role": "assistant", "content": "Hello!"}'
        message = ChatMessage.model_validate_json(json_data)
        
        assert message.role == "assistant"
        assert message.content == "Hello!" 