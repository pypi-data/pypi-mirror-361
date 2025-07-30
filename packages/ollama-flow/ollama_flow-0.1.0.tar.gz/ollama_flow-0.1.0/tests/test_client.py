"""
OllamaClient 單元測試
"""

import pytest
import json
import requests
from unittest.mock import patch, Mock, MagicMock
from typing import Dict, Any, List

from ollama_flow import OllamaClient, ChatMessage
from ollama_flow.models import GenerateResponse, ChatResponse, EmbedResponse
from pydantic import BaseModel, Field


class PersonInfoModel(BaseModel):
    """測試用的人員資訊模型"""
    name: str = Field(..., description="姓名")
    age: int = Field(..., description="年齡")
    skills: List[str] = Field(..., description="技能列表")


class TestOllamaClient:
    """OllamaClient 測試類別"""
    
    def setup_method(self):
        """在每個測試方法之前執行"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    def test_init_with_default_url(self):
        """測試使用預設 URL 初始化"""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.timeout == 30
        assert client.check_models is True
        
    def test_init_with_custom_params(self):
        """測試使用自定義參數初始化"""
        client = OllamaClient(
            base_url="http://custom:8080",
            timeout=60,
            check_models=False
        )
        assert client.base_url == "http://custom:8080"
        assert client.timeout == 60
        assert client.check_models is False
        
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """測試成功的 HTTP 請求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        result = self.client._make_request("/api/generate", {"prompt": "test"})
        
        assert result.json() == {"test": "data"}
        assert result.status_code == 200
        mock_request.assert_called_once()
        
    @patch('requests.Session.request')
    def test_make_request_http_error(self, mock_request):
        """測試 HTTP 錯誤處理"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_request.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            self.client._make_request("/api/generate", {"prompt": "test"})
        
        assert "Request failed" in str(exc_info.value)
            
    @patch('requests.Session.request')
    def test_make_request_connection_error(self, mock_request):
        """測試連接錯誤處理"""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            self.client._make_request("/api/generate", {"prompt": "test"})
        
        assert "Request failed" in str(exc_info.value)
            
    @patch('requests.Session.request')
    def test_list_models_success(self, mock_request):
        """測試成功獲取模型列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2", "size": 1000000},
                {"name": "qwen3:4b", "size": 2000000}
            ]
        }
        mock_request.return_value = mock_response
        
        models = self.client.list_models()
        
        assert len(models) == 2
        assert "llama3.2" in models
        assert "qwen3:4b" in models
        
    @patch('requests.Session.request')
    def test_list_models_caching(self, mock_request):
        """測試模型列表快取功能"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3.2", "size": 1000000}]
        }
        mock_request.return_value = mock_response
        
        # 第一次調用
        models1 = self.client.list_models()
        # 第二次調用，應該使用快取
        models2 = self.client.list_models()
        
        assert models1 == models2
        # 確認只調用了一次 API
        mock_request.assert_called_once()
        
    @patch('requests.Session.request')
    def test_check_model_exists_valid(self, mock_request):
        """測試檢查有效的模型"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3.2", "size": 1000000}]
        }
        mock_request.return_value = mock_response
        
        # 不應該拋出異常
        self.client._check_model_exists("llama3.2")
        
    @patch('requests.Session.request')
    def test_check_model_exists_invalid(self, mock_request):
        """測試檢查無效的模型"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3.2", "size": 1000000}]
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            self.client._check_model_exists("invalid_model")
        
        assert "Model 'invalid_model' does not exist" in str(exc_info.value)
        assert "llama3.2" in str(exc_info.value)
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_generate_success(self, mock_request, mock_check_model):
        """測試成功生成回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama3.2",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "This is a test response",
            "done": True,
            "total_duration": 1000000000,
            "load_duration": 500000000,
            "eval_count": 20
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate(
            model="llama3.2",
            prompt="Test prompt",
            stream=False
        )
        
        assert isinstance(result, GenerateResponse)
        assert result.response == "This is a test response"
        assert result.done is True
        mock_check_model.assert_called_once_with("llama3.2")
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_generate_with_options(self, mock_request, mock_check_model):
        """測試帶選項的生成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama3.2",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "Response with options",
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate(
            model="llama3.2",
            prompt="Test prompt",
            stream=False,
            options={"temperature": 0.7, "top_p": 0.9}
        )
        
        assert result.response == "Response with options"
        
        # 檢查請求參數
        call_args = mock_request.call_args
        request_data = call_args[1]['json']
        assert request_data['options']['temperature'] == 0.7
        assert request_data['options']['top_p'] == 0.9
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_chat_success(self, mock_request, mock_check_model):
        """測試成功的聊天回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama3.2",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you?"
            },
            "done": True,
            "total_duration": 1000000000
        }
        mock_request.return_value = mock_response
        
        messages = [ChatMessage(role="user", content="Hello")]
        result = self.client.chat(
            model="llama3.2",
            messages=messages,
            stream=False
        )
        
        assert isinstance(result, ChatResponse)
        assert result.message.role == "assistant"
        assert result.message.content == "Hello! How can I help you?"
        mock_check_model.assert_called_once_with("llama3.2")
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_chat_with_system_message(self, mock_request, mock_check_model):
        """測試包含系統訊息的聊天"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama3.2",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "I'm a helpful assistant."
            },
            "done": True
        }
        mock_request.return_value = mock_response
        
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Who are you?")
        ]
        
        result = self.client.chat(
            model="llama3.2",
            messages=messages,
            stream=False
        )
        
        assert result.message.content == "I'm a helpful assistant."
        
        # 檢查請求參數
        call_args = mock_request.call_args
        request_data = call_args[1]['json']
        assert len(request_data['messages']) == 2
        assert request_data['messages'][0]['role'] == "system"
        assert request_data['messages'][1]['role'] == "user"
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_embed_success(self, mock_request, mock_check_model):
        """測試成功的嵌入生成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "all-minilm",
            "embeddings": [[0.1, 0.2, 0.3, 0.4, 0.5]]
        }
        mock_request.return_value = mock_response
        
        result = self.client.embed(
            model="all-minilm",
            input="Test text"
        )
        
        assert isinstance(result, EmbedResponse)
        assert len(result.embeddings) == 1
        assert len(result.embeddings[0]) == 5
        assert result.embeddings[0][0] == 0.1
        mock_check_model.assert_called_once_with("all-minilm")
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_embed_multiple_inputs(self, mock_request, mock_check_model):
        """測試多個輸入的嵌入生成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "all-minilm",
            "embeddings": [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6]
            ]
        }
        mock_request.return_value = mock_response
        
        result = self.client.embed(
            model="all-minilm",
            input=["Text 1", "Text 2"]
        )
        
        assert len(result.embeddings) == 2
        assert result.embeddings[0] == [0.1, 0.2, 0.3]
        assert result.embeddings[1] == [0.4, 0.5, 0.6]
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_generate_structured_success(self, mock_request, mock_check_model):
        """測試成功的結構化生成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama3.2",
            "created_at": "2024-01-01T00:00:00Z",
            "response": '{"name": "John", "age": 30, "skills": ["Python", "JavaScript"]}',
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate_structured(
            model="llama3.2",
            prompt="Generate a person",
            schema=PersonInfoModel,
            stream=False
        )
        
        assert isinstance(result, GenerateResponse)
        assert '"name": "John"' in result.response
        mock_check_model.assert_called_once_with("llama3.2")
        
    def test_parse_structured_response_success(self):
        """測試成功解析結構化回應"""
        json_response = '{"name": "Alice", "age": 25, "skills": ["Python", "Data Science"]}'
        
        result = self.client.parse_structured_response(json_response, PersonInfoModel)
        
        assert isinstance(result, PersonInfoModel)
        assert result.name == "Alice"
        assert result.age == 25
        assert result.skills == ["Python", "Data Science"]
        
    def test_parse_structured_response_invalid_json(self):
        """測試解析無效 JSON 的結構化回應"""
        invalid_json = '{"name": "Alice", "age": 25, "skills": ["Python"]'  # 缺少結束括號
        
        with pytest.raises(ValueError) as exc_info:
            self.client.parse_structured_response(invalid_json, PersonInfoModel)
        
        assert "Unable to parse JSON response" in str(exc_info.value)
        
    def test_parse_structured_response_validation_error(self):
        """測試結構化回應驗證錯誤"""
        json_response = '{"name": "Alice", "age": "not_a_number", "skills": ["Python"]}'
        
        with pytest.raises(ValueError) as exc_info:
            self.client.parse_structured_response(json_response, PersonInfoModel)
        
        assert "Unable to validate response data" in str(exc_info.value)
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_generate_json_success(self, mock_request, mock_check_model):
        """測試成功的 JSON 生成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama3.2",
            "created_at": "2024-01-01T00:00:00Z",
            "response": '{"languages": ["Python", "JavaScript", "Go"]}',
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate_json(
            model="llama3.2",
            prompt="List programming languages",
            stream=False
        )
        
        assert isinstance(result, GenerateResponse)
        assert '"languages"' in result.response
        
        # 檢查請求參數中是否包含 JSON 格式
        call_args = mock_request.call_args
        request_data = call_args[1]['json']
        assert request_data['format'] == 'json'
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_streaming_generate(self, mock_request, mock_check_model):
        """測試串流生成"""
        # 模擬串流回應
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"model": "llama3.2", "created_at": "2024-01-01T00:00:00Z", "response": "Hello", "done": false}',
            b'{"model": "llama3.2", "created_at": "2024-01-01T00:00:00Z", "response": " world", "done": false}',
            b'{"model": "llama3.2", "created_at": "2024-01-01T00:00:00Z", "response": "!", "done": true, "total_duration": 1000000000}'
        ]
        mock_request.return_value = mock_response
        
        result = self.client.generate(
            model="llama3.2",
            prompt="Say hello",
            stream=True
        )
        
        responses = list(result)
        assert len(responses) == 3
        assert responses[0]["response"] == "Hello"
        assert responses[1]["response"] == " world"
        assert responses[2]["response"] == "!"
        assert responses[2]["done"] is True
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_streaming_chat(self, mock_request, mock_check_model):
        """測試串流聊天"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"model": "llama3.2", "created_at": "2024-01-01T00:00:00Z", "message": {"role": "assistant", "content": "Hi"}, "done": false}',
            b'{"model": "llama3.2", "created_at": "2024-01-01T00:00:00Z", "message": {"role": "assistant", "content": " there"}, "done": false}',
            b'{"model": "llama3.2", "created_at": "2024-01-01T00:00:00Z", "message": {"role": "assistant", "content": "!"}, "done": true}'
        ]
        mock_request.return_value = mock_response
        
        messages = [ChatMessage(role="user", content="Hello")]
        result = self.client.chat(
            model="llama3.2",
            messages=messages,
            stream=True
        )
        
        responses = list(result)
        assert len(responses) == 3
        assert responses[0]["message"]["content"] == "Hi"
        assert responses[1]["message"]["content"] == " there"
        assert responses[2]["message"]["content"] == "!"
        assert responses[2]["done"] is True
        
    def test_context_manager(self):
        """測試上下文管理器"""
        with OllamaClient() as client:
            assert client is not None
            assert hasattr(client, 'session')
            
    def test_model_checking_disabled(self):
        """測試停用模型檢查"""
        client = OllamaClient(check_models=False)
        
        # 這應該不會進行實際的模型檢查，即使使用無效模型也能成功
        with patch('requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "llama3.2",
                "created_at": "2024-01-01T00:00:00Z",
                "response": "test",
                "done": True
            }
            mock_request.return_value = mock_response
            
            # 使用不存在的模型名，如果模型檢查被禁用，這應該成功
            result = client.generate(model="non_existent_model", prompt="test", stream=False)
            
            # 確認請求成功
            assert result.response == "test"
                
    def test_refresh_models_cache(self):
        """測試刷新模型快取"""
        with patch('requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [{"name": "test_model", "size": 1000}]
            }
            mock_request.return_value = mock_response
            
            # 第一次獲取
            self.client.list_models()
            
            # 刷新快取
            self.client.refresh_models_cache()
            
            # 再次獲取，應該重新調用 API
            self.client.list_models()
            
            # 應該調用了兩次 API（一次初始，一次刷新後）
            assert mock_request.call_count == 2 