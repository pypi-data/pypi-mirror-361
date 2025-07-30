"""
pytest 配置文件
定義測試夾具和共享設置
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from typing import Dict, Any

from ollama_flow import OllamaClient, ChatMessage


@pytest.fixture
def mock_ollama_client():
    """創建模擬的 Ollama 客戶端"""
    client = OllamaClient(base_url="http://localhost:11434")
    return client


@pytest.fixture
def mock_models_response():
    """創建模擬的模型列表回應"""
    return {
        "models": [
            {"name": "llama3.2", "size": 1000000},
            {"name": "qwen3:4b", "size": 2000000},
            {"name": "all-minilm", "size": 500000}
        ]
    }


@pytest.fixture
def mock_generate_response():
    """創建模擬的生成回應"""
    return {
        "model": "llama3.2",
        "response": "This is a test response.",
        "done": True,
        "total_duration": 1000000000,
        "load_duration": 500000000,
        "eval_count": 20,
        "eval_duration": 800000000
    }


@pytest.fixture
def mock_chat_response():
    """創建模擬的聊天回應"""
    return {
        "model": "llama3.2",
        "message": {
            "role": "assistant",
            "content": "Hello! How can I help you today?"
        },
        "done": True,
        "total_duration": 1500000000
    }


@pytest.fixture
def mock_embed_response():
    """創建模擬的嵌入回應"""
    return {
        "embeddings": [
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.6, 0.7, 0.8, 0.9, 1.0]
        ]
    }


@pytest.fixture
def sample_chat_messages():
    """創建樣本聊天訊息"""
    return [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there!"),
        ChatMessage(role="user", content="How are you?")
    ]


@pytest.fixture
def mock_streaming_response():
    """創建模擬的串流回應"""
    return [
        b'{"response": "Hello", "done": false}',
        b'{"response": " there", "done": false}',
        b'{"response": "!", "done": true, "total_duration": 1000000000}'
    ]


@pytest.fixture
def temp_directory():
    """創建臨時目錄"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_requests_session():
    """模擬 requests.Session（非自動使用）"""
    with patch('requests.Session') as mock_session:
        yield mock_session


@pytest.fixture
def mock_successful_http_response():
    """創建成功的 HTTP 回應模擬"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.fixture
def mock_error_http_response():
    """創建錯誤的 HTTP 回應模擬"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    return mock_response


@pytest.fixture(scope="session")
def test_data_dir():
    """測試數據目錄"""
    return os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture
def json_test_data():
    """JSON 測試數據"""
    return {
        "valid_person": {
            "name": "張三",
            "age": 30,
            "skills": ["Python", "JavaScript"]
        },
        "invalid_person": {
            "name": "李四",
            "age": "not_a_number",
            "skills": "not_a_list"
        }
    }


# 測試標記
def pytest_configure(config):
    """配置 pytest"""
    config.addinivalue_line(
        "markers", "unit: 單元測試"
    )
    config.addinivalue_line(
        "markers", "integration: 整合測試"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速測試"
    )
    config.addinivalue_line(
        "markers", "network: 需要網絡的測試"
    )


# 測試收集鉤子
def pytest_collection_modifyitems(config, items):
    """修改測試項目"""
    # 為測試添加標記
    for item in items:
        # 根據文件名添加標記
        if "test_client" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_models" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_schemas" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_errors" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            
        # 標記需要網絡的測試
        if "network" in item.name.lower():
            item.add_marker(pytest.mark.network)
            
        # 標記慢速測試
        if "slow" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# 測試報告鉤子
def pytest_report_header(config):
    """自定義測試報告標題"""
    testpaths = getattr(config.option, 'testpaths', None) or getattr(config, 'testpaths', ['tests'])
    return [
        "Ollama Flow 測試套件",
        "=" * 60,
        f"測試目錄: {testpaths}",
        f"Pytest 版本: {pytest.__version__}",
        "=" * 60
    ]


# 測試失敗時的額外信息
@pytest.fixture(autouse=True)
def test_context(request):
    """為測試添加上下文信息"""
    # 測試開始前
    test_name = request.node.name
    test_file = request.node.fspath.basename
    
    # 可以在這裡添加測試開始的日誌
    print(f"\n開始測試: {test_file}::{test_name}")
    
    yield
    
    # 測試結束後
    print(f"結束測試: {test_file}::{test_name}")


# 參數化測試數據
@pytest.fixture(params=[
    {"temperature": 0.7, "top_p": 0.9},
    {"temperature": 0.5, "top_p": 0.8},
    {"temperature": 1.0, "top_p": 1.0}
])
def generation_options(request):
    """生成選項參數"""
    return request.param


@pytest.fixture(params=[
    "單行文本",
    "多行\n文本\n測試",
    "包含特殊字符的文本: !@#$%^&*()",
    "Unicode 文本: 你好世界 🌍"
])
def text_inputs(request):
    """文本輸入參數"""
    return request.param 