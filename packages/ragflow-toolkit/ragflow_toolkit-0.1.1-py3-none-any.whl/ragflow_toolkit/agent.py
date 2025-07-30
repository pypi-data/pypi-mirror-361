from typing import List, Optional, Any
from .types import ID
from .exceptions import RagflowError, BadRequestError, NotFoundError, ServerError
from pydantic import BaseModel, PrivateAttr, Field, ValidationError

try:
    from ragflow_sdk import RAGFlow
except ImportError:
    RAGFlow = None

class AgentSession(BaseModel):
    """
    智能体会话对象，支持消息交互。
    """
    id: ID
    agent: Optional['Agent'] = Field(default=None, exclude=True)
    _sdk_obj: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, **data):
        sdk_obj = data.pop('sdk_obj', None)
        super().__init__(**data)
        self._sdk_obj = sdk_obj

    def ask(self, question: str, stream: bool = False, **kwargs) -> Any:
        """
        向智能体会话提问。
        Args:
            question (str): 问题内容。
            stream (bool): 是否流式返回。
        Returns:
            Any: 回答内容。
        """
        if not self._sdk_obj:
            raise RagflowError("No underlying SDK object for ask.")
        try:
            return self._sdk_obj.ask(question=question, stream=stream, **kwargs)
        except Exception as e:
            raise ServerError(f"Failed to ask question: {e}")

    def delete(self):
        """
        删除智能体会话。
        Raises:
            ServerError: 删除失败。
        """
        if not self.agent or not self.agent._sdk_obj:
            raise RagflowError("No agent SDK object for delete operation.")
        try:
            self.agent._sdk_obj.delete_sessions(ids=[self.id])
        except Exception as e:
            raise ServerError(f"Failed to delete agent session: {e}")

class AgentSessionManager:
    """
    智能体会话管理器，用于创建、列出和删除智能体会话。
    """
    def __init__(self, agent: 'Agent'):
        """
        Args:
            agent (Agent): 所属智能体。
        """
        self.agent = agent
        self._sdk_obj = agent._sdk_obj  # ragflow_sdk.Agent 实例

    def create(self, **kwargs) -> AgentSession:
        """
        创建新的智能体会话。
        Args:
            **kwargs: 创建会话所需的参数。
        Returns:
            AgentSession: 创建的会话对象。
        Raises:
            ServerError: 创建失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No agent SDK object for create session.")
        if 'question' in kwargs:
            try:
                params = AgentSessionCreateParams(**kwargs)
            except ValidationError as e:
                raise BadRequestError(str(e))
        try:
            sdk_obj = self._sdk_obj.create_session(**kwargs)
            return AgentSession(id=sdk_obj.id, agent=self.agent, sdk_obj=sdk_obj)
        except Exception as e:
            raise ServerError(f"Failed to create agent session: {e}")

    def list(self, page: int = 1, page_size: int = 30, **kwargs) -> List[AgentSession]:
        """
        列出智能体会话。
        Args:
            page (int): 页码。
            page_size (int): 每页数量。
        Returns:
            List[AgentSession]: 会话列表。
        Raises:
            ServerError: 列出失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No agent SDK object for list sessions.")
        try:
            sdk_list = self._sdk_obj.list_sessions(page=page, page_size=page_size, **kwargs)
            return [AgentSession(id=s.id, agent=self.agent, sdk_obj=s) for s in sdk_list]
        except Exception as e:
            raise ServerError(f"Failed to list agent sessions: {e}")

    def delete(self, ids: List[ID]):
        """
        批量删除智能体会话。
        Args:
            ids (List[ID]): 会话 ID 列表。
        Raises:
            BadRequestError: 未提供会话 ID。
            ServerError: 删除失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No agent SDK object for delete sessions.")
        if not ids:
            raise BadRequestError("No agent session ids provided for deletion.")
        try:
            self._sdk_obj.delete_sessions(ids=ids)
        except Exception as e:
            raise ServerError(f"Failed to delete agent sessions: {e}")

    def get(self, *, id: str = None):
        """
        获取单个智能体会话，通过 id。
        Returns:
            AgentSession 或 None
        """
        sessions = self.list()
        if id:
            return next((s for s in sessions if s.id == id), None)
        return None

class Agent(BaseModel):
    """
    智能体对象，代表一个 AI 模型或服务。
    """
    id: ID
    title: str
    _client: Optional[Any] = PrivateAttr(default=None)
    _sdk_obj: Optional[Any] = PrivateAttr(default=None)
    _sessions: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, **data):
        sdk_obj = data.pop('sdk_obj', None)
        client = data.pop('client', None)
        super().__init__(**data)
        self._sdk_obj = sdk_obj
        self._client = client
        self._sessions = AgentSessionManager(self)

    @property
    def sessions(self):
        """
        智能体下的会话管理器，支持 list、create、delete、get 等操作。
        Returns:
            AgentSessionManager: 智能体会话管理器实例。
        """
        return self._sessions

    def update(self, update_message: dict):
        """
        更新智能体配置。
        Args:
            update_message (dict): 更新内容。
        Raises:
            RagflowError: 无 SDK 客户端。
            ServerError: 更新失败。
        """
        if not self._client or not hasattr(self._client, '_sdk'):
            raise RagflowError("No SDK client for update operation.")
        try:
            self._client._sdk.update_agent(agent_id=self.id, **update_message)
        except Exception as e:
            raise ServerError(f"Failed to update agent: {e}")

    def delete(self):
        """
        删除智能体。
        Raises:
            RagflowError: 无 SDK 客户端。
            ServerError: 删除失败。
        """
        if not self._client or not hasattr(self._client, '_sdk'):
            raise RagflowError("No SDK client for delete operation.")
        try:
            self._client._sdk.delete_agent(agent_id=self.id)
        except Exception as e:
            raise ServerError(f"Failed to delete agent: {e}")

class AgentCreateParams(BaseModel):
    title: str = Field(..., min_length=1, description="智能体标题")
    dsl: dict = Field(..., description="智能体 DSL 配置")

class AgentSessionCreateParams(BaseModel):
    question: str = Field(..., min_length=1, description="提问内容")

class AgentManager:
    """
    智能体管理器，用于创建、列出和删除智能体。
    """
    def __init__(self, client):
        """
        Args:
            client: 客户端对象。
        Raises:
            ImportError: ragflow-sdk 未安装。
        """
        self.client = client
        if RAGFlow is None:
            raise ImportError("ragflow-sdk is required. Please install it via 'pip install ragflow-sdk'.")
        self._sdk = RAGFlow(api_key=client.api_key, base_url=client.base_url)
        client._sdk = self._sdk

    def create(self, title: str, dsl: dict, description: Optional[str] = None) -> Agent:
        try:
            params = AgentCreateParams(title=title, dsl=dsl)
        except ValidationError as e:
            raise BadRequestError(str(e))
        if not title or not dsl:
            raise BadRequestError("Agent title and dsl are required.")
        try:
            self._sdk.create_agent(title=title, dsl=dsl, description=description)
            # 获取最新 agent
            agents = self.list(page=1, page_size=1, title=title)
            if not agents:
                raise NotFoundError("Created agent not found.")
            return agents[0]
        except Exception as e:
            raise ServerError(f"Failed to create agent: {e}")

    def list(self, page: int = 1, page_size: int = 30, **kwargs) -> List[Agent]:
        """
        列出智能体。
        Args:
            page (int): 页码。
            page_size (int): 每页数量。
        Returns:
            List[Agent]: 智能体列表。
        Raises:
            ServerError: 列出失败。
        """
        try:
            sdk_list = self._sdk.list_agents(page=page, page_size=page_size, **kwargs)
            return [Agent(id=agent.id, title=agent.title, client=self.client, sdk_obj=agent) for agent in sdk_list]
        except Exception as e:
            raise ServerError(f"Failed to list agents: {e}")

    def delete(self, agent_id: ID):
        """
        删除智能体。
        Args:
            agent_id (ID): 智能体 ID。
        Raises:
            BadRequestError: 未提供智能体 ID。
            ServerError: 删除失败。
        """
        if not agent_id:
            raise BadRequestError("No agent id provided for deletion.")
        try:
            self._sdk.delete_agent(agent_id=agent_id)
        except Exception as e:
            raise ServerError(f"Failed to delete agent: {e}") 