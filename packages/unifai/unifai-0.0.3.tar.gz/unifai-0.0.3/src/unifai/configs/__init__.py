from ._base_configs import ProviderConfig
from .document_chunker_config import DocumentChunkerConfig
from .document_db_config import DocumentDBConfig, DocumentDBCollectionConfig
from .document_loader_config import DocumentLoaderConfig, FileIODocumentLoaderConfig
from .embedder_config import EmbedderConfig
from .llm_config import LLMConfig
from .input_parser_config import InputParserConfig
from .output_parser_config import OutputParserConfig
from .reranker_config import RerankerConfig
from .tokenizer_config import TokenizerConfig
from .tool_caller_config import ToolCallerConfig
from .vector_db_config import VectorDBConfig, VectorDBCollectionConfig

# High level configs must be imported last to avoid circular imports
from .chat_config import ChatConfig
from .rag_config import RAGConfig
from .function_config import FunctionConfig
from .unifai_config import UnifAIConfig

COMPONENT_CONFIGS = {
    "document_chunker": DocumentChunkerConfig,
    "document_db": DocumentDBConfig,
    "document_db_collection": DocumentDBCollectionConfig,
    "document_loader": FileIODocumentLoaderConfig,
    "embedder": EmbedderConfig,
    "llm": LLMConfig,
    "input_parser": InputParserConfig,
    "output_parser": OutputParserConfig,
    "reranker": RerankerConfig,
    "tokenizer": TokenizerConfig,
    "tool_caller": ToolCallerConfig,
    "vector_db": VectorDBConfig,
    "vector_db_collection": VectorDBCollectionConfig,
    "ragpipe": RAGConfig,
    "chat": ChatConfig,
    "function": FunctionConfig,
}