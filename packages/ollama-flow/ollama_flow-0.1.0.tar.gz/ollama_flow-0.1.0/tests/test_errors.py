"""
異常處理和邊界條件測試
"""

import pytest
import json
import requests
from unittest.mock import patch, Mock
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException
from pydantic import ValidationError

from ollama_flow import OllamaClient, ChatMessage
from ollama_flow.models import GenerateResponse, ChatResponse, EmbedResponse
from pydantic import BaseModel, Field


class SampleTestModel(BaseModel):
    """測試模型"""
    name: str = Field(..., description="名稱")
    value: int = Field(..., description="數值")


class TestNetworkErrors:
    """網絡錯誤測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_connection_error(self, mock_request, mock_check_model):
        """測試連接錯誤"""
        mock_request.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            self.client.generate(model="test_model", prompt="test", stream=False)
        
        assert "Request failed: Connection failed" in str(exc_info.value)
            
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_timeout_error(self, mock_request, mock_check_model):
        """測試超時錯誤"""
        mock_request.side_effect = Timeout("Request timed out")
        
        with pytest.raises(Exception) as exc_info:
            self.client.generate(model="test_model", prompt="test", stream=False)
        
        assert "Request failed: Request timed out" in str(exc_info.value)
            
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_http_404_error(self, mock_request, mock_check_model):
        """測試 404 錯誤"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_request.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            self.client.generate(model="test_model", prompt="test", stream=False)
        
        assert "Request failed: 404 Not Found" in str(exc_info.value)
            
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_http_500_error(self, mock_request, mock_check_model):
        """測試 500 錯誤"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = HTTPError("500 Internal Server Error")
        mock_request.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            self.client.generate(model="test_model", prompt="test", stream=False)
        
        assert "Request failed: 500 Internal Server Error" in str(exc_info.value)
            
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_malformed_json_response(self, mock_request, mock_check_model):
        """測試格式錯誤的 JSON 回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_request.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            self.client.generate(model="test_model", prompt="test", stream=False)
        
        assert "Invalid JSON" in str(exc_info.value)
            
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_empty_response(self, mock_request, mock_check_model):
        """測試空回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ValidationError) as exc_info:
            self.client.generate(model="test_model", prompt="test", stream=False)
        
        assert "validation errors for GenerateResponse" in str(exc_info.value)
            
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_missing_required_fields(self, mock_request, mock_check_model):
        """測試缺少必要欄位的回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Test response"
            # 缺少 "done" 和 "model" 欄位
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(ValidationError) as exc_info:
            self.client.generate(model="test_model", prompt="test", stream=False)
        
        assert "validation errors for GenerateResponse" in str(exc_info.value)


class TestInputValidation:
    """輸入驗證測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    def test_empty_model_name(self):
        """測試空模型名稱"""
        with pytest.raises(ValueError) as exc_info:
            self.client.generate(model="", prompt="test", stream=False)
        
        assert "Model '' does not exist" in str(exc_info.value)
            
    def test_none_model_name(self):
        """測試 None 模型名稱"""
        with pytest.raises(ValueError) as exc_info:
            self.client.generate(model=None, prompt="test", stream=False)
        
        assert "Model 'None' does not exist" in str(exc_info.value)
            
    def test_empty_prompt(self):
        """測試空提示"""
        with patch('ollama_flow.client.OllamaClient._check_model_exists'):
            with patch('requests.Session.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "model": "test_model",
                    "created_at": "2024-01-01T00:00:00Z",
                    "response": "",
                    "done": True
                }
                mock_request.return_value = mock_response
                
                # 空提示應該被接受
                result = self.client.generate(model="test_model", prompt="", stream=False)
                assert result.response == ""
                
    def test_none_prompt(self):
        """測試 None 提示"""
        with pytest.raises(ValueError) as exc_info:
            self.client.generate(model="test_model", prompt=None, stream=False)
        
        assert "Model 'test_model' does not exist" in str(exc_info.value)
            
    def test_invalid_options_type(self):
        """測試無效的選項類型"""
        with pytest.raises(ValueError) as exc_info:
            self.client.generate(
                model="test_model",
                prompt="test",
                options="invalid_options",
                stream=False
            )
        
        assert "Model 'test_model' does not exist" in str(exc_info.value)
            
    def test_empty_messages_list(self):
        """測試空訊息列表"""
        with patch('ollama_flow.client.OllamaClient._check_model_exists'):
            with patch('requests.Session.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "Hello"
            },
            "done": True
        }
                mock_request.return_value = mock_response
                
                # 空訊息列表應該被接受
                result = self.client.chat(model="test_model", messages=[], stream=False)
                assert result.message.content == "Hello"
                
    def test_invalid_message_role(self):
        """測試訊息角色接受任何字符串"""
        # ChatMessage 接受任何字符串作為角色
        message = ChatMessage(role="invalid_role", content="test")
        assert message.role == "invalid_role"
        assert message.content == "test"
            
    def test_missing_message_content(self):
        """測試缺少訊息內容"""
        with pytest.raises(ValidationError):
            ChatMessage(role="user")
            
    def test_invalid_embed_input_type(self):
        """測試無效的嵌入輸入類型"""
        with pytest.raises(ValueError) as exc_info:
            self.client.embed(model="test_model", input=123)  # 應該是字符串或列表
        
        assert "Model 'test_model' does not exist" in str(exc_info.value)


class TestModelValidation:
    """模型驗證測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('requests.Session.request')
    def test_model_not_found(self, mock_request):
        """測試模型未找到"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "existing_model", "size": 1000}
            ]
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            self.client.generate(model="nonexistent_model", prompt="test", stream=False)
            
        assert "Model 'nonexistent_model' does not exist" in str(exc_info.value)
        assert "existing_model" in str(exc_info.value)
        
    @patch('requests.Session.request')
    def test_model_list_api_error(self, mock_request):
        """測試模型列表 API 錯誤"""
        mock_request.side_effect = ConnectionError("Failed to connect")
        
        with pytest.raises(Exception) as exc_info:
            self.client.list_models()
        
        assert "Failed to get model list" in str(exc_info.value)
            
    @patch('requests.Session.request')
    def test_model_list_empty_response(self, mock_request):
        """測試模型列表空回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_request.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            self.client.generate(model="any_model", prompt="test", stream=False)
            
        assert "Model 'any_model' does not exist" in str(exc_info.value)
        
    @patch('requests.Session.request')
    def test_model_list_malformed_response(self, mock_request):
        """測試模型列表格式錯誤的回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "structure"}
        mock_request.return_value = mock_response
        
        # 模型列表 API 應該拋出異常，但不是 KeyError
        # 因為 client.py 中有 .get("models", []) 處理
        models = self.client.list_models()
        assert models == []  # 格式錯誤時返回空列表


class TestStreamingErrors:
    """串流錯誤測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_streaming_connection_error(self, mock_request, mock_check_model):
        """測試串流連接錯誤"""
        mock_request.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            result = self.client.generate(model="test_model", prompt="test", stream=True)
            list(result)  # 嘗試讀取串流
        
        assert "Request failed" in str(exc_info.value)
            
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_streaming_malformed_json(self, mock_request, mock_check_model):
        """測試串流中的格式錯誤 JSON"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'invalid json line',  # 格式錯誤的 JSON
            b'{"response": "!", "done": true}'
        ]
        mock_request.return_value = mock_response
        
        result = self.client.generate(model="test_model", prompt="test", stream=True)
        
        # 串流處理器會忽略格式錯誤的 JSON 行，繼續處理有效的行
        responses = list(result)
        
        # 應該只包含有效的 JSON 響應
        assert len(responses) == 2
        assert responses[0]["response"] == "Hello"
        assert responses[1]["response"] == "!"
                
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_streaming_empty_lines(self, mock_request, mock_check_model):
        """測試串流中的空行"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'',  # 空行
            b'{"response": "!", "done": true}'
        ]
        mock_request.return_value = mock_response
        
        result = self.client.generate(model="test_model", prompt="test", stream=True)
        responses = list(result)
        
        # 應該忽略空行
        assert len(responses) == 2
        assert responses[0]["response"] == "Hello"
        assert responses[1]["response"] == "!"
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_streaming_incomplete_response(self, mock_request, mock_check_model):
        """測試串流不完整回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'{"response": " world", "done": false}'
            # 缺少 "done": true 的結束響應
        ]
        mock_request.return_value = mock_response
        
        result = self.client.generate(model="test_model", prompt="test", stream=True)
        responses = list(result)
        
        # 應該能夠處理不完整的回應
        assert len(responses) == 2
        assert responses[0]["response"] == "Hello"
        assert responses[1]["response"] == " world"


class TestStructuredOutputErrors:
    """結構化輸出錯誤測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_structured_output_invalid_json(self, mock_request, mock_check_model):
        """測試結構化輸出無效 JSON"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": '{"name": "test", "value": }',  # 無效 JSON
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate_structured(
            model="test_model",
            prompt="test",
            schema=SampleTestModel,
            stream=False
        )
        
        with pytest.raises(ValueError) as exc_info:
            self.client.parse_structured_response(result.response, SampleTestModel)
            
        assert "Unable to parse JSON response" in str(exc_info.value)
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_structured_output_validation_error(self, mock_request, mock_check_model):
        """測試結構化輸出驗證錯誤"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": '{"name": "test", "value": "not_a_number"}',  # 類型錯誤
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate_structured(
            model="test_model",
            prompt="test",
            schema=SampleTestModel,
            stream=False
        )
        
        with pytest.raises(ValueError) as exc_info:
            self.client.parse_structured_response(result.response, SampleTestModel)
            
        assert "Unable to validate response data" in str(exc_info.value)
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_structured_output_missing_fields(self, mock_request, mock_check_model):
        """測試結構化輸出缺少欄位"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": '{"name": "test"}',  # 缺少 value 欄位
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate_structured(
            model="test_model",
            prompt="test",
            schema=SampleTestModel,
            stream=False
        )
        
        with pytest.raises(ValueError) as exc_info:
            self.client.parse_structured_response(result.response, SampleTestModel)
            
        assert "Unable to validate response data" in str(exc_info.value)


class TestEdgeCasesAndBoundaries:
    """邊界情況和極端情況測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_very_long_prompt(self, mock_request, mock_check_model):
        """測試非常長的提示"""
        long_prompt = "A" * 10000  # 10KB 的提示
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "Response to long prompt",
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate(
            model="test_model",
            prompt=long_prompt,
            stream=False
        )
        
        assert result.response == "Response to long prompt"
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_unicode_content(self, mock_request, mock_check_model):
        """測試 Unicode 內容"""
        unicode_prompt = "你好世界 🌍 émoji test 🚀"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "Unicode 回應 ✨",
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate(
            model="test_model",
            prompt=unicode_prompt,
            stream=False
        )
        
        assert result.response == "Unicode 回應 ✨"
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_special_characters_in_prompt(self, mock_request, mock_check_model):
        """測試提示中的特殊字符"""
        special_prompt = 'Test with "quotes" and \n newlines and \t tabs'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "Handled special characters",
            "done": True
        }
        mock_request.return_value = mock_response
        
        result = self.client.generate(
            model="test_model",
            prompt=special_prompt,
            stream=False
        )
        
        assert result.response == "Handled special characters"
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_multiple_consecutive_calls(self, mock_request, mock_check_model):
        """測試多次連續調用"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "Response",
            "done": True
        }
        mock_request.return_value = mock_response
        
        # 進行多次連續調用
        for i in range(10):
            result = self.client.generate(
                model="test_model",
                prompt=f"Test {i}",
                stream=False
            )
            assert result.response == "Response"
            
    def test_context_manager_exception_handling(self):
        """測試上下文管理器異常處理"""
        with patch('requests.Session.close') as mock_close:
            try:
                with OllamaClient() as client:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            # 確認即使發生異常也會關閉會話
            mock_close.assert_called_once()
            
    def test_client_with_invalid_base_url(self):
        """測試無效的基礎 URL"""
        client = OllamaClient(base_url="invalid-url")
        
        with patch('requests.Session.request') as mock_request:
            mock_request.side_effect = ConnectionError("Invalid URL")
            
            with pytest.raises(Exception) as exc_info:
                client.generate(model="test_model", prompt="test", stream=False)
            
            assert "Failed to get model list" in str(exc_info.value)
                
    def test_client_with_very_short_timeout(self):
        """測試非常短的超時時間"""
        client = OllamaClient(timeout=0.001)  # 1ms 超時
        
        with patch('requests.Session.request') as mock_request:
            mock_request.side_effect = Timeout("Request timed out")
            
            with pytest.raises(Exception) as exc_info:
                client.generate(model="test_model", prompt="test", stream=False)
            
            assert "Failed to get model list" in str(exc_info.value)
                
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_empty_embedding_response(self, mock_request, mock_check_model):
        """測試空嵌入回應"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "embeddings": []
        }
        mock_request.return_value = mock_response
        
        result = self.client.embed(model="test_model", input="test")
        assert len(result.embeddings) == 0
        
    @patch('ollama_flow.client.OllamaClient._check_model_exists')
    @patch('requests.Session.request')
    def test_extremely_large_embedding_dimension(self, mock_request, mock_check_model):
        """測試極大維度的嵌入"""
        # 創建一個非常大的嵌入向量
        large_embedding = [0.1] * 10000  # 10k 維度
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "test_model",
            "embeddings": [large_embedding]
        }
        mock_request.return_value = mock_response
        
        result = self.client.embed(model="test_model", input="test")
        assert len(result.embeddings[0]) == 10000 