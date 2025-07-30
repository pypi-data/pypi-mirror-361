from typing import List, Optional, Any
from .types import ID
from .exceptions import RagflowError, BadRequestError, NotFoundError, ServerError
from pydantic import BaseModel, PrivateAttr, Field, ValidationError

# 需要用户已安装 ragflow-sdk
try:
    from ragflow_sdk import RAGFlow
except ImportError:
    RAGFlow = None

class DatasetCreateParams(BaseModel):
    name: str = Field(..., min_length=1, description="数据集名称")

class DocumentUploadParams(BaseModel):
    file_path: str = Field(..., min_length=1, description="文件路径")

class ChunkAddParams(BaseModel):
    content: str = Field(..., min_length=1, description="块内容")

# Chunk ORM
class Chunk(BaseModel):
    """
    文档块对象，支持内容、标签、可用性等操作。
    """
    id: ID
    content: str
    important_keywords: Optional[list] = Field(default_factory=list)
    document: Optional['Document'] = Field(default=None, exclude=True)
    _sdk_obj: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, **data):
        sdk_obj = data.pop('sdk_obj', None)
        super().__init__(**data)
        self._sdk_obj = sdk_obj

    def update(self, update_message: dict):
        """
        更新 chunk 内容或配置。
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
            raise ServerError(f"Failed to update chunk: {e}")

# Chunk 管理器
class ChunkManager:
    """
    文档块管理器，支持增删查改。
    """
    def __init__(self, document: 'Document'):
        """
        Args:
            document (Document): 所属文档对象。
        """
        self.document = document
        self._sdk_obj = document._sdk_obj  # ragflow_sdk.Document 实例

    def list(self, keywords: Optional[str] = None, page: int = 1, page_size: int = 30) -> List[Chunk]:
        """
        列出 chunk 列表。
        Args:
            keywords (Optional[str]): 关键词过滤。
            page (int): 页码。
            page_size (int): 每页数量。
        Returns:
            List[Chunk]: 块对象列表。
        """
        if not self._sdk_obj:
            raise RagflowError("No document SDK object for list.")
        try:
            sdk_chunks = self._sdk_obj.list_chunks(keywords=keywords, page=page, page_size=page_size)
            return [Chunk(id=chunk.id, content=chunk.content, document=self.document, sdk_obj=chunk, important_keywords=getattr(chunk, 'important_keywords', [])) for chunk in sdk_chunks]
        except Exception as e:
            raise ServerError(f"Failed to list chunks: {e}")

    def add(self, content: str, important_keywords: Optional[List[str]] = None) -> Chunk:
        """
        添加 chunk。
        Args:
            content (str): 块内容。
            important_keywords (Optional[List[str]]): 关键词。
        Returns:
            Chunk: 新增块对象。
        """
        if not self._sdk_obj:
            raise RagflowError("No document SDK object for add.")
        try:
            params = ChunkAddParams(content=content)
            chunk = self._sdk_obj.add_chunk(content=content, important_keywords=important_keywords or [])
            return Chunk(id=chunk.id, content=chunk.content, document=self.document, sdk_obj=chunk, important_keywords=getattr(chunk, 'important_keywords', []))
        except Exception as e:
            raise ServerError(f"Failed to add chunk: {e}")

    def delete(self, chunk_ids: List[ID]):
        """
        删除 chunk。
        Args:
            chunk_ids (List[ID]): 待删除块 id 列表。
        Raises:
            ServerError: 删除失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No document SDK object for delete.")
        if not chunk_ids:
            raise BadRequestError("No chunk ids provided for deletion.")
        try:
            self._sdk_obj.delete_chunks(chunk_ids=chunk_ids)
        except Exception as e:
            raise ServerError(f"Failed to delete chunks: {e}")

    def get(self, *, id: str = None):
        """
        获取单个 chunk，通过 id。
        Returns:
            Chunk 或 None
        """
        chunks = self.list()
        if id:
            return next((c for c in chunks if c.id == id), None)
        return None

# Document ORM
class Document(BaseModel):
    """
    文档对象，支持内容、标签、可用性等操作。
    """
    id: ID
    name: str
    dataset: Optional['Dataset'] = Field(default=None, exclude=True)
    _sdk_obj: Optional[Any] = PrivateAttr(default=None)
    _chunks: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, **data):
        sdk_obj = data.pop('sdk_obj', None)
        dataset = data.get('dataset', None)
        super().__init__(**data)
        self._sdk_obj = sdk_obj
        self._chunks = ChunkManager(self)

    @property
    def chunks(self):
        """
        文档下的 chunk 管理器，支持 list、add、delete、get 等操作。
        Returns:
            ChunkManager: chunk 管理器实例。
        """
        return self._chunks

    def update(self, update_message: dict):
        """
        更新文档内容或配置。
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
            raise ServerError(f"Failed to update document: {e}")

    def download(self) -> bytes:
        """
        下载文档内容。
        Returns:
            bytes: 文档内容。
        Raises:
            RagflowError: 下载失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No underlying SDK object for download.")
        try:
            return self._sdk_obj.download()
        except Exception as e:
            raise ServerError(f"Failed to download document: {e}")

    def parse(self):
        """
        异步解析文档。
        Raises:
            RagflowError: 解析失败。
        """
        if not self.dataset or not self.dataset._sdk_obj:
            raise RagflowError("No dataset SDK object for parse operation.")
        try:
            self.dataset._sdk_obj.async_parse_documents([self.id])
        except Exception as e:
            raise ServerError(f"Failed to parse document: {e}")

    def delete(self):
        """
        删除文档。
        Raises:
            RagflowError: 删除失败。
        """
        if not self.dataset or not self.dataset._sdk_obj:
            raise RagflowError("No dataset SDK object for delete operation.")
        try:
            self.dataset._sdk_obj.delete_documents(ids=[self.id])
        except Exception as e:
            raise ServerError(f"Failed to delete document: {e}")

# Document 管理器
class DocumentManager:
    """
    文档管理器，支持增删查改。
    """
    def __init__(self, dataset: 'Dataset'):
        """
        Args:
            dataset (Dataset): 所属数据集对象。
        """
        self.dataset = dataset
        self._sdk_obj = dataset._sdk_obj  # ragflow_sdk.DataSet 实例

    def upload(self, file_path: Optional[str] = None, display_name: Optional[str] = None) -> Document:
        if not self._sdk_obj:
            raise RagflowError("No dataset SDK object for upload.")
        try:
            doc_dict = {}
            if display_name:
                doc_dict["display_name"] = display_name
            if file_path:
                with open(file_path, "rb") as f:
                    doc_dict["blob"] = f.read()
            else:
                # 没有 file_path 时，blob 传空字节串
                doc_dict["blob"] = b""
            self._sdk_obj.upload_documents([doc_dict])
            # 获取最新文档
            docs = self.list(keywords=display_name or file_path, page=1, page_size=1)
            if not docs:
                raise NotFoundError("Uploaded document not found in dataset.")
            return docs[0]
        except Exception as e:
            raise ServerError(f"Failed to upload document: {e}")

    def list(self, keywords: Optional[str] = None, page: int = 1, page_size: int = 30) -> List[Document]:
        """
        列出文档列表。
        Args:
            keywords (Optional[str]): 关键词过滤。
            page (int): 页码。
            page_size (int): 每页数量。
        Returns:
            List[Document]: 文档对象列表。
        Raises:
            ServerError: 列出失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No dataset SDK object for list.")
        try:
            sdk_docs = self._sdk_obj.list_documents(keywords=keywords, page=page, page_size=page_size)
            return [Document(id=doc.id, name=doc.name, dataset=self.dataset, sdk_obj=doc) for doc in sdk_docs]
        except Exception as e:
            raise ServerError(f"Failed to list documents: {e}")

    def delete(self, ids: List[ID]):
        """
        删除文档。
        Args:
            ids (List[ID]): 待删除文档 id 列表。
        Raises:
            ServerError: 删除失败。
        """
        if not self._sdk_obj:
            raise RagflowError("No dataset SDK object for delete.")
        if not ids:
            raise BadRequestError("No document ids provided for deletion.")
        try:
            self._sdk_obj.delete_documents(ids=ids)
        except Exception as e:
            raise ServerError(f"Failed to delete documents: {e}")

    def get(self, *, id: str = None, name: str = None):
        """
        获取单个文档，可通过 id 或 name。
        Returns:
            Document 或 None
        """
        docs = self.list()
        if id:
            return next((d for d in docs if d.id == id), None)
        if name:
            return next((d for d in docs if d.name == name), None)
        return None

class RetrieveParams(BaseModel):
    question: str = Field(..., description="用户查询或关键词")
    dataset_ids: Optional[List[str]] = None
    document_ids: Optional[List[str]] = None
    page: int = 1
    page_size: int = 30
    similarity_threshold: float = 0.2
    vector_similarity_weight: float = 0.3
    top_k: int = 1024
    rerank_id: Optional[str] = None
    keyword: bool = False
    highlight: bool = False

# Dataset ORM
class Dataset(BaseModel):
    """
    数据集对象，支持内容、标签、可用性等操作。
    """
    id: ID
    name: str
    _client: Optional[Any] = PrivateAttr(default=None)
    _sdk_obj: Optional[Any] = PrivateAttr(default=None)
    _documents: Optional[Any] = PrivateAttr(default=None)

    def __init__(self, **data):
        sdk_obj = data.pop('sdk_obj', None)
        client = data.pop('client', None)
        super().__init__(**data)
        self._sdk_obj = sdk_obj
        self._client = client
        self._documents = DocumentManager(self)

    @property
    def documents(self):
        """
        数据集下的文档管理器，支持 list、upload、delete 等操作。
        Returns:
            DocumentManager: 文档管理器实例。
        """
        return self._documents

    def update(self, update_message: dict):
        """
        更新数据集内容或配置。
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
            raise ServerError(f"Failed to update dataset: {e}")

    def delete(self):
        """
        删除数据集。
        Raises:
            RagflowError: 删除失败。
        """
        if not self._client:
            raise RagflowError("No client for delete operation.")
        try:
            self._client.datasets.delete([self.id])
        except Exception as e:
            raise ServerError(f"Failed to delete dataset: {e}")

    def retrieve(self, params: 'RetrieveParams') -> List[Any]:
        """
        检索数据集内容，支持所有 ragflow-sdk 检索参数。
        Args:
            params (RetrieveParams): 检索参数模型。
        Returns:
            List[Any]: 检索到的 chunk 或文档块对象列表。
        Raises:
            RagflowError: 检索失败。
        """
        if not self._client or not hasattr(self._client, '_sdk'):
            raise RagflowError("No SDK client for retrieve operation.")
        try:
            return self._client._sdk.retrieve(
                question=params.question,
                dataset_ids=[self.id],
                document_ids=params.document_ids,
                page=params.page,
                page_size=params.page_size,
                similarity_threshold=params.similarity_threshold,
                vector_similarity_weight=params.vector_similarity_weight,
                top_k=params.top_k,
                rerank_id=params.rerank_id,
                keyword=params.keyword,
                highlight=params.highlight
            )
        except Exception as e:
            raise ServerError(f"Failed to retrieve: {e}")

# Dataset 管理器
class DatasetManager:
    """
    数据集管理器，支持增删查改。
    """
    def __init__(self, client):
        """
        Args:
            client: 客户端对象。
        """
        self.client = client
        # 初始化 ragflow_sdk.RAGFlow 实例
        if RAGFlow is None:
            raise ImportError("ragflow-sdk is required. Please install it via 'pip install ragflow-sdk'.")
        self._sdk = RAGFlow(api_key=client.api_key, base_url=client.base_url)
        # 便于 Dataset/Document 访问
        client._sdk = self._sdk

    def create(self, name: str, **kwargs) -> Dataset:
        """
        创建数据集。
        Args:
            name (str): 数据集名称。
            **kwargs: 其他参数。
        Returns:
            Dataset: 创建的数据集对象。
        Raises:
            BadRequestError: 数据集名称缺失。
            ServerError: 创建失败。
        """
        try:
            params = DatasetCreateParams(name=name)
        except ValidationError as e:
            raise BadRequestError(str(e))
        if not name:
            raise BadRequestError("Dataset name is required.")
        try:
            sdk_obj = self._sdk.create_dataset(name=name, **kwargs)
            return Dataset(id=sdk_obj.id, name=sdk_obj.name, client=self.client, sdk_obj=sdk_obj)
        except Exception as e:
            raise ServerError(f"Failed to create dataset: {e}")

    def list(self, page: int = 1, page_size: int = 30, **kwargs) -> List[Dataset]:
        """
        列出数据集列表。
        Args:
            page (int): 页码。
            page_size (int): 每页数量。
            **kwargs: 其他参数。
        Returns:
            List[Dataset]: 数据集对象列表。
        Raises:
            ServerError: 列出失败。
        """
        try:
            sdk_list = self._sdk.list_datasets(page=page, page_size=page_size, **kwargs)
            return [Dataset(id=ds.id, name=ds.name, client=self.client, sdk_obj=ds) for ds in sdk_list]
        except Exception as e:
            raise ServerError(f"Failed to list datasets: {e}")

    def delete(self, ids: List[ID]):
        """
        删除数据集。
        Args:
            ids (List[ID]): 待删除数据集 id 列表。
        Raises:
            BadRequestError: 未提供数据集 id。
            ServerError: 删除失败。
        """
        if not ids:
            raise BadRequestError("No dataset ids provided for deletion.")
        try:
            self._sdk.delete_datasets(ids=ids)
        except Exception as e:
            raise ServerError(f"Failed to delete datasets: {e}")

    def get(self, *, id: str = None, name: str = None):
        """
        获取单个数据集，可通过 id 或 name。
        Returns:
            Dataset 或 None
        """
        datasets = self.list()
        if id:
            return next((d for d in datasets if d.id == id), None)
        if name:
            return next((d for d in datasets if d.name == name), None)
        return None 