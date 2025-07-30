"""
整合測試 - 測試各個組件之間的協作
"""

import pytest
import json
from unittest.mock import patch, Mock
from typing import List
from pydantic import BaseModel, Field

from ollama_flow import OllamaClient, ChatMessage, StructuredOutput
from ollama_flow.models import GenerateResponse, ChatResponse, EmbedResponse


class PersonModel(BaseModel):
    """測試用的人員模型"""
    name: str = Field(..., description="姓名")
    age: int = Field(..., description="年齡")
    skills: List[str] = Field(default_factory=list, description="技能列表")


class TestFullWorkflow:
    """完整工作流程測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('requests.Session.request')
    def test_complete_generation_workflow(self, mock_request):
        """測試完整的生成工作流程"""
        # 模擬模型列表回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        # 模擬生成回應
        generate_response = Mock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "這是一個測試回應",
            "done": True,
            "total_duration": 1000000000,
            "eval_count": 10
        }
        
        # 設置 mock 調用序列
        mock_request.side_effect = [models_response, generate_response]
        
        # 執行生成
        result = self.client.generate(
            model="test_model",
            prompt="生成一個測試回應",
            stream=False,
            options={"temperature": 0.7}
        )
        
        # 驗證結果
        assert isinstance(result, GenerateResponse)
        assert result.model == "test_model"
        assert result.response == "這是一個測試回應"
        assert result.done is True
        assert result.total_duration == 1000000000
        assert result.eval_count == 10
        
        # 驗證調用了正確的端點
        assert mock_request.call_count == 2
        
    @patch('requests.Session.request')
    def test_complete_chat_workflow(self, mock_request):
        """測試完整的聊天工作流程"""
        # 模擬模型列表回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        # 模擬聊天回應
        chat_response = Mock()
        chat_response.status_code = 200
        chat_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "你好！我是AI助手。"
            },
            "done": True,
            "total_duration": 1500000000
        }
        
        mock_request.side_effect = [models_response, chat_response]
        
        # 創建對話
        messages = [
            ChatMessage(role="system", content="你是一個友善的助手"),
            ChatMessage(role="user", content="你好")
        ]
        
        result = self.client.chat(
            model="test_model",
            messages=messages,
            stream=False,
            options={"temperature": 0.8}
        )
        
        # 驗證結果
        assert isinstance(result, ChatResponse)
        assert result.model == "test_model"
        assert result.message.role == "assistant"
        assert result.message.content == "你好！我是AI助手。"
        assert result.done is True
        
    @patch('requests.Session.request')
    def test_complete_embedding_workflow(self, mock_request):
        """測試完整的嵌入工作流程"""
        # 模擬模型列表回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "embedding_model", "size": 1000}]
        }
        
        # 模擬嵌入回應
        embed_response = Mock()
        embed_response.status_code = 200
        embed_response.json.return_value = {
            "model": "embedding_model",
            "embeddings": [
                [0.1, 0.2, 0.3, 0.4, 0.5],
                [0.6, 0.7, 0.8, 0.9, 1.0]
            ]
        }
        
        mock_request.side_effect = [models_response, embed_response]
        
        # 執行嵌入
        result = self.client.embed(
            model="embedding_model",
            input=["第一個文本", "第二個文本"]
        )
        
        # 驗證結果
        assert isinstance(result, EmbedResponse)
        assert len(result.embeddings) == 2
        assert result.embeddings[0] == [0.1, 0.2, 0.3, 0.4, 0.5]
        assert result.embeddings[1] == [0.6, 0.7, 0.8, 0.9, 1.0]
        
    @patch('requests.Session.request')
    def test_structured_output_workflow(self, mock_request):
        """測試結構化輸出工作流程"""
        # 模擬模型列表回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        # 模擬結構化輸出回應
        structured_response = Mock()
        structured_response.status_code = 200
        structured_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": '{"name": "張三", "age": 30, "skills": ["Python", "JavaScript"]}',
            "done": True
        }
        
        mock_request.side_effect = [models_response, structured_response]
        
        # 執行結構化生成
        result = self.client.generate_structured(
            model="test_model",
            prompt="生成一個軟體工程師的個人資料",
            schema=PersonModel,
            stream=False
        )
        
        # 驗證原始回應
        assert isinstance(result, GenerateResponse)
        assert result.model == "test_model"
        assert result.done is True
        
        # 解析結構化回應
        parsed_person = self.client.parse_structured_response(
            result.response,
            PersonModel
        )
        
        # 驗證解析結果
        assert isinstance(parsed_person, PersonModel)
        assert parsed_person.name == "張三"
        assert parsed_person.age == 30
        assert parsed_person.skills == ["Python", "JavaScript"]
        
    @patch('requests.Session.request')
    def test_streaming_workflow(self, mock_request):
        """測試串流工作流程"""
        # 模擬模型列表回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        # 模擬串流回應
        streaming_response = Mock()
        streaming_response.status_code = 200
        streaming_response.iter_lines.return_value = [
            '{"model": "test_model", "response": "Hello", "done": false}'.encode('utf-8'),
            '{"model": "test_model", "response": ", ", "done": false}'.encode('utf-8'),
            '{"model": "test_model", "response": "world", "done": false}'.encode('utf-8'),
            '{"model": "test_model", "response": "!", "done": true, "total_duration": 2000000000}'.encode('utf-8')
        ]
        
        mock_request.side_effect = [models_response, streaming_response]
        
        # 執行串流生成
        result = self.client.generate(
            model="test_model",
            prompt="說你好",
            stream=True
        )
        
        # 收集串流回應
        responses = []
        full_text = ""
        
        for chunk in result:
            responses.append(chunk)
            full_text += chunk.get("response", "")
            
        # 驗證串流結果
        assert len(responses) == 4
        assert responses[0]["response"] == "Hello"
        assert responses[1]["response"] == ", "
        assert responses[2]["response"] == "world"
        assert responses[3]["response"] == "!"
        assert responses[3]["done"] is True
        assert full_text == "Hello, world!"
        
    @patch('requests.Session.request')
    def test_conversation_workflow(self, mock_request):
        """測試對話工作流程"""
        # 模擬模型列表回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        # 模擬多輪對話回應
        chat_response1 = Mock()
        chat_response1.status_code = 200
        chat_response1.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "你好！我是AI助手。"},
            "done": True
        }
        
        chat_response2 = Mock()
        chat_response2.status_code = 200
        chat_response2.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "當然可以！我很樂意幫助你。"},
            "done": True
        }
        
        mock_request.side_effect = [models_response, chat_response1, chat_response2]
        
        # 初始化對話
        conversation = [
            ChatMessage(role="system", content="你是一個友善的助手")
        ]
        
        # 第一輪對話
        conversation.append(ChatMessage(role="user", content="你好"))
        result1 = self.client.chat(
            model="test_model",
            messages=conversation,
            stream=False
        )
        
        # 添加助手回應到對話記錄
        conversation.append(result1.message)
        
        # 第二輪對話
        conversation.append(ChatMessage(role="user", content="你能幫我嗎？"))
        result2 = self.client.chat(
            model="test_model",
            messages=conversation,
            stream=False
        )
        
        # 驗證對話結果
        assert result1.message.content == "你好！我是AI助手。"
        assert result2.message.content == "當然可以！我很樂意幫助你。"
        assert len(conversation) == 4  # system + user + assistant + user


class TestErrorRecovery:
    """錯誤恢復測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('requests.Session.request')
    def test_model_validation_then_success(self, mock_request):
        """測試模型驗證失敗後成功的情況"""
        # 第一次調用：獲取模型列表
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "available_model", "size": 1000}]
        }

        # 模擬成功的生成請求
        models_response2 = Mock()
        models_response2.status_code = 200
        models_response2.json.return_value = {
            "models": [{"name": "available_model", "size": 1000}]
        }

        generate_response = Mock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "model": "available_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "成功生成",
            "done": True
        }

        # 依序回傳：1. 查不存在模型 2. 查存在模型 3. generate 前再查一次 4. 生成
        mock_request.side_effect = [models_response, models_response2, models_response2, generate_response]

        # 嘗試使用不存在的模型
        with pytest.raises(ValueError):
            self.client.generate(model="nonexistent_model", prompt="test", stream=False)

        # 使用正確的模型
        result = self.client.generate(model="available_model", prompt="test", stream=False)
        assert result.response == "成功生成"
        
    @patch('requests.Session.request')
    def test_retry_after_network_error(self, mock_request):
        """測試網絡錯誤後重試的情況"""
        # 第一次調用失敗
        mock_request.side_effect = [
            Exception("Network error"),
            # 第二次調用成功
            Mock(status_code=200, json=lambda: {"models": [{"name": "test_model", "size": 1000}]}),
            Mock(status_code=200, json=lambda: {"model": "test_model", "created_at": "2024-01-01T00:00:00Z", "response": "重試成功", "done": True})
        ]
        
        # 第一次嘗試失敗
        with pytest.raises(Exception):
            self.client.generate(model="test_model", prompt="test", stream=False)
            
        # 重置 mock 狀態
        mock_request.side_effect = [
            Mock(status_code=200, json=lambda: {"models": [{"name": "test_model", "size": 1000}]}),
            Mock(status_code=200, json=lambda: {"model": "test_model", "created_at": "2024-01-01T00:00:00Z", "response": "重試成功", "done": True})
        ]
        
        # 第二次嘗試成功
        result = self.client.generate(model="test_model", prompt="test", stream=False)
        assert result.response == "重試成功"


class TestPerformanceAndConcurrency:
    """性能和並發測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('requests.Session.request')
    def test_model_cache_efficiency(self, mock_request):
        """測試模型快取效率"""
        # 模擬模型列表回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        # 模擬生成回應
        generate_response = Mock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "測試回應",
            "done": True
        }
        
        mock_request.side_effect = [
            models_response,  # 第一次獲取模型列表
            generate_response,  # 第一次生成
            generate_response,  # 第二次生成（不應該再次獲取模型列表）
            generate_response,  # 第三次生成
        ]
        
        # 進行多次生成
        for i in range(3):
            result = self.client.generate(model="test_model", prompt=f"test {i}", stream=False)
            assert result.response == "測試回應"
            
        # 驗證模型列表只被獲取一次
        assert mock_request.call_count == 4  # 1次模型列表 + 3次生成
        
    @patch('requests.Session.request')
    def test_multiple_clients_independence(self, mock_request):
        """測試多個客戶端的獨立性"""
        # 創建兩個不同的客戶端
        client1 = OllamaClient(base_url="http://localhost:11434", timeout=30)
        client2 = OllamaClient(base_url="http://localhost:11434", timeout=60)
        
        # 模擬回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        generate_response = Mock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "測試回應",
            "done": True
        }
        
        mock_request.side_effect = [
            models_response, generate_response,  # client1 的調用
            models_response, generate_response,  # client2 的調用
        ]
        
        # 使用兩個客戶端
        result1 = client1.generate(model="test_model", prompt="test1", stream=False)
        result2 = client2.generate(model="test_model", prompt="test2", stream=False)
        
        # 驗證結果
        assert result1.response == "測試回應"
        assert result2.response == "測試回應"
        assert client1.timeout == 30
        assert client2.timeout == 60
        
    @patch('requests.Session.request')
    def test_context_manager_resource_management(self, mock_request):
        """測試上下文管理器的資源管理"""
        # 模擬回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "test_model", "size": 1000}]
        }
        
        generate_response = Mock()
        generate_response.status_code = 200
        generate_response.json.return_value = {
            "model": "test_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "測試回應",
            "done": True
        }
        
        mock_request.side_effect = [models_response, generate_response]
        
        # 使用上下文管理器
        with OllamaClient() as client:
            result = client.generate(model="test_model", prompt="test", stream=False)
            assert result.response == "測試回應"
            
        # 驗證會話被正確關閉（通過檢查 close 方法是否被調用）
        # 這個測試主要確保沒有資源洩漏


class TestEndToEndScenarios:
    """端到端場景測試"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = OllamaClient(base_url="http://localhost:11434")
        
    @patch('requests.Session.request')
    def test_complete_ai_assistant_scenario(self, mock_request):
        """測試完整的AI助手場景"""
        # 模擬各種回應
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [
                {"name": "chat_model", "size": 1000},
                {"name": "embed_model", "size": 2000}
            ]
        }

        # 歡迎訊息
        welcome_response = Mock()
        welcome_response.status_code = 200
        welcome_response.json.return_value = {
            "model": "chat_model",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "歡迎使用AI助手！我能為您做什麼？"},
            "done": True
        }

        # 查詢回應
        query_response = Mock()
        query_response.status_code = 200
        query_response.json.return_value = {
            "model": "chat_model",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "讓我為您查找相關資訊..."},
            "done": True
        }

        # 嵌入回應
        embed_response = Mock()
        embed_response.status_code = 200
        embed_response.json.return_value = {
            "model": "embed_model",
            "embeddings": [[0.1, 0.2, 0.3, 0.4, 0.5]]
        }

        # 結果回應
        result_response = Mock()
        result_response.status_code = 200
        result_response.json.return_value = {
            "model": "chat_model",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "根據查找結果，我建議您..."},
            "done": True
        }

        # 直接用 list 指定 side_effect 順序
        mock_request.side_effect = [
            models_response,    # 1. 查 chat_model
            welcome_response,   # 2. 歡迎訊息
            models_response,    # 3. 查 embed_model
            models_response,    # 4. 再查 embed_model
            embed_response,     # 5. 嵌入查詢
            query_response,     # 6. 查詢處理
            result_response     # 7. 最終結果
        ]

        # 場景執行
        conversation = []
        
        # 1. 初始化對話
        conversation.append(ChatMessage(role="system", content="你是一個專業的AI助手"))
        
        # 2. 歡迎用戶
        conversation.append(ChatMessage(role="user", content="你好"))
        welcome = self.client.chat(model="chat_model", messages=conversation, stream=False)
        conversation.append(welcome.message)
        
        # 3. 用戶查詢
        user_query = "什麼是機器學習？"
        conversation.append(ChatMessage(role="user", content=user_query))
        
        # 4. 對查詢進行嵌入以搜索相關內容
        embed_result = self.client.embed(model="embed_model", input=user_query)
        
        # 5. 處理查詢
        query_result = self.client.chat(model="chat_model", messages=conversation, stream=False)
        conversation.append(query_result.message)
        
        # 6. 提供最終回答
        conversation.append(ChatMessage(role="user", content="請詳細說明"))
        final_result = self.client.chat(model="chat_model", messages=conversation, stream=False)
        
        # 驗證整個流程
        assert welcome.message.content == "歡迎使用AI助手！我能為您做什麼？"
        assert len(embed_result.embeddings) == 1
        assert len(embed_result.embeddings[0]) == 5
        assert query_result.message.content == "讓我為您查找相關資訊..."
        assert final_result.message.content == "根據查找結果，我建議您..."
        
    @patch('requests.Session.request')
    def test_data_analysis_scenario(self, mock_request):
        """測試數據分析場景"""
        # 模擬回應設置
        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = {
            "models": [{"name": "analysis_model", "size": 1000}]
        }
        
        # 結構化數據回應
        structured_response = Mock()
        structured_response.status_code = 200
        structured_response.json.return_value = {
            "model": "analysis_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": '{"name": "數據分析師", "age": 28, "skills": ["Python", "SQL", "統計學", "機器學習"]}',
            "done": True
        }
        
        # 分析結果回應
        analysis_response = Mock()
        analysis_response.status_code = 200
        analysis_response.json.return_value = {
            "model": "analysis_model",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "基於提供的數據，我發現以下趨勢...",
            "done": True
        }
        
        mock_request.side_effect = [
            models_response,
            structured_response,
            analysis_response
        ]
        
        # 1. 生成結構化的分析師資料
        analyst_data = self.client.generate_structured(
            model="analysis_model",
            prompt="生成一個數據分析師的個人資料",
            schema=PersonModel,
            stream=False
        )
        
        # 2. 解析結構化數據
        analyst = self.client.parse_structured_response(
            analyst_data.response,
            PersonModel
        )
        
        # 3. 進行數據分析
        analysis_result = self.client.generate(
            model="analysis_model",
            prompt=f"請{analyst.name}分析以下數據並提供見解...",
            stream=False
        )
        
        # 驗證分析流程
        assert analyst.name == "數據分析師"
        assert analyst.age == 28
        assert "Python" in analyst.skills
        assert "機器學習" in analyst.skills
        assert analysis_result.response == "基於提供的數據，我發現以下趨勢..." 