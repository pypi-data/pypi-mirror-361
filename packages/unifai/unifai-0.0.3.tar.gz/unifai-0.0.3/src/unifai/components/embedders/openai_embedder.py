
from typing import Optional, Union, Any, Literal, Mapping, Iterator, Sequence, Generator

from openai.types.create_embedding_response import CreateEmbeddingResponse

from ...types import Embeddings, ResponseInfo, Usage
from ..adapters.openai_adapter import OpenAIAdapter
from .._base_components._base_embedder import Embedder

class OpenAIEmbedder(OpenAIAdapter, Embedder):
    provider = "openai"
    default_embedding_model = "text-embedding-3-large"
    model_embedding_dimensions = {
        "text-embedding-3-large": 3072,
        "text-embedding-3-small": 1536,
        "text-embedding-ada-002": 1536,
    }
    model_max_tokens = {
        "text-embedding-3-large": 8191,
        "text-embedding-3-small": 8191,
        "text-embedding-ada-002": 8191,
    }

    # Embeddings
    def _get_embed_response(
            self,
            input: list[str],
            model: str,
            dimensions: Optional[int] = None,
            task_type: Literal["search_query", "search_document", "classification", "clustering", "image"] = "search_query",
            truncate: Literal[False, "end", "start"] = False,                  
            **kwargs
            ) -> CreateEmbeddingResponse:
        
        if dimensions is not None:
            kwargs["dimensions"] = dimensions
        return self.client.embeddings.create(input=input, model=model, **kwargs)


    def _extract_embeddings(
            self,            
            response: CreateEmbeddingResponse,
            **kwargs
            ) -> Embeddings:
        return Embeddings(
            root=[embedding.embedding for embedding in response.data],
            response_info=ResponseInfo(
                model=response.model, 
                usage=Usage(
                    input_tokens=response.usage.prompt_tokens, 
                    output_tokens=0
                )
            )
        )

 