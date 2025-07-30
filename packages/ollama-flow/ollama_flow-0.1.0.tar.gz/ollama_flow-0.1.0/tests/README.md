# Ollama Flow 測試套件

這個測試套件提供了對 Ollama Flow 庫的全面測試覆蓋。

## 測試結構

```
tests/
├── __init__.py              # 測試模組初始化
├── conftest.py              # 共享測試配置和夾具
├── test_client.py           # OllamaClient 核心功能測試
├── test_models.py           # 數據模型驗證測試
├── test_schemas.py          # 結構化輸出和模式測試
├── test_errors.py           # 異常處理和邊界條件測試
├── test_integration.py      # 整合測試
└── README.md               # 此文檔
```

## 測試類型

### 1. 單元測試 (Unit Tests)
- **test_client.py**: 測試 OllamaClient 的各個方法
- **test_models.py**: 測試 Pydantic 數據模型
- **test_schemas.py**: 測試結構化輸出功能
- **test_errors.py**: 測試異常處理

### 2. 整合測試 (Integration Tests)
- **test_integration.py**: 測試組件間的協作

### 3. 錯誤處理測試
- 網絡錯誤
- 輸入驗證錯誤
- 模型驗證錯誤
- 串流錯誤
- 結構化輸出錯誤

## 運行測試

### 基本運行方式

```bash
# 運行所有測試
pytest

# 運行指定測試文件
pytest tests/test_client.py

# 運行指定測試函數
pytest tests/test_client.py::TestOllamaClient::test_generate_success

# 運行指定模式的測試
pytest -k "test_generate"
```

### 使用測試腳本

```bash
# 安裝測試依賴
python run_tests.py --install-deps

# 運行所有測試
python run_tests.py

# 運行單元測試
python run_tests.py --unit

# 運行整合測試
python run_tests.py --integration

# 生成覆蓋率報告
python run_tests.py --coverage --html

# 並行運行測試
python run_tests.py --parallel

# 詳細輸出
python run_tests.py --verbose

# 運行特定測試文件
python run_tests.py --file test_client.py

# 運行特定測試函數
python run_tests.py --function test_generate
```

### 覆蓋率報告

```bash
# 生成覆蓋率報告
pytest --cov=ollama_flow --cov-report=html --cov-report=term-missing

# 使用測試腳本生成覆蓋率報告
python run_tests.py --coverage --html
```

覆蓋率報告將生成在 `htmlcov/` 目錄中。

## 測試標記

測試使用以下標記進行分類：

- `@pytest.mark.unit`: 單元測試
- `@pytest.mark.integration`: 整合測試
- `@pytest.mark.slow`: 慢速測試
- `@pytest.mark.network`: 需要網絡連接的測試

```bash
# 只運行單元測試
pytest -m unit

# 只運行整合測試
pytest -m integration

# 排除慢速測試
pytest -m "not slow"

# 排除需要網絡的測試
pytest -m "not network"
```

## 模擬策略

測試使用以下模擬策略：

1. **HTTP 請求模擬**: 使用 `unittest.mock.patch` 模擬 `requests.Session.request`
2. **模型驗證模擬**: 模擬 `_check_model_exists` 方法
3. **串流回應模擬**: 使用 `iter_lines` 模擬串流回應
4. **錯誤條件模擬**: 模擬各種異常情況

## 測試數據

測試使用以下測試數據：

- **模型列表**: 包含 llama3.2、qwen3:4b、all-minilm 等
- **生成回應**: 包含完整的回應數據和統計信息
- **聊天回應**: 包含不同角色的訊息
- **嵌入回應**: 包含多維度的嵌入向量
- **結構化數據**: 包含人員、公司等模型的 JSON 數據

## 夾具 (Fixtures)

`conftest.py` 提供了以下共享夾具：

- `mock_ollama_client`: 模擬的 Ollama 客戶端
- `mock_models_response`: 模擬的模型列表回應
- `mock_generate_response`: 模擬的生成回應
- `mock_chat_response`: 模擬的聊天回應
- `mock_embed_response`: 模擬的嵌入回應
- `sample_chat_messages`: 樣本聊天訊息
- `mock_streaming_response`: 模擬的串流回應

## 性能測試

性能相關的測試包括：

- 模型快取效率測試
- 並發客戶端測試
- 大量數據處理測試
- 資源管理測試

## 邊界條件測試

測試涵蓋以下邊界條件：

- 空輸入
- 超長輸入
- 特殊字符
- Unicode 文本
- 無效格式
- 網絡超時
- 記憶體限制

## 持續集成

測試套件支持 CI/CD 環境：

```bash
# CI 環境運行
pytest --cov=ollama_flow --cov-report=xml --junit-xml=junit.xml

# 快速測試（排除慢速測試）
pytest -m "not slow"

# 並行測試
pytest -n auto
```

## 故障排除

### 常見問題

1. **導入錯誤**: 確保 ollama_flow 包已正確安裝
2. **依賴缺失**: 運行 `pip install -r test-requirements.txt`
3. **模擬失敗**: 檢查 mock 的設置是否正確

### 調試測試

```bash
# 顯示詳細錯誤信息
pytest -v --tb=long

# 進入 PDB 調試器
pytest --pdb

# 只運行失敗的測試
pytest --lf

# 停止在第一個失敗
pytest -x
```

## 貢獻指南

添加新測試時請遵循以下指南：

1. 為每個新功能添加相應的測試
2. 使用適當的測試標記
3. 添加必要的文檔字符串
4. 確保測試獨立且可重複
5. 使用模擬避免外部依賴
6. 測試邊界條件和錯誤情況

## 測試覆蓋率目標

- 總體覆蓋率: ≥90%
- 核心功能覆蓋率: ≥95%
- 分支覆蓋率: ≥85% 