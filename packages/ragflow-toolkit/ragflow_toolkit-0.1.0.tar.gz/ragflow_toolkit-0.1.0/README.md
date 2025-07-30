# ragflow-toolkit

基于 ragflow-sdk 的高可用、ORM 风格 RAGFlow Python 工具包，支持数据集、文档、对话助手、智能体等全流程管理。

---

## 安装

```bash
pip install ragflow-toolkit
# 依赖 ragflow-sdk
pip install ragflow-sdk
```

---

## 快速上手

```python
from ragflow_toolkit import RagflowClient

client = RagflowClient(api_key="your-api-key", base_url="http://your-ragflow-server:9380")

# 数据集操作
dataset = client.datasets.create(name="my_kb")
doc = dataset.documents.upload("file.txt")
doc.parse()
results = dataset.retrieve(question="你的问题？")

# 对话助手
chat = client.chats.create(name="助手", dataset_ids=[dataset.id])
session = chat.sessions.create()
response = session.ask("你好")

# 智能体
agent = client.agents.create(title="智能体", dsl={})
agent_session = agent.sessions.create()
agent_session.ask("请帮我分析一下……")
```

---

## 核心 API 参考

### RagflowClient

- `datasets`：数据集管理器
- `chats`：对话助手管理器
- `agents`：智能体管理器

### DatasetManager / Dataset

- `create(name, ...)`：创建数据集
- `list(...)`：查询数据集
- `delete(ids)`：删除数据集
- `update(update_message)`：更新数据集
- `retrieve(question, ...)`：检索内容
- `documents.upload(file_path, ...)`：上传文档
- `documents.list(...)`：查询文档
- `documents.delete(ids)`：删除文档

### ChatManager / Chat / Session

- `create(name, dataset_ids, ...)`：创建对话助手
- `list(...)`：查询对话助手
- `delete(ids)`：删除对话助手
- `sessions.create()`：创建会话
- `sessions.list()`：查询会话
- `session.ask(question)`：提问

### AgentManager / Agent / AgentSession

- `create(title, dsl, ...)`：创建智能体
- `list(...)`：查询智能体
- `delete(agent_id)`：删除智能体
- `sessions.create()`：创建智能体会话
- `sessions.list()`：查询智能体会话
- `session.ask(question)`：提问

---

## 异常与错误处理

所有接口均可能抛出如下异常：

- `RagflowError`：基类异常
- `NetworkError`：网络异常
- `AuthError`：认证异常
- `NotFoundError`：资源未找到
- `BadRequestError`：参数错误
- `ServerError`：服务端错误
- `SDKError`：SDK 内部错误

建议用 try/except 捕获并处理。

---

## 测试

```bash
pytest tests/
```

---

## 贡献 & 联系

欢迎 issue、PR 及建议！  
如需定制开发或企业支持，请联系 maintainer@example.com

---

## License

MIT

## 进阶用法

### 1. Manager 的 get/list/create/delete 用法

```python
# 获取单个数据集
kb = client.datasets.get(name="药品")
# 获取所有数据集
all_kb = client.datasets.list()
# 创建数据集
new_kb = client.datasets.create(name="新知识库")
# 删除数据集
client.datasets.delete([kb.id])

# 获取单个文档
doc = kb.documents.get(name="说明书.pdf")
# 获取所有文档
docs = kb.documents.list()
# 上传文档
new_doc = kb.documents.upload(file_path="说明书.pdf")
# 删除文档
kb.documents.delete([doc.id])
```

### 2. 检索（retrieve）Pydantic 参数模型用法

```python
from ragflow_toolkit.dataset import RetrieveParams
params = RetrieveParams(
    question="什么是布洛芬？",
    page=1,
    page_size=10,
    highlight=True
)
results = kb.retrieve(params)
```

### 3. property 代理用法

```python
# 文档下的 chunk
chunks = doc.chunks.list()
chunk = doc.chunks.get(id="chunk_id")

# 对话助手下的会话
sessions = chat.sessions.list()
session = chat.sessions.get(name="会话1")

# 智能体下的会话
agent_sessions = agent.sessions.list()
```

### 4. Mock 测试

```python
from unittest.mock import patch, MagicMock
with patch("ragflow_toolkit.dataset.RAGFlow") as MockRAGFlow:
    mock_sdk = MagicMock()
    MockRAGFlow.return_value = mock_sdk
    client = RagflowClient(api_key="test", base_url="http://mock")
    # 配置 mock_sdk.create_dataset 等方法返回值
```

### 5. 异常处理

```python
from ragflow_toolkit import RagflowError, NotFoundError
try:
    ds = client.datasets.get(name="不存在的库")
    if not ds:
        raise NotFoundError("数据集不存在")
except RagflowError as e:
    print("操作失败：", e)
```

### 6. 对象序列化

```python
# Dataset/Document/Chunk 等对象均支持 .dict()/.json()
print(ds.dict())
print(doc.json())
```

---

## 常见问题（FAQ）

**Q: 如何获取某个数据集下的某个文档？**
A: `doc = ds.documents.get(name="xxx")` 或 `doc = ds.documents.get(id="xxx")`

**Q: 如何获取文档下所有 chunk？**
A: `chunks = doc.chunks.list()`

**Q: 如何检索时传递所有 ragflow-sdk 支持的参数？**
A: 用 `RetrieveParams` Pydantic 模型，所有参数都能类型安全传递。

**Q: 如何 mock ragflow-sdk 进行单元测试？**
A: 见上方“Mock 测试”用法。

**Q: 如何处理 ragflow-toolkit 抛出的异常？**
A: 捕获 `RagflowError` 及其子类，见上方“异常处理”用法。

**Q: 如何序列化 ORM 对象？**
A: 直接用 `.dict()` 或 `.json()` 方法。

---

如有更多问题，欢迎提 issue 或联系维护者！