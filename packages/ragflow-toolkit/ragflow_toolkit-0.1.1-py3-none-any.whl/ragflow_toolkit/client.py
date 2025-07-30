from typing import Optional
from .exceptions import RagflowError
from .dataset import DatasetManager
from .chat import ChatManager
from .agent import AgentManager

class RagflowClient:
    """
    Ragflow-toolkit 的顶层入口，负责 API Key、Base URL、全局配置管理，
    并提供 datasets、chats、agents 三大资源的 ORM 管理器。

    Attributes:
        api_key (str): 认证用 API Key。
        base_url (str): ragflow 服务地址。
        datasets (DatasetManager): 数据集管理器。
        chats (ChatManager): 对话助手管理器。
        agents (AgentManager): 智能体管理器。
    """
    def __init__(self, api_key: str, base_url: str = "http://localhost:9380"):
        """
        初始化 RagflowClient。

        Args:
            api_key (str): 认证用 API Key。
            base_url (str): ragflow 服务地址，默认为本地。
        Raises:
            RagflowError: 若 api_key 为空。
        """
        if not api_key:
            raise RagflowError("API key is required.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        # 资源管理器
        self.datasets = DatasetManager(self)
        self.chats = ChatManager(self)
        self.agents = AgentManager(self)

    def __repr__(self):
        """返回客户端简要信息。"""
        return f"<RagflowClient base_url={self.base_url}>" 