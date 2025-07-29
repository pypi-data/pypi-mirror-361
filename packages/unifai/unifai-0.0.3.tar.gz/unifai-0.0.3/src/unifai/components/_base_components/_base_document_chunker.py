from typing import Optional, List, Union, Literal, Iterable, Iterator, Any, Callable
from typing import Type, Optional, Sequence, Any, Union, Literal, TypeVar, ClassVar, Collection, Callable, Iterator, Iterable, Generator, Self, Dict

from ...utils import clean_text, combine_dicts, copy_paramspec_from
from ...types import Document
from ...types.annotations import ComponentName, ModelName, ProviderName, CollectionName

from ._base_adapter import UnifAIAdapter
from .__base_component import UnifAIComponent
from ._base_tokenizer import Tokenizer
from ..tokenizers.tiktoken_tokenizer import TikTokenTokenizer
from ...configs.document_chunker_config import DocumentChunkerConfig
from ...configs.tokenizer_config import TokenizerConfig

import re
from itertools import chain, zip_longest, islice
from copy import deepcopy
from functools import partial

T = TypeVar("T")

class DocumentChunker(UnifAIComponent[DocumentChunkerConfig]):
    component_type = "document_chunker"
    provider = "base"
    config_class = DocumentChunkerConfig
    can_get_components = True

    """
    A document chunker that chunks text based on character separators.
    Supports both single and multiple separators with recursive splitting.
        
        Args:
            chunk_size: Maximum size of each chunk in tokens (as measured by the tokenizer)
            chunk_overlap: Number of tokens to overlap between chunks. Can be an int (number of tokens) or a float (percentage of chunk size)
            tokenizer: Tokenizer to use for tokenizing text. Can be an instance of Tokenizer, a subclass of Tokenizer, or a callable that returns the size of a tokenized text
            tokenizer_model: Model to use for the tokenizer
            tokenizer_kwargs: Additional keyword arguments to pass to the tokenizer
            separators: List of character separators to split text on. Default is ["\\n\\n", "\\n", ""]
            keep_separator: Whether and where to keep separators. Options are "start", "end", or False
            regex: Whether to treat separators as regular expressions. Default is False
            strip_chars: Argument to pass to str.strip() to strip characters from the start and end of chunks. Default is " \n\t"
            deepcopy_metadata: Whether to deepcopy metadata for each chunk. Default is True
            add_to_metadata: List of metadata fields to add to each chunk. Options are "source", "chunk_size", "start_index", and "end_index"
            default_base_id: Base ID to use for documents when no ID is provided. Default is "doc"
            **kwargs: Additional keyword arguments for subclasses of DocumentChunker
        """

    def _setup(self) -> None:
        super()._setup()
        self._tokenizer = None
        self._size_function = len
        self.size_function_kwargs = self.config.extra_kwargs.get("size_function", {}) if self.config.extra_kwargs else {}

        self.tokenizer = self.config.tokenizer
        self.size_function = self.config.size_function
        
        self.chunk_size = self.config.chunk_size
        if isinstance((config_chunk_overlap := self.config.chunk_overlap), int):
            self.chunk_overlap = config_chunk_overlap
        else:
            self.chunk_overlap = self.get_overlap_from_percentage(self.chunk_size, config_chunk_overlap)
        self.separators = self.config.separators
        if not self.separators:
            self.separators.append("")   
        self.keep_separator = self.config.keep_separator     
        self.regex = self.config.regex        

        self.strip_chars = self.config.strip_chars
        self.deepcopy_metadata = self.config.deepcopy_metadata
        self.add_to_metadata = self.config.add_to_metadata
        self.default_base_id = self.config.default_base_id
                
    def _set_tokenizer(self, tokenizer: Optional["Tokenizer | TokenizerConfig | ProviderName | tuple[ProviderName, ComponentName]"]) -> Optional[Tokenizer]:
        update_size_function = self._tokenizer and self.size_function is self._tokenizer.count_tokens
        if tokenizer is None or isinstance(tokenizer, Tokenizer):
            self._tokenizer = tokenizer        
        else:
            self._tokenizer = self._get_component("tokenizer", tokenizer)
        
        if self._tokenizer:
            self.size_function_kwargs["model"] = self.config.tokenizer_model
            if update_size_function:
                self.size_function = self._tokenizer.count_tokens
        else:
            self.size_function_kwargs.pop("model", None)

    @property
    def tokenizer(self) -> Optional[Tokenizer]:
        if self._tokenizer is None and self.config.tokenizer:
            self._set_tokenizer(self.config.tokenizer)
        return self._tokenizer
    
    @tokenizer.setter
    def tokenizer(self, tokenizer: Optional["Tokenizer | TokenizerConfig | ProviderName | tuple[ProviderName, ComponentName]"]) -> None:
        self._set_tokenizer(tokenizer)

    def _set_size_function(self, size_function: Callable[..., int] | Literal["tokens", "characters", "words"]) -> None:
        if size_function == "tokens":
            if not self.tokenizer:
                raise ValueError("Tokenizer must be set to use 'tokens' as size function")
            self._size_function = self.tokenizer.count_tokens
        elif size_function == "characters":
            self._size_function = lambda text, **kwargs: len(text)
        elif size_function == "words":
            self._size_function = lambda text, **kwargs: len(text.split())
        elif callable(size_function):
            self._size_function = size_function
        else:
            raise ValueError("Invalid size function: must be 'tokens', 'characters', 'words', or a callable that takes a string and returns an int")

    @property
    def size_function(self) -> Callable[..., int]:
        if self._size_function is None and self.config.size_function:
            self._set_size_function(self.config.size_function)
        return self._size_function
    
    @size_function.setter
    def size_function(self, size_function: Callable[..., int] | Literal["tokens", "characters", "words"]) -> None:
        self._set_size_function(size_function)

    def get_overlap_from_percentage(self, chunk_size: int, chunk_overlap: int|float) -> int:
        """
        Calculate the overlap size based on a percentage of the chunk size.
        
        Args:
            chunk_size: Size of each chunk
            chunk_overlap: Percentage of chunk size to overlap
        
        Returns:
            Size of the overlap
        """
        if chunk_overlap < 0 or chunk_overlap >= 1:
            raise ValueError("Overlap must be a percentage between 0 and 1")
        return int(chunk_size * chunk_overlap)

    def get_chunk_size(self, chunk_text: str, tokenizer_model: Optional[ModelName] = None) -> int:
        """
        Calculate the size of a chunk.
        
        Args:
            chunk_text: Text content of the chunk
            
        Returns:
            Size of the chunk
        """
        kwargs = self.size_function_kwargs if not tokenizer_model else combine_dicts(self.size_function_kwargs, {"model": tokenizer_model})
        return self.size_function(chunk_text, **kwargs)

    def get_chunk_id(
        self,
        chunk_num: int,
        chunk_text: str, 
        chunk_metadata: Optional[Dict[str, Any]],
        document_num: int,       
        document_id: Optional[str] = None,
        document_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Generate an ID for a chunk based on the document ID and chunk number.
        
        Args:
            chunk_num: Number of the chunk in the document
            chunk_text: Text content of the chunk
            chunk_metadata: Metadata for the chunk
            document_num: Number of the parent document in the document set
            document_id: ID of the parent document
            document_metadata: Metadata for the parent document
            **kwargs: Additional arguments
        Returns:
            String ID for the chunk in format "{document_id}_chunk_{chunk_num}"
        
        Note: When document_id is not set, the "{default_base_id}+{document_num} is used as the document ID.
        """
        if document_id is None:
            document_id = f"{self.default_base_id}_{document_num}"
        return f"{document_id}_chunk_{chunk_num}"

    def _split_text_with_regex(
        self,
        text: str,
        separator: str,
        keep_separator: Union[bool, Literal["start", "end"]]
    ) -> Iterator[str]:
        """Split text using regex pattern while optionally keeping separators.

        Args:
            text: Text to split
            separator: Separator pattern to split on
            keep_separator: Whether and where to keep separators

        Returns:
            Iterator of split text chunks
        """
        if not separator:
            yield from filter(bool, text)
            return
        if not keep_separator:
            yield from filter(bool, re.split(separator, text))
            return

        # Split and capture separators
        _chunks = re.split(f"({separator})", text)
        if keep_separator == "end":
            # Handle pairs of content + separator
            for i in range(0, len(_chunks) - 1, 2):
                if _chunks[i] + _chunks[i + 1]:
                    yield _chunks[i] + _chunks[i + 1]            
            # Handle last element if it exists
            if len(_chunks) % 2 == 0 and _chunks[-1]:
                yield _chunks[-1]
        else:  # keep_separator == "start"
            # Handle first element
            if _chunks[0]:
                yield _chunks[0]                
            # Handle pairs of separator + content
            for i in range(1, len(_chunks), 2):
                if i + 1 < len(_chunks) and _chunks[i] + _chunks[i + 1]:
                    yield _chunks[i] + _chunks[i + 1]

    def _recursive_split(
        self,
        text: str,
        separators: List[str],
        chunk_size: int,
        chunk_overlap: int,   
        strip_chars: str|Literal[False],        
        **kwargs
    ) -> Iterator[str]:
        """Recursively split text using multiple separators.

        Args:
            text: Text to split
            separators: List of separators to try
            chunk_size: Maximum chunk size
            **kwargs: Additional arguments passed to splitting functions

        Returns:
            Iterator of split text chunks
        """
        separator = separators[-1]
        new_separators = []
        for i, sep in enumerate(separators):
            if sep == "":
                separator = sep
                break
            if re.search(sep if self.regex else re.escape(sep), text):
                separator = sep
                new_separators = separators[i + 1:]
                break

        split_separator = separator if self.regex else re.escape(separator)
        chunks = self._split_text_with_regex(text, split_separator, self.keep_separator)
        
        stack: list[str] = []
        # if separator is space keep it when merging unless already keeping (avoids no spaces or double spaces respectively)
        merge_separator = separator if (separator == " ") ^ bool(self.keep_separator) else ""

        for chunk in chunks:
            if self.get_chunk_size(chunk) < chunk_size:
                stack.append(chunk)
                continue
            # Yield any accumulated chunks before processing the large chunk
            if stack:
                yield from self._merge_chunks(stack, merge_separator, chunk_size, chunk_overlap, strip_chars, **kwargs)
                stack = []            
            # Recursively split the large chunk
            if new_separators:
                yield from self._recursive_split(chunk, new_separators, chunk_size, chunk_overlap, strip_chars, **kwargs)
            else:
                # Or yield as is if no new separators
                yield chunk

        # Yield any remaining chunks
        if stack:
            yield from self._merge_chunks(stack, merge_separator, chunk_size, chunk_overlap, strip_chars, **kwargs)
    
    def _join_chunks(
            self, 
            texts: list[str], 
            separator: str,
            strip_chars: str|Literal[False],
            ) -> Optional[str]:
        text = separator.join(texts)
        if strip_chars is not False:
            text = text.strip(strip_chars)
        return text or None
    
    def _merge_chunks(
            self, 
            chunks: Iterable[str], 
            separator: str,
            chunk_size: int,
            chunk_overlap: int,
            strip_chars: str|Literal[False],
            **kwargs         
            ) -> Iterator[str]:
        sep_size = self.get_chunk_size(separator)
        
        stack: list[str] = []
        current_size = 0
        for chunk in chunks:
            current_chunk_size = self.get_chunk_size(chunk)
            current_sep_size = sep_size if stack else 0
            if (current_size + current_chunk_size + current_sep_size > chunk_size):
                if stack:
                    if (joined_chunk := self._join_chunks(stack, separator, strip_chars)) is not None:
                        yield joined_chunk
                    while current_size > chunk_overlap or (
                        current_size + current_chunk_size + (sep_size if stack else 0) > chunk_size
                        and current_size > 0
                    ):
                        current_size -= self.get_chunk_size(stack[0])
                        if len(stack) > 1:
                            current_size -= sep_size
                        stack = stack[1:]

            stack.append(chunk)
            current_size += current_chunk_size 
            if len(stack) > 1:
                current_size += sep_size

        if (joined_chunk := self._join_chunks(stack, separator, strip_chars)) is not None:
            yield joined_chunk

    def _chunk_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
        keep_separator: Literal["start", "end", False],
        strip_chars: str|Literal[False],
        **kwargs
    ) -> Iterator[str]:
        """Chunk text into smaller pieces using character-based splitting.

        Args:
            text: Text to chunk
            chunk_size: Maximum size of chunks
            chunk_overlap: Number of characters to overlap
            keep_separator: Whether to keep separators
            strip_chars: Characters to strip from chunks
            **kwargs: Additional arguments passed to splitting functions

        Returns:
            Iterator of text chunks
        """

        # For single separator case, use simple splitting
        if len(self.separators) == 1:
            split_separator = self.separators[0] if self.regex else re.escape(self.separators[0])
            merge_separator = self.separators[0] if self.keep_separator else ""
            chunks = self._split_text_with_regex(text, split_separator, keep_separator)
            yield from self._merge_chunks(chunks, merge_separator, chunk_size, chunk_overlap, strip_chars, **kwargs)
        # For multiple separators, use recursive splitting
        else:
            separators = self.separators.copy()
            if separators[-1] != "":
                separators.append("") # add empty separator to end of list so chunks are split correctly
            yield from self._recursive_split(text, separators, chunk_size, chunk_overlap, strip_chars, **kwargs)

    def _create_documents_from_texts_metadatas_ids(
            self,
            text_metadata_id_iterable: Iterable[tuple[str, Optional[Dict[str, Any]], Optional[str]]],
            chunk_size: Optional[int] = None,
            chunk_overlap: Optional[int|float] = None,
            strip_chars: Optional[str|Literal[False]] = None,
            keep_separator: Optional[Literal["start", "end", False]] = None,
            deepcopy_metadata: Optional[bool] = None,
            add_to_metadata: Optional[Collection[Literal["source", "chunk_size", "start_index", "end_index"]]] = None,      
            tokenizer_model: Optional[ModelName] = None,
            **kwargs
            ) -> Iterator[Document]:
        """
        Create Document instances from text and metadata.
        
        Args:
            texts: Text content of the documents
            metadatas: Metadata for the documents
            ids: IDs for the documents
            **kwargs: Additional keyword arguments passed to _chunk_text
        """
        chunk_size = chunk_size if chunk_size is not None else self.chunk_size
        chunk_overlap = chunk_overlap if chunk_overlap is not None else self.chunk_overlap
        if isinstance(chunk_overlap, float):
            chunk_overlap = self.get_overlap_from_percentage(chunk_size, chunk_overlap)
        strip_chars = strip_chars if strip_chars is not None else self.strip_chars
        keep_separator = keep_separator if keep_separator is not None else self.keep_separator
        deepcopy_metadata = deepcopy_metadata if deepcopy_metadata is not None else self.deepcopy_metadata
        add_to_metadata = add_to_metadata if add_to_metadata is not None else self.add_to_metadata
        if add_to_metadata:
            add_source_id_to_metadata = "source" in add_to_metadata
            add_chunk_size_to_metadata = "chunk_size" in add_to_metadata
            add_start_index_to_metadata = "start_index" in add_to_metadata
            add_end_index_to_metadata = "end_index" in add_to_metadata
            calculate_indicies = add_start_index_to_metadata or add_end_index_to_metadata
        else:
            add_source_id_to_metadata = add_chunk_size_to_metadata = add_start_index_to_metadata = add_end_index_to_metadata = calculate_indicies = False
        
        for doc_num, (doc_text, doc_metadata, doc_id) in enumerate(text_metadata_id_iterable):
            if calculate_indicies:
                current_position, prev_chunk_len = 0, 0

            for chunk_num, chunk_text in enumerate(self._chunk_text(doc_text, chunk_size, chunk_overlap, keep_separator, strip_chars, **kwargs)):
                if doc_metadata is None:
                    chunk_metadata = {}
                else:
                    chunk_metadata = deepcopy(doc_metadata) if deepcopy_metadata else doc_metadata.copy()
                
                if add_source_id_to_metadata:
                    chunk_metadata["source"] = doc_id   
                if add_chunk_size_to_metadata:
                    chunk_metadata["chunk_size"] = self.get_chunk_size(chunk_text)                                    
                if calculate_indicies:
                    offset = max(current_position + prev_chunk_len - chunk_overlap, 0) # type: ignore (current_position, prev_chunk_len will always be initialized when calculate_indicies is True)
                    current_position = doc_text.find(chunk_text, offset)
                    prev_chunk_len = len(chunk_text)
                    if add_start_index_to_metadata:
                        chunk_metadata["start_index"] = current_position
                    if add_end_index_to_metadata:
                        chunk_metadata["end_index"] = current_position + prev_chunk_len

                chunk_id = self.get_chunk_id(chunk_num, chunk_text, chunk_metadata, doc_num, doc_id, doc_metadata, **kwargs)
                yield Document(id=chunk_id, text=chunk_text, metadata=chunk_metadata)

    def _text_metadata_id_iterable_from_documents(
            self,
            documents: Iterable[Document],
            strip_chars: Optional[str|Literal[False]] = None,
            ) -> Iterable[tuple[str, Optional[Dict[str, Any]], Optional[str]]]:
        strip_chars = strip_chars if strip_chars is not None else self.strip_chars
        for document in documents:
            if (not (doc_text := document.text) # Null or empty text before stripping
                or (strip_chars is not False and not doc_text.strip(strip_chars)) # empty text after stripping (Note2self is not False since .strip(None) is valid)
                ):
                continue
            yield document.text, document.metadata, document.id

    def ichunk_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[Iterable[Dict[str, Any]]] = None,
            ids: Optional[Iterable[str]] = None,
            chunk_size: Optional[int] = None,
            chunk_overlap: Optional[int|float] = None,
            strip_chars: Optional[str|Literal[False]] = None,
            keep_separator: Optional[Literal["start", "end", False]] = None,
            deepcopy_metadata: Optional[bool] = None,
            add_to_metadata: Optional[Collection[Literal["source", "chunk_size", "start_index", "end_index"]]] = None,      
            **kwargs
            ) -> Iterator[Document]:       
        _txt_md_id_iterable = zip_longest(texts, metadatas or (), ids or ())
        return self._create_documents_from_texts_metadatas_ids(
            _txt_md_id_iterable, chunk_size, chunk_overlap, strip_chars, keep_separator, 
            deepcopy_metadata, add_to_metadata, **kwargs
        )

    @copy_paramspec_from(ichunk_texts)
    def chunk_texts(self, *args, **kwargs):
        return list(self.ichunk_texts(*args, **kwargs))

    def ichunk_documents(
            self,
            documents: Iterable[Document],
            chunk_size: Optional[int] = None,
            chunk_overlap: Optional[int|float] = None,
            strip_chars: Optional[str|Literal[False]] = None,
            keep_separator: Optional[Literal["start", "end", False]] = None,
            deepcopy_metadata: Optional[bool] = None,
            add_to_metadata: Optional[Collection[Literal["source", "chunk_size", "start_index", "end_index"]]] = None,      
            **kwargs
            ) -> Iterator[Document]:
        _txt_md_id_iterable = self._text_metadata_id_iterable_from_documents(documents, strip_chars)
        return self._create_documents_from_texts_metadatas_ids(
            _txt_md_id_iterable, chunk_size, chunk_overlap, strip_chars, keep_separator, 
            deepcopy_metadata, add_to_metadata, **kwargs
        )
    
    @copy_paramspec_from(ichunk_documents)
    def chunk_documents(self, *args, **kwargs):
        return list(self.ichunk_documents(*args, **kwargs))
    
    def ichunk_document(
            self,
            document: Document,
            chunk_size: Optional[int] = None,
            chunk_overlap: Optional[int|float] = None,
            strip_chars: Optional[str|Literal[False]] = None,
            keep_separator: Optional[Literal["start", "end", False]] = None,
            deepcopy_metadata: Optional[bool] = None,
            add_to_metadata: Optional[Collection[Literal["source", "chunk_size", "start_index", "end_index"]]] = None,      
            **kwargs
            ) -> Iterator[Document]:
        _txt_md_id_iterable = [(document.text or "", document.metadata, document.id)]
        return self._create_documents_from_texts_metadatas_ids(
            _txt_md_id_iterable, chunk_size, chunk_overlap, strip_chars, keep_separator, 
            deepcopy_metadata, add_to_metadata, **kwargs
        )

    @copy_paramspec_from(ichunk_document)
    def chunk_document(self, *args, **kwargs):
        return list(self.ichunk_document(*args, **kwargs))