from typing import Optional, Union, Sequence, Any, Literal, Mapping, Iterator, Generator
from json import loads as json_loads

from anthropic import Anthropic
from anthropic.types import (
    Usage as AnthropicUsage,    
    Message as AnthropicMessage,
    MessageParam as AnthropicMessageParam,
    ContentBlock as AnthropicContentBlock,
    TextBlock as AnthropicTextBlock,
    ToolUseBlock as AnthropicToolUseBlock,
    TextBlockParam as AnthropicTextBlockParam,
    ImageBlockParam as AnthropicImageBlockParam,
    ToolUseBlockParam as AnthropicToolUseBlockParam,
    ToolResultBlockParam as AnthropicToolResultBlockParam,
    ToolParam as AnthropicToolParam, 
    RawMessageStreamEvent as AnthropicRawMessageStreamEvent,
)
from anthropic._streaming import Stream
from anthropic.types.image_block_param import Source as AnthropicImageSource


from anthropic import (
    AnthropicError,
    APIError as AnthropicAPIError,
    APIConnectionError as AnthropicAPIConnectionError,
    APITimeoutError as AnthropicAPITimeoutError,
    APIResponseValidationError as AnthropicAPIResponseValidationError,
    APIStatusError as AnthropicAPIStatusError,
    AuthenticationError as AnthropicAuthenticationError,
    BadRequestError as AnthropicBadRequestError,
    ConflictError as AnthropicConflictError,
    InternalServerError as AnthropicInternalServerError,
    NotFoundError as AnthropicNotFoundError,
    PermissionDeniedError as AnthropicPermissionDeniedError,
    RateLimitError as AnthropicRateLimitError,
    UnprocessableEntityError as AnthropicUnprocessableEntityError,
)

from unifai.exceptions import (
    UnifAIError,
    APIError,
    UnknownAPIError,
    APIConnectionError,
    APITimeoutError,
    APIResponseValidationError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
    STATUS_CODE_TO_EXCEPTION_MAP,
    ProviderUnsupportedFeatureError  
)

from ...exceptions import ProviderUnsupportedFeatureError
from ...types import Message, MessageChunk, Tool, ToolCall, Image, Usage, ResponseInfo, Embeddings
from ...utils import stringify_content
from ..adapters.anthropic_adapter import AnthropicAdapter
from .._base_components._base_llm import LLM
    
class AnthropicLLM(AnthropicAdapter, LLM):
    default_llm_model = "claude-3-5-sonnet-20240620"

    _system_prompt_input_type = "kwarg"

    # List Models
    def _list_models(self) -> list[str]:
        return AnthropicAdapter._list_models(self)
        
    # Chat    
    def _get_chat_response(
            self,
            stream: bool,
            messages: list[AnthropicMessageParam], 
            model: Optional[str] = None, 
            system_prompt: Optional[str] = None,                 
            tools: Optional[list[AnthropicToolParam]] = None,
            tool_choice: Optional[dict] = None,
            response_format: Optional[Union[str, dict[str, str]]] = None,
            max_tokens: Optional[int] = None,
            frequency_penalty: Optional[float] = None,
            presence_penalty: Optional[float] = None,
            seed: Optional[int] = None,
            stop_sequences: Optional[list[str]] = None, 
            temperature: Optional[float] = None,
            top_k: Optional[int] = None,
            top_p: Optional[float] = None,             
            **kwargs
            ) -> AnthropicMessage|Stream[AnthropicRawMessageStreamEvent]:
        
        if stream:
            kwargs["stream"] = True
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = tools
            if tool_choice and tool_choice.get("type") != "none":
                # TODO Fix tool_choice == "none" bug (Should not call tools, currently equivalent to None not "none")
                kwargs["tool_choice"] = tool_choice

        max_tokens = max_tokens or 4096
        if stop_sequences is not None:
            kwargs["stop_sequences"] = stop_sequences
        if temperature is not None:
            kwargs["temperature"] = temperature
        if top_k is not None:
            kwargs["top_k"] = top_k
        if top_p is not None:
            kwargs["top_p"] = top_p

        return self.client.messages.create(
            max_tokens=max_tokens,
            messages=messages,
            model=model,
            **kwargs
        )


    # Convert Objects from UnifAI to AI Provider format            
        # Messages
    def format_user_message(self, message: Message) -> AnthropicMessageParam:
        content = []
        if message.images:
            content.extend(map(self.format_image, message.images))        
        if message.content:
            content.append(AnthropicTextBlockParam(text=message.content, type="text"))

        return AnthropicMessageParam(role="user", content=content)

    def format_assistant_message(self, message: Message) -> AnthropicMessageParam:
        content = []
        if message.content:
            content.append(AnthropicTextBlockParam(text=message.content, type="text"))
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_use_param = AnthropicToolUseBlockParam(
                    id=tool_call.id,
                    name=tool_call.tool_name,
                    input=tool_call.arguments,
                    type="tool_use"
                )
                content.append(tool_use_param)
        if message.images:
            content.extend(map(self.format_image, message.images))
        
        if not content:
            # Should not happen unless switching providers after a tool call
            content.append(AnthropicTextBlockParam(text="continue", type="text"))
        
        return AnthropicMessageParam(role="assistant", content=content)

    def format_tool_message(self, message: Message) -> AnthropicMessageParam:
        content = []
        # if message.content:
        #     content.append(AnthropicTextBlockParam(text=message.content, type="text"))
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_result_content = []
                # if message.content:
                #     tool_result_content.append(AnthropicTextBlockParam(text=message.content, type="text"))                
                tool_result_content.append(AnthropicTextBlock(text=stringify_content(tool_call.output), type="text"))

                tool_result_param = AnthropicToolResultBlockParam(
                    tool_use_id=tool_call.id,
                    content=tool_result_content,
                    is_error=False,
                    type="tool_result"
                )
                content.append(tool_result_param)
            return AnthropicMessageParam(role="user", content=content)
        raise ValueError("Tool messages must have tool calls")

    def format_system_message(self, message: Message) -> AnthropicMessageParam:
        raise ProviderUnsupportedFeatureError("Anthropic does not support system messages")
    

        # Images
    def format_image(self, image: Image) -> AnthropicImageBlockParam:
        return AnthropicImageBlockParam(
            type="image",
            source=AnthropicImageSource(
                type="base64",
                data=image.path or image.base64_string,
                media_type=image.mime_type                
            )
        )


        # Tools
    def format_tool(self, tool: Tool) -> AnthropicToolParam:
        return AnthropicToolParam(
            name=tool.name,
            description=tool.description,
            input_schema=tool.parameters.to_dict()
        )    

    def format_tool_choice(self, tool_choice: str) -> dict:
        if tool_choice == "required":
            tool_choice = "any"
        if tool_choice in ("auto", "any", "none"):
            return {"type": tool_choice}        
        return {"type": "tool", "name": tool_choice}


        # Response Format
    def format_response_format(self, response_format: Optional[Literal["text", "json"] | Tool]) -> None:
        raise ProviderUnsupportedFeatureError("Anthropic does not support response_format")

    # Convert Objects from AI Provider to UnifAI format    
        # Images
    def parse_image(self, response_image: Any, **kwargs) -> Image:
        raise ProviderUnsupportedFeatureError("Anthropic does not support image parsing")        

        # Tool Calls
    def parse_tool_call(self, response_tool_call: AnthropicToolUseBlock, **kwargs) -> ToolCall:
        return ToolCall(
                    id=response_tool_call.id,
                    tool_name=response_tool_call.name,
                    arguments=response_tool_call.input 
                )
    
        # Response Info (Model, Usage, Done Reason, etc.)
    def parse_done_reason(self, response_obj: AnthropicMessage, **kwargs) -> str|None:
        done_reason = response_obj.stop_reason
        if done_reason == "end_turn" or done_reason == "stop_sequence":
            return "stop"
        if done_reason == "tool_use":
            return "tool_calls"
        # "max_tokens" or None
        return done_reason

    def parse_usage(self, response_obj: AnthropicMessage, **kwargs) -> Usage|None:
        if response_usage := response_obj.usage:
            return Usage(
                input_tokens=response_usage.input_tokens, 
                output_tokens=response_usage.output_tokens
            )

    def parse_response_info(self, response: AnthropicMessage, **kwargs) -> ResponseInfo:
        model = response.model                     
        done_reason = self.parse_done_reason(response)
        usage = self.parse_usage(response)
        return ResponseInfo(model=model, provider=self.provider, done_reason=done_reason, usage=usage) 

    # Assistant Messages (Content, Images, Tool Calls, Response Info)
    def parse_message(self, response: AnthropicMessage, **kwargs) -> tuple[Message, AnthropicMessageParam]:
        client_message = AnthropicMessageParam(role=response.role, content=response.content)
        content = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(self.parse_tool_call(block))

        images = None # TODO: Implement image extraction  
        response_info = self.parse_response_info(response)

        unifai_message = Message(
            role=response.role,
            content=content or None,
            tool_calls=tool_calls or None,
            images=images or None,
            response_info=response_info,
        )
        return unifai_message, client_message 
    
    def parse_stream(self, response: Stream[AnthropicRawMessageStreamEvent], **kwargs) -> Generator[MessageChunk, None, tuple[Message, AnthropicMessageParam]]:
        message = None
        pings = 0
        # content = []        
        for event in response:
            event_type = event.type
            if event_type == "ping":
                pings += 1
                continue
            if event_type == "erorr":
                #TODO: Implement error handling mid stream
                error = event.error
                raise NotImplementedError("Error handling not implemented")

            if event_type == "message_start":
                message = event.message
                continue

            if not message:
                raise ValueError("No message found")

            if event_type == "message_delta":
                delta = event.delta
                message.stop_reason = delta.stop_reason
                message.stop_sequence = delta.stop_sequence
                # message.usage.input_tokens = event.usage.input_tokens                 
                message.usage.output_tokens += event.usage.output_tokens

            if event_type == "message_stop":
                break
                
            if event_type == "content_block_start":
                index = event.index
                content_block = event.content_block
                if content_block.type == "tool_use":
                    content_block.input = ""
                message.content.insert(index, content_block)

            if event_type == "content_block_delta":
                index = event.index
                delta = event.delta
                
                if delta.type == "text_delta":
                    message.content[index].text += delta.text
                    yield MessageChunk(role="assistant", content=delta.text)
                elif delta.type == "input_json_delta":
                    message.content[index].input += delta.partial_json

            if event_type == "content_block_stop":
                index = event.index
                content_block = message.content[index]

                if content_block.type == "tool_use":
                    content_block.input = json_loads(content_block.input)
                    tool_call = self.parse_tool_call(content_block)
                    yield MessageChunk(role="assistant", tool_calls=[tool_call])

        if message is None:
            raise ValueError("No message found")
                    
        return self.parse_message(message, **kwargs)