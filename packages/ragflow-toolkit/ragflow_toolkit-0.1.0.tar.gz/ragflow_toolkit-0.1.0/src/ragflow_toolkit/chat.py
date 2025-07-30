from typing import List, Optional, Any
from .types import ID
from .exceptions import RagflowError, BadRequestError, NotFoundError, ServerError
from pydantic import BaseModel, PrivateAttr, Field, ValidationError

try:
    from ragflow_sdk import RAGFlow
except ImportError:
    RAGFlow = None

class Session(BaseModel):
    """
    对话会话对象，支持消息交互、历史记录等。
    """
    id: ID
    name: str
    chat: Optional['Chat'] = Field(default=None, exclude=True)
    _sdk_obj: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, **data):
        sdk_obj = data.pop('sdk_obj', None)
        super().__init__(**data)
        self._sdk_obj = sdk_obj

    def update(self, update_message: dict):
        """
        更新会话配置。
        Args:
            update_message (dict): 更新内容。
        Raises:
            ServerError: 更新失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No underlying SDK object for update.")
        try:
            self._sdk_obj.update(update_message)
        except Exception as e:
            raise ServerError(f"Failed to update session: {e}")

    def ask(self, question: str, stream: bool = False, **kwargs) -> Any:
        """
        向会话提问。
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
        删除会话。
        Raises:
            ServerError: 删除失败。
        """
        if not self.chat or not self.chat._sdk_obj:
            raise RagflowError("No chat SDK object for delete operation.")
        try:
            self.chat._sdk_obj.delete_sessions(ids=[self.id])
        except Exception as e:
            raise ServerError(f"Failed to delete session: {e}")

class SessionManager:
    """
    会话管理器，负责创建、列出和删除对话会话。
    """
    def __init__(self, chat: 'Chat'):
        """
        Args:
            chat (Chat): 所属对话助手。
        """
        self.chat = chat
        self._sdk_obj = chat._sdk_obj  # ragflow_sdk.Chat 实例

    def create(self, name: Optional[str] = None) -> Session:
        """
        创建新的对话会话。
        Args:
            name (str, optional): 会话名称，默认为 "New session"。
        Returns:
            Session: 创建的会话对象。
        Raises:
            ServerError: 创建失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No chat SDK object for create session.")
        try:
            params = SessionCreateParams(name=name or "New session")
            sdk_obj = self._sdk_obj.create_session(name=params.name)
            return Session(id=sdk_obj.id, name=sdk_obj.name, chat=self.chat, sdk_obj=sdk_obj)
        except ValidationError as e:
            raise BadRequestError(str(e))
        except Exception as e:
            raise ServerError(f"Failed to create session: {e}")

    def list(self, page: int = 1, page_size: int = 30, **kwargs) -> List[Session]:
        """
        列出对话会话。
        Args:
            page (int): 页码。
            page_size (int): 每页数量。
        Returns:
            List[Session]: 会话列表。
        Raises:
            ServerError: 列出失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No chat SDK object for list sessions.")
        try:
            sdk_list = self._sdk_obj.list_sessions(page=page, page_size=page_size, **kwargs)
            return [Session(id=s.id, name=s.name, chat=self.chat, sdk_obj=s) for s in sdk_list]
        except Exception as e:
            raise ServerError(f"Failed to list sessions: {e}")

    def delete(self, ids: List[ID]):
        """
        批量删除对话会话。
        Args:
            ids (List[ID]): 会话 ID 列表。
        Raises:
            BadRequestError: 未提供会话 ID。
            ServerError: 删除失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No chat SDK object for delete sessions.")
        if not ids:
            raise BadRequestError("No session ids provided for deletion.")
        try:
            self._sdk_obj.delete_sessions(ids=ids)
        except Exception as e:
            raise ServerError(f"Failed to delete sessions: {e}")

    def get(self, *, id: str = None, name: str = None):
        """
        获取单个会话，可通过 id 或 name。
        Returns:
            Session 或 None
        """
        sessions = self.list()
        if id:
            return next((s for s in sessions if s.id == id), None)
        if name:
            return next((s for s in sessions if s.name == name), None)
        return None

class Chat(BaseModel):
    """
    对话助手对象，包含多个对话会话。
    """
    id: ID
    name: str
    _client: Optional[Any] = PrivateAttr(default=None)
    _sdk_obj: Optional[Any] = PrivateAttr(default=None)
    _sessions: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, **data):
        sdk_obj = data.pop('sdk_obj', None)
        client = data.pop('client', None)
        super().__init__(**data)
        self._sdk_obj = sdk_obj
        self._client = client
        self._sessions = SessionManager(self)

    @property
    def sessions(self):
        """
        对话助手下的会话管理器，支持 list、create、delete、get 等操作。
        Returns:
            SessionManager: 会话管理器实例。
        """
        return self._sessions

    def update(self, update_message: dict):
        """
        更新对话助手配置。
        Args:
            update_message (dict): 更新内容。
        Raises:
            ServerError: 更新失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No underlying SDK object for update.")
        try:
            self._sdk_obj.update(update_message)
        except Exception as e:
            raise ServerError(f"Failed to update chat: {e}")

    def delete(self):
        """
        删除对话助手。
        Raises:
            RagflowError: 客户端或 SDK 客户端不存在。
            ServerError: 删除失败。
        """
        if not self._client or not hasattr(self._client, '_sdk'):
            raise RagflowError("No SDK client for delete operation.")
        try:
            self._client.chats.delete([self.id])
        except Exception as e:
            raise ServerError(f"Failed to delete chat: {e}")

class ChatCreateParams(BaseModel):
    name: str = Field(..., min_length=1, description="对话助手名称")

class SessionCreateParams(BaseModel):
    name: str = Field(..., min_length=1, description="会话名称")

class ChatManager:
    """
    对话助手管理器，负责创建、列出和删除对话助手。
    """
    def __init__(self, client):
        """
        Args:
            client: 客户端对象。
        """
        self.client = client
        if RAGFlow is None:
            raise ImportError("ragflow-sdk is required. Please install it via 'pip install ragflow-sdk'.")
        self._sdk = RAGFlow(api_key=client.api_key, base_url=client.base_url)
        client._sdk = self._sdk

    def create(self, name: str, **kwargs) -> Chat:
        """
        创建新的对话助手。
        Args:
            name (str): 对话助手名称。
        Returns:
            Chat: 创建的对话助手对象。
        Raises:
            BadRequestError: 对话助手名称缺失。
            ServerError: 创建失败。
        """
        try:
            params = ChatCreateParams(name=name)
        except ValidationError as e:
            raise BadRequestError(str(e))
        if not name:
            raise BadRequestError("Chat name is required.")
        try:
            sdk_obj = self._sdk.create_chat(name=name, **kwargs)
            return Chat(id=sdk_obj.id, name=sdk_obj.name, client=self.client, sdk_obj=sdk_obj)
        except Exception as e:
            raise ServerError(f"Failed to create chat: {e}")

    def list(self, page: int = 1, page_size: int = 30, **kwargs) -> List[Chat]:
        """
        列出对话助手。
        Args:
            page (int): 页码。
            page_size (int): 每页数量。
        Returns:
            List[Chat]: 对话助手列表。
        Raises:
            ServerError: 列出失败。
        """
        try:
            sdk_list = self._sdk.list_chats(page=page, page_size=page_size, **kwargs)
            return [Chat(id=chat.id, name=chat.name, client=self.client, sdk_obj=chat) for chat in sdk_list]
        except Exception as e:
            raise ServerError(f"Failed to list chats: {e}")

    def delete(self, ids: List[ID]):
        """
        批量删除对话助手。
        Args:
            ids (List[ID]): 对话助手 ID 列表。
        Raises:
            BadRequestError: 未提供对话助手 ID。
            ServerError: 删除失败。
        """
        if not ids:
            raise BadRequestError("No chat ids provided for deletion.")
        try:
            self._sdk.delete_chats(ids=ids)
        except Exception as e:
            raise ServerError(f"Failed to delete chats: {e}") 