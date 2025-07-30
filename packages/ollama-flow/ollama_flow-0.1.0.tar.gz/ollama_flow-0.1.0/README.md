# Ollama Flow

一個強大且易用的 Python 函式庫，用於與 Ollama API 互動。

## 功能特色

- 🚀 **簡潔易用的 API** - 提供直觀的 Python 介面
- 🎯 **結構化輸出** - 支援 JSON Schema 和 Pydantic 模型
- 🌊 **串流模式** - 即時獲取生成內容
- 💬 **完整聊天支援** - 支援多輪對話和工具調用
- 🔤 **嵌入向量** - 生成文本嵌入向量
- ✅ **智能模型驗證** - 自動檢查模型是否存在，提供友好的錯誤提示
- 💾 **緩存機制** - 智能緩存模型列表，提升性能
- 🛡️ **類型安全** - 完整的類型提示支援
- 📦 **零依賴** - 僅依賴 `requests` 和 `pydantic`

## 支援的 API 端點

- `/api/generate` - 生成完成
- `/api/chat` - 聊天完成
- `/api/embed` - 生成嵌入向量

## 安裝

```bash
pip install ollama-flow
```

或者從源碼安裝：

```bash
git clone https://github.com/your-username/ollama-flow.git
cd ollama-flow
pip install -e .
```

## 快速開始

### 基本使用

```python
from ollama_flow import OllamaClient

# 建立客戶端
client = OllamaClient(base_url="http://localhost:11434")

# 生成文本
response = client.generate(
    model="llama3.2",
    prompt="解釋什麼是機器學習？",
    stream=False
)
print(response.response)
```

### 聊天對話

```python
from ollama_flow import OllamaClient, ChatMessage

client = OllamaClient()

messages = [
    ChatMessage(role="system", content="你是一個有用的助手。"),
    ChatMessage(role="user", content="你好！")
]

response = client.chat(
    model="llama3.2",
    messages=messages,
    stream=False
)
print(response.message.content)
```

### 結構化輸出

```python
from ollama_flow import OllamaClient
from pydantic import BaseModel, Field
from typing import List

class Product(BaseModel):
    name: str = Field(..., description="產品名稱")
    price: float = Field(..., description="價格")
    features: List[str] = Field(..., description="功能特點")

client = OllamaClient()

# 使用 Pydantic 模型
response = client.generate_structured(
    model="llama3.2",
    prompt="創建一個智慧型手機產品資訊，請用 JSON 格式回應。",
    schema=Product,
    stream=False
)

# 解析結構化回應
product = client.parse_structured_response(response.response, Product)
print(f"產品名稱：{product.name}")
print(f"價格：${product.price}")
print(f"功能：{', '.join(product.features)}")
```

### 串流模式

```python
from ollama_flow import OllamaClient

client = OllamaClient()

response_stream = client.generate(
    model="llama3.2",
    prompt="寫一篇關於人工智慧的文章。",
    stream=True
)

print("生成中：", end="", flush=True)
for chunk in response_stream:
    if chunk.get("done", False):
        print("\n生成完成！")
        break
    else:
        print(chunk.get("response", ""), end="", flush=True)
```

### 生成嵌入向量

```python
from ollama_flow import OllamaClient

client = OllamaClient()

response = client.embed(
    model="all-minilm",
    input="這是要轉換為嵌入向量的文本。"
)

print(f"嵌入維度：{len(response.embeddings[0])}")
print(f"嵌入向量：{response.embeddings[0][:5]}...")  # 顯示前5個值
```

## 進階功能

### 模型驗證

```python
# 預設開啟模型驗證
client = OllamaClient(check_models=True)

# 獲取可用模型列表
models = client.list_models()
print(f"可用模型：{models}")

# 刷新模型緩存
models = client.refresh_models_cache()

# 關閉模型驗證（不推薦）
client_no_check = OllamaClient(check_models=False)

# 當使用不存在的模型時，會拋出 ValueError
try:
    client.generate(model="nonexistent-model", prompt="Hello")
except ValueError as e:
    print(f"模型驗證錯誤：{e}")
```

### JSON 模式

```python
# 使用 JSON 模式
response = client.generate_json(
    model="llama3.2",
    prompt="列出三個程式設計語言及其特點。請用 JSON 格式回應。",
    stream=False
)

import json
data = json.loads(response.response)
print(json.dumps(data, indent=2, ensure_ascii=False))
```

### 自定義 JSON Schema

```python
# 使用自定義 JSON Schema
person_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "hobbies": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "age"]
}

response = client.generate_structured(
    model="llama3.2",
    prompt="創建一個虛構角色的資訊。",
    schema=person_schema,
    stream=False
)
```

### 上下文管理器

```python
# 使用上下文管理器自動清理連線
with OllamaClient() as client:
    response = client.generate(
        model="llama3.2",
        prompt="你好！",
        stream=False
    )
    print(response.response)
```

## API 參考

### OllamaClient

主要的客戶端類別，提供與 Ollama API 的介面。

#### 初始化

```python
client = OllamaClient(
    base_url="http://localhost:11434",  # Ollama 服務器 URL
    timeout=30,  # 請求超時時間（秒）
    check_models=True  # 是否在調用前檢查模型是否存在
)
```

#### 方法

- `generate()` - 生成文本完成
- `chat()` - 聊天完成
- `embed()` - 生成嵌入向量
- `generate_json()` - 生成 JSON 格式回應
- `generate_structured()` - 生成結構化回應
- `chat_json()` - 聊天生成 JSON 格式回應
- `chat_structured()` - 聊天生成結構化回應
- `parse_structured_response()` - 解析結構化回應
- `list_models()` - 獲取可用模型列表
- `refresh_models_cache()` - 刷新模型緩存

### 資料模型

#### GenerateRequest
- `model`: 模型名稱
- `prompt`: 提示文本
- `format`: 回應格式（可選）
- `stream`: 是否使用串流模式
- `options`: 模型參數（可選）

#### ChatMessage
- `role`: 角色（system/user/assistant/tool）
- `content`: 訊息內容
- `images`: 圖像列表（可選）

#### ChatRequest
- `model`: 模型名稱
- `messages`: 對話訊息列表
- `format`: 回應格式（可選）
- `stream`: 是否使用串流模式
- `tools`: 工具定義（可選）

#### EmbedRequest
- `model`: 模型名稱
- `input`: 輸入文本或文本列表
- `truncate`: 是否截斷長文本

## 範例

查看 `examples/` 目錄中的詳細範例：

- `basic_usage.py` - 基本使用方法
- `structured_output.py` - 結構化輸出範例
- `streaming.py` - 串流模式範例
- `model_validation.py` - 模型驗證功能範例

## 錯誤處理

```python
from ollama_flow import OllamaClient

client = OllamaClient()

try:
    response = client.generate(
        model="llama3.2",
        prompt="你好！",
        stream=False
    )
    print(response.response)
except Exception as e:
    print(f"發生錯誤：{e}")
```

## 需求

- Python 3.7+
- requests >= 2.31.0
- pydantic >= 2.0.0
- 運行中的 Ollama 服務

## 許可證

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

1. Fork 這個專案
2. 建立您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的變更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟一個 Pull Request

## 更新日誌

### v0.1.0
- 初始發布
- 支援 generate, chat, embed API
- 結構化輸出支援
- 串流模式支援
- 智能模型驗證功能
- 模型列表緩存機制
- 完整的類型提示

## 相關連結

- [Ollama](https://ollama.com/) - 本地 LLM 運行平台
- [Ollama API 文檔](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Pydantic](https://docs.pydantic.dev/) - 資料驗證函式庫
