from typing import TYPE_CHECKING, Any, Literal, Optional, Type
from typing import Any, Callable, Collection, Literal, Optional, Sequence, Type, Union, Iterable, Generator, overload

if TYPE_CHECKING:
    from ..types.annotations import ComponentName, ProviderName, ToolName
    from ..configs import UnifAIConfig
    from pathlib import Path

from ..type_conversions import standardize_config

from ..types import (
    ProviderName,
    Message,
    MessageChunk,
    MessageInput, 
    Tool,
    ToolInput,
)
from ..type_conversions import standardize_tool, standardize_tools
from ..types.annotations import ComponentName, ProviderName, ModelName, ToolName, ToolInput, BaseModel
from ..configs.llm_config import LLMConfig
from ..configs.chat_config import ChatConfig
from ..configs.tool_caller_config import ToolCallerConfig

from ..components._base_components._base_llm import LLM
from ..components._base_components._base_tool_caller import ToolCaller
from ..components.prompt_templates import PromptTemplate
from ..components.chats import Chat
from ._base_client import BaseClient, UnifAIConfig, Path

from ..utils import update_kwargs_with_locals, copy_paramspec_from


class UnifAIChatClient(BaseClient):
    
    def configure(
        self,
        config: Optional["UnifAIConfig|dict[str, Any]|str|Path"] = None,
        api_keys: Optional["dict[ProviderName, str]"] = None,
        **kwargs
    ) -> None:
        BaseClient.configure(self, config, api_keys, **kwargs)
        self._init_tools(self.config.tools, self.config.tool_callables)

    # Tools
    def _init_tools(
            self, 
            tools: Optional[Iterable[ToolInput]] = None, 
            tool_callables: Optional[dict[str, Callable]] = None
            ) -> None:
        self._tools: dict[str, Tool] = {}
        self._tool_callables: dict[str, Callable] = {} 
        # Maybe TODO Tools in Config?
        if tools:
            self.register_tools(tools, tool_callables)

    def _cleanup_tools(self) -> None:
        self._tools.clear()
        self._tool_callables.clear()

    def cleanup(self) -> None:
        BaseClient.cleanup(self)
        self._cleanup_tools()

    def register_tool(
            self, 
            tool: ToolInput, 
            tool_callable: Optional[Callable] = None, 
            tool_name: Optional[str] = None
        ) -> None:
        tool = standardize_tool(tool)
        tool_name = tool_name or tool.name
        self._tools[tool_name] = tool
        if tool_callable:
            self.register_tool_callable(tool_name, tool_callable)

    def register_tools(
            self, 
            tools: Iterable[ToolInput], 
            tool_callables: Optional[dict[str, Callable]] = None
        ) -> None:
        for tool_name, tool in standardize_tools(tools).items():
            self.register_tool(tool, tool_callables.get(tool_name) if tool_callables else None)       

    def register_tool_callable(
            self, 
            tool_name: ToolName, 
            tool_callable: Callable,
            update_tool_instance: bool = False
        ) -> None:
        self._tool_callables[tool_name] = tool_callable
        if update_tool_instance:
            if not (tool := self._tools.get(tool_name)):
                raise ValueError(f"Tool {tool_name} not found in registry. Tool callable must be registered after the tool when update_tool_instance is True.")
            tool.callable = tool_callable

    def register_tool_callables(
            self, 
            tool_callables: dict[str, Callable],
            update_tool_instances: bool = False
        ) -> None:
        for tool_name, tool_callable in tool_callables.items():
            self.register_tool_callable(tool_name, tool_callable, update_tool_instances)

    def get_tool(self, tool_name: ToolName,) -> Tool:
        return self._tools[tool_name]
        
    def get_tool_callable(self, tool_name: ToolName,) -> Optional[Callable]:
        return self._tool_callables.get(tool_name)


    # Chat
    def start_chat_from_config(
            self, 
            config: ChatConfig,
            messages: Optional[Sequence[MessageInput]] = None,            
            **init_kwargs
        ) -> Chat:
        return Chat(
            config=config, 
            messages=messages,
            tool_registry=self._tools,
            _get_component=self._get_component, 
            **init_kwargs
        )

    def start_chat(
        self,
        messages: Optional[Sequence[MessageInput]] = None,
        llm: ProviderName | LLMConfig | tuple[ProviderName, ComponentName] = "default",
        llm_model: Optional[ModelName] = None,
        system_prompt: Optional[str | PromptTemplate | Callable[...,str]] = None,
        examples: Optional[list[Union[Message, dict[Literal["input", "response"], Any]]]] = None,
        tools: Optional[list[ToolInput]] = None,
        tool_choice: Optional[ToolName | Tool | Literal["auto", "required", "none"] | Sequence[ToolName | Tool | Literal["auto", "required", "none"]]] = None,
        enforce_tool_choice: bool = True,
        tool_choice_error_retries: int = 3,
        tool_callables: Optional[dict[ToolName, Callable[..., Any]]] = None,
        tool_caller: Optional[ProviderName | ToolCallerConfig | tuple[ProviderName, ComponentName]] = "default",

        response_format: Optional[Literal["text", "json"] | Type[BaseModel] | Tool | dict[Literal["json_schema"], dict[str, str] | Type[BaseModel] | Tool]] = None,
        return_on: Union[Literal["content", "tool_call", "message"], ToolName, Tool, list[ToolName | Tool]] = "content",

        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        stop_sequences: Optional[list[str]] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,

        max_messages_per_run: int = 10,
        max_tool_calls_per_run: Optional[int] = None,
        max_tokens_per_run: Optional[int] = None,
        max_input_tokens_per_run: Optional[int] = None,
        max_output_tokens_per_run: Optional[int] = None,
        count_tokens_proactively: bool = False,

        **init_kwargs
    ) -> Chat:        
        config_kwargs = update_kwargs_with_locals({}, locals(), exclude=("self", "messages", "tools"))
        config_kwargs["tools"] = [standardize_tool(tool, self._tools) for tool in tools] if tools else None
        return self.start_chat_from_config(ChatConfig(**config_kwargs), messages, **init_kwargs)

    @copy_paramspec_from(start_chat)
    def chat(self, *args, messages: Optional[Sequence[MessageInput]] = None, **kwargs) -> Chat:
        chat = self.start_chat(*args, messages=messages, **kwargs)
        if messages:
            chat.run()
        return chat
    
    @copy_paramspec_from(start_chat)    
    def chat_stream(self, *args, messages: Optional[Sequence[MessageInput]] = None, **kwargs) -> Generator[MessageChunk, None, Chat]:
        chat = self.start_chat(*args, messages=messages, **kwargs)
        if messages:
            yield from chat.run_stream()
        return chat

    # def chat(
    #     self,
    #     messages: Optional[Sequence[MessageInput]] = None,
    #     llm: ProviderName | LLMConfig | tuple[ProviderName, ComponentName] = "default",
    #     llm_model: Optional[ModelName] = None,
    #     system_prompt: Optional[str | PromptTemplate | Callable[...,str]] = None,
    #     examples: Optional[list[Union[Message, dict[Literal["input", "response"], Any]]]] = None,
    #     tools: Optional[list[ToolInput]] = None,
    #     tool_choice: Optional[ToolName | Tool | Literal["auto", "required", "none"] | Sequence[ToolName | Tool | Literal["auto", "required", "none"]]] = None,
    #     enforce_tool_choice: bool = True,
    #     tool_choice_error_retries: int = 3,
    #     tool_callables: Optional[dict[ToolName, Callable[..., Any]]] = None,
    #     tool_caller: Optional[ProviderName | ToolCallerConfig | tuple[ProviderName, ComponentName]] = "default",

    #     response_format: Optional[Literal["text", "json"] | Type[BaseModel] | Tool | dict[Literal["json_schema"], dict[str, str] | Type[BaseModel] | Tool]] = None,
    #     return_on: Union[Literal["content", "tool_call", "message"], ToolName, Tool, list[ToolName | Tool]] = "content",

    #     frequency_penalty: Optional[float] = None,
    #     presence_penalty: Optional[float] = None,
    #     seed: Optional[int] = None,
    #     stop_sequences: Optional[list[str]] = None,
    #     temperature: Optional[float] = None,
    #     top_k: Optional[int] = None,
    #     top_p: Optional[float] = None,

    #     max_messages_per_run: int = 10,
    #     max_tool_calls_per_run: Optional[int] = None,
    #     max_tokens_per_run: Optional[int] = None,
    #     max_input_tokens_per_run: Optional[int] = None,
    #     max_output_tokens_per_run: Optional[int] = None,
    #     count_tokens_proactively: bool = False,

    #     **init_kwargs
    # ) -> Chat:
    #     config_kwargs = update_kwargs_with_locals({}, locals(), exclude=("self", "messages", "tools"))
    #     config_kwargs["tools"] = [standardize_tool(tool, self._tools) for tool in tools] if tools else None
    #     chat = self.start_chat_from_config(ChatConfig(**config_kwargs), messages, **init_kwargs)
    #     if messages:
    #         chat.run()
    #     return chat
        
    # def chat_stream(
    #     self,
    #     messages: Optional[Sequence[MessageInput]] = None,
    #     llm: ProviderName | LLMConfig | tuple[ProviderName, ComponentName] = "default",
    #     llm_model: Optional[ModelName] = None,
    #     system_prompt: Optional[str | PromptTemplate | Callable[...,str]] = None,
    #     examples: Optional[list[Union[Message, dict[Literal["input", "response"], Any]]]] = None,
    #     tools: Optional[list[ToolInput]] = None,
    #     tool_choice: Optional[ToolName | Tool | Literal["auto", "required", "none"] | Sequence[ToolName | Tool | Literal["auto", "required", "none"]]] = None,
    #     enforce_tool_choice: bool = True,
    #     tool_choice_error_retries: int = 3,
    #     tool_callables: Optional[dict[ToolName, Callable[..., Any]]] = None,
    #     tool_caller: Optional[ProviderName | ToolCallerConfig | tuple[ProviderName, ComponentName]] = "default",

    #     response_format: Optional[Literal["text", "json"] | Type[BaseModel] | Tool | dict[Literal["json_schema"], dict[str, str] | Type[BaseModel] | Tool]] = None,
    #     return_on: Union[Literal["content", "tool_call", "message"], ToolName, Tool, list[ToolName | Tool]] = "content",

    #     frequency_penalty: Optional[float] = None,
    #     presence_penalty: Optional[float] = None,
    #     seed: Optional[int] = None,
    #     stop_sequences: Optional[list[str]] = None,
    #     temperature: Optional[float] = None,
    #     top_k: Optional[int] = None,
    #     top_p: Optional[float] = None,

    #     max_messages_per_run: int = 10,
    #     max_tool_calls_per_run: Optional[int] = None,
    #     max_tokens_per_run: Optional[int] = None,
    #     max_input_tokens_per_run: Optional[int] = None,
    #     max_output_tokens_per_run: Optional[int] = None,
    #     count_tokens_proactively: bool = False,
    #     **init_kwargs
    # ) -> Generator[MessageChunk, None, Chat]:
    #     config_kwargs = update_kwargs_with_locals({}, locals(), exclude=("self", "messages", "tools"))
    #     config_kwargs["tools"] = [standardize_tool(tool, self._tools) for tool in tools] if tools else None
    #     chat = self.start_chat_from_config(ChatConfig(**config_kwargs), messages, **init_kwargs)
    #     if messages:
    #         yield from chat.run_stream()
    #     return chat