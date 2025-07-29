from typing import TYPE_CHECKING, ParamSpec, cast, Concatenate, Any, Callable, Collection, Literal, Optional, Sequence, Type, Union, Self, Iterable, Mapping, Generator, NoReturn, Generic, TypeVar

if TYPE_CHECKING:
    from ...types.annotations import ComponentName, ModelName, ProviderName

from .._base_components._base_document_chunker import DocumentChunker
from .._base_components._base_document_db import DocumentDB, DocumentDBCollection
from .._base_components._base_document_loader import DocumentLoader
from .._base_components._base_embedder import Embedder
from .._base_components._base_vector_db import VectorDB, VectorDBCollection
from .._base_components._base_reranker import Reranker
from .._base_components._base_tokenizer import Tokenizer
from ._base_prompt_template import PromptModel

from ...configs.rag_config import RAGConfig
from ...configs.document_chunker_config import DocumentChunkerConfig
from ...configs.document_db_config import DocumentDBConfig, DocumentDBCollectionConfig
from ...configs.document_loader_config import DocumentLoaderConfig, LoaderInputP
from ...configs.embedder_config import EmbedderConfig
from ...configs.reranker_config import RerankerConfig
from ...configs.tokenizer_config import TokenizerConfig
from ...configs.vector_db_config import VectorDBConfig, VectorDBCollectionConfig

from ...types import Document, Documents, ResponseInfo, QueryResult
from ...types.annotations import InputP as QueryInputP, NewInputP


from ...utils import chunk_iterable, combine_dicts, copy_paramspec_from

from .__base_component import UnifAIComponent

RAGConfigT = TypeVar('RAGConfigT', bound=RAGConfig)
# QueryInputP = ParamSpec('QueryInputP')

class BaseRAGPipe(UnifAIComponent[RAGConfigT], Generic[RAGConfigT, LoaderInputP, QueryInputP]):
    component_type = "ragpipe"
    provider = "base"

    can_get_components = True

    def _setup(self) -> None:
        super()._setup()
        self._document_loader: Callable[LoaderInputP, Documents | Iterable[Document] | Generator[Document, None, ResponseInfo | None]] | None = self.init_kwargs.get("document_loader")
        self._document_chunker = self.init_kwargs.get("document_chunker")
        self._vector_db = self.init_kwargs.get("vector_db")
        self._vector_db_collection = self.init_kwargs.get("vector_db_collection")
        self._reranker = self.init_kwargs.get("reranker")
        self._tokenizer = self.init_kwargs.get("tokenizer")
        self._extra_kwargs = self.config.extra_kwargs or {}
        self.response_infos: list[ResponseInfo] = []
        # Set the query_modifier and prompt_template functions        
        self._set_query_modifier(self.config.query_modifier)
        self._set_prompt_template(self.config.prompt_template)

    @property
    def document_loader(self) -> Callable[LoaderInputP, Documents | Iterable[Document] | Generator[Document, None, ResponseInfo | None]]:
        if self._document_loader is not None:
            return self._document_loader        
        if not (_document_loader := self.config.document_loader):
            raise ValueError("document_loader is required. Set document_loader in the config or provide an instance at runtime.")
        self._set_document_loader(_document_loader)
        return self._document_loader 
    
    @document_loader.setter
    def document_loader(self, document_loader: "DocumentLoader[NewInputP] | DocumentLoaderConfig[NewInputP] | ProviderName | tuple[ProviderName, ComponentName] | Callable[NewInputP, Documents | Iterable[Document] | Generator[Document, None, ResponseInfo | None]]") -> None:
        self._set_document_loader(document_loader)

    def _set_document_loader(self, document_loader: "DocumentLoader[NewInputP] | DocumentLoaderConfig[NewInputP] | ProviderName | tuple[ProviderName, ComponentName] | Callable[NewInputP, Documents | Iterable[Document] | Generator[Document, None, ResponseInfo | None]]") -> None:
        if callable(document_loader):
            self._document_loader = document_loader
        else:
            self._document_loader = self._get_component("document_loader", document_loader).iload_documents

    def set_document_loader(self, document_loader: Callable[NewInputP, Documents | Iterable[Document] | Generator[Document, None, ResponseInfo | None]]):
        self._set_document_loader(document_loader)
        return cast("BaseRAGPipe[RAGConfig[NewInputP, QueryInputP], NewInputP, QueryInputP]", self)

    @property
    def document_chunker(self) -> DocumentChunker:
        if self._document_chunker is not None:
            return self._document_chunker        
        if not self.config.document_chunker:
            raise ValueError("document_chunker is required. Set document_chunker in the config or provide an instance at runtime.")
        self._document_chunker = self._get_component("document_chunker", self.config.document_chunker)
        return self._document_chunker
    
    @document_chunker.setter
    def document_chunker(self, value: "Optional[DocumentChunker | DocumentChunkerConfig | ProviderName | tuple[ProviderName, ComponentName]]") -> None:
        if value is None or isinstance(value, DocumentChunker):
            self._document_chunker = value
        else:
            self._document_chunker = self._get_component("document_chunker", value)
    
    @property
    def vector_db(self) -> VectorDB:
        if self._vector_db is not None:
            return self._vector_db        
        if not self.config.vector_db:
            raise ValueError("vector_db is required. Set vector_db in the config or provide an instance at runtime.")
        if isinstance(self.config.vector_db, VectorDBCollectionConfig):
            self._vector_db = self._get_component("vector_db", self.config.vector_db.provider)
        else:       
            self._vector_db = self._get_component("vector_db", self.config.vector_db)
        return self._vector_db

    @property
    def vector_db_collection(self) -> VectorDBCollection:
        if self._vector_db_collection is not None:
            return self._vector_db_collection        
        if not self.config.vector_db:
            raise ValueError("vector_db is required. Set vector_db in the config or provide an instance at runtime.")
        if isinstance(self.config.vector_db, VectorDBCollectionConfig):
            self._vector_db_collection = self.vector_db.get_or_create_collection_from_config(self.config.vector_db)
        else:
            self._vector_db_collection = self.vector_db.get_or_create_collection()
        return self._vector_db_collection

    @vector_db_collection.setter
    def vector_db_collection(self, value: "Optional[VectorDBCollection | VectorDBCollectionConfig | ProviderName | tuple[ProviderName, ComponentName]]") -> None:
        if value is None or isinstance(value, VectorDBCollection):
            self._vector_db_collection = value
        else:
            self._vector_db_collection = self._get_component("vector_db", value)
    
    @property
    def reranker(self) -> Optional[Reranker]:
        if self._reranker is not None:
            return self._reranker
        if self.config.reranker:
            self._reranker = self._get_component("reranker", self.config.reranker)
        return self._reranker
    
    @reranker.setter
    def reranker(self, value: "Optional[Reranker | RerankerConfig | ProviderName | tuple[ProviderName, ComponentName]]") -> None:
        if value is None or isinstance(value, Reranker):
            self._reranker = value
        else:
            self._reranker = self._get_component("reranker", value)    
    
    @property
    def tokenizer(self) -> Tokenizer:
        if self._tokenizer is not None:
            return self._tokenizer        
        if not self.config.tokenizer:
            raise ValueError("tokenizer is required. Set tokenizer in the config or provide an instance at runtime.")
        return self._get_component("tokenizer", self.config.tokenizer)
    
    @tokenizer.setter
    def tokenizer(self, value: "Optional[Tokenizer | TokenizerConfig | ProviderName | tuple[ProviderName, ComponentName]]") -> None:
        if value is None or isinstance(value, Tokenizer):
            self._tokenizer = value
        else:
            self._tokenizer = self._get_component("tokenizer", value)
        
    def iupsert_documents(
            self,
            documents: Iterable[Document],
            *,
            embedder: Optional[Embedder] = None,
            vector_db_collection: Optional[VectorDBCollection] = None,
            embed_kwargs: Optional[dict[str, Any]] = None,            
            upsert_kwargs: Optional[dict[str, Any]] = None,
            batch_size: Optional[int] = None,
            ) -> Generator[Document, None, ResponseInfo]:
        
        vector_db_collection = vector_db_collection or self.vector_db_collection
        embedder = embedder or vector_db_collection.embedder
        embed_kwargs = combine_dicts(
            vector_db_collection.config.extra_kwargs["embed"] if vector_db_collection.config.extra_kwargs else None, 
            self._extra_kwargs.get("embed"), 
            embed_kwargs
        )
        if "task_type" not in embed_kwargs:
            embed_kwargs["task_type"] = self.vector_db_collection.config.embed_document_task_type
        
        upsert_kwargs = combine_dicts(
            vector_db_collection.config.extra_kwargs["upsert"] if vector_db_collection.config.extra_kwargs else None, 
            self._extra_kwargs.get("upsert"), 
            upsert_kwargs
        )
                    
        response_info = ResponseInfo()
        for batch in chunk_iterable(documents, batch_size):
            embedded_documents = embedder.embed_documents(batch, **embed_kwargs)
            vector_db_collection.upsert_documents(embedded_documents, **upsert_kwargs)
            response_info += embedded_documents.response_info
            yield from batch
        return response_info

    def ingest_documents(
            self,
            documents: Iterable[Document],
            *,
            document_chunker: Optional[DocumentChunker] = None,
            embedder: Optional[Embedder] = None,
            vector_db_collection: Optional[VectorDBCollection] = None,
            chunk_kwargs: Optional[dict[str, Any]] = None,
            embed_kwargs: Optional[dict[str, Any]] = None,
            upsert_kwargs: Optional[dict[str, Any]] = None,
            batch_size: Optional[int] = None,
        ) -> Generator[Document, None, ResponseInfo]:

        document_chunker = document_chunker or self.document_chunker
        
        chunk_kwargs = combine_dicts(
            document_chunker.config.extra_kwargs["chunk_documents"] if document_chunker.config.extra_kwargs else None, 
            self._extra_kwargs.get("chunk"), 
            chunk_kwargs
        )       
        embedder = embedder or self.vector_db_collection.embedder
        if "chunk_size" not in chunk_kwargs:
            chunk_kwargs["chunk_size"] = embedder.get_model_max_tokens(self.vector_db_collection.embedding_model)

        documents = document_chunker.ichunk_documents(documents, **chunk_kwargs)
        return self.iupsert_documents(
            documents,
            embedder=embedder,
            vector_db_collection=vector_db_collection,
            embed_kwargs=embed_kwargs,
            upsert_kwargs=upsert_kwargs,
            batch_size=batch_size,
        )
    
    def ingest_all_documents(
            self,
            documents: Iterable[Document],
            *,
            document_chunker: Optional[DocumentChunker] = None,
            embedder: Optional[Embedder] = None,
            vector_db_collection: Optional[VectorDBCollection] = None,
            chunk_kwargs: Optional[dict[str, Any]] = None,
            embed_kwargs: Optional[dict[str, Any]] = None,
            upsert_kwargs: Optional[dict[str, Any]] = None,
            batch_size: Optional[int] = None,
        ) -> Documents:      
        return Documents.from_generator(self.ingest_documents(
            documents,
            document_chunker=document_chunker,
            embedder=embedder,
            vector_db_collection=vector_db_collection,
            chunk_kwargs=chunk_kwargs,
            embed_kwargs=embed_kwargs,
            upsert_kwargs=upsert_kwargs,
            batch_size=batch_size,
        ))
                    
    def ingest(
            self,
            document_chunker: Optional[DocumentChunker] = None,
            embedder: Optional[Embedder] = None,
            vector_db_collection: Optional[VectorDBCollection] = None,
            load_kwargs: Optional[dict[str, Any]] = None,
            chunk_kwargs: Optional[dict[str, Any]] = None,
            embed_kwargs: Optional[dict[str, Any]] = None,
            upsert_kwargs: Optional[dict[str, Any]] = None,
            batch_size: Optional[int] = None,
            *args: LoaderInputP.args,            
            **kwargs: LoaderInputP.kwargs
    ) -> Generator[Document, None, ResponseInfo]:
        
        if isinstance(_document_loader := self.document_loader, DocumentLoader) and (_loader_extra_kwargs := _document_loader.config.extra_kwargs) :
            _loader_load_extra_kwargs = _loader_extra_kwargs.get("load_documents")
        else:
            _loader_load_extra_kwargs = None            

        _load_kwargs = combine_dicts(
            _loader_load_extra_kwargs,
            self._extra_kwargs.get("load"), 
            load_kwargs,
            kwargs
        )
        documents = _document_loader(*args, **_load_kwargs)
        return self.ingest_documents(
            documents,
            document_chunker=document_chunker,
            embedder=embedder,
            vector_db_collection=vector_db_collection,
            chunk_kwargs=chunk_kwargs,
            embed_kwargs=embed_kwargs,
            upsert_kwargs=upsert_kwargs,
            batch_size=batch_size,
        )
    
    def ingest_all(
            self,
            document_chunker: Optional[DocumentChunker] = None,
            embedder: Optional[Embedder] = None,
            vector_db_collection: Optional[VectorDBCollection] = None,
            load_kwargs: Optional[dict[str, Any]] = None,
            chunk_kwargs: Optional[dict[str, Any]] = None,
            embed_kwargs: Optional[dict[str, Any]] = None,
            upsert_kwargs: Optional[dict[str, Any]] = None,
            batch_size: Optional[int] = None,
            *args: LoaderInputP.args,
            **kwargs: LoaderInputP.kwargs
    ) -> Documents:
        return Documents.from_generator(self.ingest(
            document_chunker,
            embedder,
            vector_db_collection,
            load_kwargs,
            chunk_kwargs,
            embed_kwargs,
            upsert_kwargs,
            batch_size,
            *args,
            **kwargs
        ))
    

    @property
    def query_modifier(self) -> Callable[QueryInputP, str|Callable[..., str]]:
        return self._query_modifier
    
    @query_modifier.setter
    def query_modifier(self, query_modifier: Callable[QueryInputP, str|Callable[..., str]]) -> None:
        self._set_query_modifier(query_modifier)
    
    def _set_query_modifier(self, query_modifier: Callable[NewInputP, str|Callable[..., str]]) -> None:
        self._query_modifier = query_modifier

    def set_query_modifier(self, query_modifier: Callable[NewInputP, str|Callable[..., str]]):
        self._set_query_modifier(query_modifier)
        return cast("BaseRAGPipe[RAGConfig[LoaderInputP, NewInputP], LoaderInputP, NewInputP]", self)
    
    def with_query_modifier(self, query_modifier: Callable[NewInputP, str|Callable[..., str]]):
        return self.with_config().set_query_modifier(query_modifier)
    
    @property
    def prompt_template(self) -> Callable[Concatenate[QueryResult, QueryInputP], str|Callable[..., str]]:
        return self._prompt_template
    
    @prompt_template.setter
    def prompt_template(self, prompt_template: Callable[Concatenate[QueryResult, QueryInputP], str|Callable[..., str]]) -> None:
        self._set_prompt_template(prompt_template)

    def _set_prompt_template(self, prompt_template: Callable[Concatenate[QueryResult, NewInputP], str|Callable[..., str]]) -> None:
        self._prompt_template = prompt_template

    def set_prompt_template(self, prompt_template: Callable[Concatenate[QueryResult, NewInputP], str|Callable[..., str]]):
        self._set_prompt_template(prompt_template)
        return cast("BaseRAGPipe[RAGConfig[LoaderInputP, NewInputP], LoaderInputP, NewInputP]", self)
    
    def with_prompt_template(self, prompt_template: Callable[Concatenate[QueryResult, NewInputP], str|Callable[..., str]]):
        return self.with_config().set_prompt_template(prompt_template)
    
    def set_query_modifier_and_prompt_template(
            self,
            query_modifier: Callable[NewInputP, str|Callable[..., str]],
            prompt_template: Callable[Concatenate[QueryResult, NewInputP], str|Callable[..., str]],
            ):
        self._set_query_modifier(query_modifier)
        return self.set_prompt_template(prompt_template)
    
    def with_query_modifier_and_prompt_template(
            self,
            query_modifier: Callable[NewInputP, str|Callable[..., str]],
            prompt_template: Callable[Concatenate[QueryResult, NewInputP], str|Callable[..., str]],
            ):
        return self.with_query_modifier(query_modifier).with_prompt_template(prompt_template)

    def query(
            self, 
            top_k: Optional[int] = None,
            top_n: Optional[int] = None,
            where: Optional[dict] = None,
            where_document: Optional[dict] = None, 
            max_distance: Optional[float] = None,
            min_similarity: Optional[float] = None,                    
            query_kwargs: Optional[dict] = None,
            reranker_model: Optional["ModelName"] = None,          
            rerank_kwargs: Optional[dict] = None,
            *args: QueryInputP.args,
            **kwargs: QueryInputP.kwargs
            ) -> QueryResult:
        
        top_k = top_k or self.config.top_k
        top_n = top_n or self.config.top_n
        where = where or self.config.where
        where_document = where_document or self.config.where_document
        max_distance = max_distance or self.config.max_distance
        min_similarity = min_similarity or self.config.min_similarity

        query_input = self.query_modifier(*args, **kwargs)
        if callable(query_input):
            query_input = query_input(*args, **kwargs)
        query_kwargs = combine_dicts(self._extra_kwargs.get("query"), query_kwargs)
        query_result = self.vector_db_collection.query(query_input, top_k, where, where_document, **query_kwargs)
        
        if max_distance is not None:
            # TODO: maybe move to VectorDBCollection
            query_result.trim_by_distance(max_distance)

        # If a reranker is configured and there are results rerank them
        if self.reranker and query_result.ids:
            reranker_model = reranker_model or self.config.reranker_model
            rerank_kwargs = combine_dicts(self._extra_kwargs.get("rerank"), rerank_kwargs)
            query_result = self.reranker.rerank(
                query=query_input,
                query_result=query_result,
                top_n=top_n,
                model=reranker_model,
                **rerank_kwargs
            )
            if min_similarity is not None:
                query_result.trim_by_similarity_score(min_similarity)

        return query_result

    def construct_rag_prompt(
            self,
            query_result: QueryResult,
            *args: QueryInputP.args,
            **kwargs: QueryInputP.kwargs
            ) -> str:        
        kwargs["query"] = query_result.query # Add modified query to kwargs
        prompt = self.prompt_template(query_result, *args, **kwargs)
        if callable(prompt):
            prompt = prompt(query_result, *args, **kwargs)
        return prompt

    def prompt(
            self, 
            top_k: Optional[int] = None,
            top_n: Optional[int] = None,
            where: Optional[dict] = None,
            where_document: Optional[dict] = None,
            max_distance: Optional[float] = None,
            min_similarity: Optional[float] = None,            
            query_kwargs: Optional[dict] = None,
            reranker_model: Optional[str] = None,
            rerank_kwargs: Optional[dict] = None,
            *args: QueryInputP.args,
            **kwargs: QueryInputP.kwargs
            ) -> str:

        query_result = self.query(top_k, top_n, where, where_document, max_distance, min_similarity, query_kwargs, reranker_model, rerank_kwargs, *args, **kwargs)
        return self.construct_rag_prompt(query_result, *args, **kwargs)
    
    @copy_paramspec_from(prompt)
    def __call__(self, *args, **kwargs):
        return self.prompt(*args, **kwargs)