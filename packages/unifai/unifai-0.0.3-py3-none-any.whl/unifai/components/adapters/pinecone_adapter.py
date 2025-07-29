from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from json import loads as json_loads, JSONDecodeError

if TYPE_CHECKING:
    from pinecone.grpc import PineconeGRPC
from pinecone.exceptions import PineconeException, PineconeApiException

from ...exceptions import UnifAIError, UnknownUnifAIError, STATUS_CODE_TO_EXCEPTION_MAP, UnknownAPIError, CollectionNotFoundError
from .._base_components.__base_component import UnifAIComponent
from .._base_components._base_adapter import UnifAIAdapter

class PineconeExceptionConverter(UnifAIComponent):
    provider = "pinecone"
    
    def _convert_exception(self, exception: PineconeException) -> UnifAIError:
        if not isinstance(exception, PineconeApiException):
            return UnknownUnifAIError(
                message=str(exception),
                original_exception=exception
            )
        status_code=exception.status
        if status_code is not None:
            unifai_exception_type = STATUS_CODE_TO_EXCEPTION_MAP.get(status_code, UnknownAPIError)
        else:
            unifai_exception_type = UnknownAPIError
                    
        error_code = None
        if body := getattr(exception, "body", None):
            message = body
            try:
                decoded_body = json_loads(body)
                error = decoded_body["error"]
                message = error.get("message") or body
                error_code = error.get("code")
            except (JSONDecodeError, KeyError, AttributeError):
                pass # Use the original body if it can't be decoded
        else:
            message = str(exception) # Use the original exception message if there is no body
        
        if status_code == 404 and "Resource" in message and "not found" in message:
            unifai_exception_type = CollectionNotFoundError

        return unifai_exception_type(
            message=message,
            error_code=error_code,
            status_code=status_code,
            original_exception=exception,
        )   


class PineconeAdapter(UnifAIAdapter, PineconeExceptionConverter):
    client: PineconeGRPC
    default_embedding_provider = "pinecone"

    def import_client(self) -> Callable:
        from pinecone.grpc import PineconeGRPC
        return PineconeGRPC

