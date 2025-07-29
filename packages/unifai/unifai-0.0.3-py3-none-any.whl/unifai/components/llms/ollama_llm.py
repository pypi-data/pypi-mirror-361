from typing import Optional, Union, Sequence, Any, Literal, Mapping,  Iterator, Iterable, Generator, Collection
from datetime import datetime
from json import loads as json_loads, JSONDecodeError

from ollama._types import (
    ChatResponse as OllamaChatResponse,
    Message as OllamaMessage,
    Tool as OllamaTool, 
    Options as OllamaOptions,
)

OllamaToolFunction = OllamaTool.Function
OllamaParameters = OllamaToolFunction.Parameters
OllamaProperty = OllamaParameters.Property
OllamaToolCall = OllamaMessage.ToolCall
OllamaToolCallFunction = OllamaToolCall.Function

from ...exceptions import ProviderUnsupportedFeatureError
from ...types import Message, MessageChunk, Tool, ToolCall, Image, Usage, ResponseInfo
from ...utils import stringify_content, generate_random_id
from ..adapters.ollama_adapter import OllamaAdapter
from .._base_components._base_llm import LLM


class OllamaLLM(OllamaAdapter, LLM):
    provider = "ollama"
    default_llm_model = "mistral:7b-instruct"

    _system_prompt_input_type = "first_message"

    # List Models
    def _list_models(self) -> list[str]:
        return OllamaAdapter._list_models(self)

    # Chat
    def _get_chat_response(
            self,
            stream: bool,            
            messages: list[OllamaMessage],     
            model: Optional[str] = None, 
            system_prompt: Optional[str] = None,                   
            tools: Optional[list[OllamaTool]] = None,
            tool_choice: Optional[str] = None,
            response_format: Optional[Literal["", "json"]] = '',
            max_tokens: Optional[int] = None,
            frequency_penalty: Optional[float] = None,
            presence_penalty: Optional[float] = None,
            seed: Optional[int] = None,
            stop_sequences: Optional[list[str]] = None, 
            temperature: Optional[float] = None,
            top_k: Optional[int] = None,
            top_p: Optional[float] = None,             
            **kwargs
            ) -> OllamaChatResponse|Iterator[OllamaChatResponse]:
        
            user_messages = [message for message in messages if message["role"] == 'user']
            last_user_content = user_messages[-1].get("content", "") if user_messages else ""            
            if (tool_choice and tool_choice != "auto" and last_user_content is not None
                ):                
                if tool_choice == "required":
                    user_messages[-1]["content"] = f"{last_user_content}\nYou MUST call one or more tools."
                elif tool_choice == "none":
                    user_messages[-1]["content"] = f"{last_user_content}\nYou CANNOT call any tools."
                else:
                    user_messages[-1]["content"] = f"{last_user_content}\nYou MUST call the tool '{tool_choice}' with ALL of its required arguments."
                last_user_content_modified = True
            else:
                last_user_content_modified = False

            keep_alive = kwargs.pop('keep_alive', None)
                        
            if frequency_penalty is not None:
                kwargs["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                kwargs["presence_penalty"] = presence_penalty
            if seed is not None:
                kwargs["seed"] = seed
            if stop_sequences is not None:
                kwargs["stop"] = stop_sequences
            if temperature is not None:
                kwargs["temperature"] = temperature
            if top_k is not None:
                kwargs["top_k"] = top_k
            if top_p is not None:
                kwargs["top_p"] = top_p

            options = OllamaOptions(**kwargs) if kwargs else None

            response = self.client.chat(
                model=model or self.default_model, 
                messages=messages,                 
                tools=tools, 
                stream=stream,
                format=response_format, 
                options=options,
                keep_alive=keep_alive,
            )

            if last_user_content_modified:
                user_messages[-1]["content"] = last_user_content

            return response


    # Convert from UnifAI to AI Provider format        
        # Messages    
    def format_user_message(self, message: Message) -> OllamaMessage:
        content = message.content or ''
        images = list(map(self.format_image, message.images)) if message.images else None
        return OllamaMessage(role='user', content=content, images=images)

    def format_assistant_message(self, message: Message) -> OllamaMessage:
        content = message.content or ''
        images = list(map(self.format_image, message.images)) if message.images else None
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                OllamaToolCall(
                    function=OllamaToolCallFunction(
                        name=tool_call.tool_name, 
                        arguments=tool_call.arguments
                    )
                ) 
                for tool_call in message.tool_calls
            ]
        return OllamaMessage(role='assistant', content=content, images=images, tool_calls=tool_calls)
        
    def format_tool_message(self, message: Message) -> OllamaMessage:
        if message.tool_calls:
            content = stringify_content(message.tool_calls[0].output)
            images = list(map(self.format_image, message.images)) if message.images else None
            return OllamaMessage(role='tool', content=content, images=images, tool_calls=None)         
        raise ValueError("Tool message must have tool_calls")

    def split_tool_message(self, message: Message) -> Iterator[Message]:        
        if tool_calls := message.tool_calls:
            for tool_call in tool_calls:
                yield Message(role="tool", tool_calls=[tool_call])
        if message.content is not None:
            yield Message(role="user", content=message.content)     

    def format_system_message(self, message: Message) -> OllamaMessage:
        return OllamaMessage(role='system', content=message.content or '')
    

        # Images
    def format_image(self, image: Image) -> Any:
        return image.raw_bytes


        # Tools
    def format_tool(self, tool: Tool) -> OllamaTool:
        if tool.type != "function":
            raise ValueError("Only function tools are supported by Ollama")

        properties = {}
        for i, parameter in enumerate(tool.parameters.values()):
            # TODO test if Ollama supports this being recursive ie nested properties
            if parameter.name is None:
                raise ValueError(f"All Ollama tool parameters must have a name. Tool '{tool.name}' parameter {i} is missing a name")
            if parameter.enum is not None:
                raise ProviderUnsupportedFeatureError(
                    f"Ollama no longer supports enum properties. Tool '{tool.name}' parameter {i} '{parameter.name}' has an enum value of {parameter.enum}"
                )
            if parameter.type in ("object", "array", "ref", "anyOf"):
                raise ProviderUnsupportedFeatureError(
                    f"Ollama does not yet support {parameter.type} properties. Tool '{tool.name}' parameter {i} '{parameter.name}' has a type of {parameter.type}"
                )            
            properties[parameter.name] = OllamaProperty(type=parameter.type, description=parameter.description)

        return OllamaTool(
            type=tool.type, 
            function=OllamaToolFunction(
                name=tool.name, 
                description=tool.description, 
                parameters=OllamaParameters(
                    type='object',
                    properties=properties,
                    required=tool.parameters.required,
                )
            )
        )    

    def format_tool_choice(self, tool_choice: str) -> str:
        return tool_choice


        # Response Format
    def format_response_format(self, response_format: Optional[Literal["text", "json"] | Tool]) -> Literal["", "json"] | dict[str, Any]:
        if not response_format or response_format == "text":
            return ""
        elif response_format == "json" or response_format == "json_object":
            return "json"
        # elif isinstance(response_format, Tool):
        #     return response_format.to_json_schema()        
        else:
            raise ValueError(f"Invalid response_format: {response_format}")


    # Convert Objects from AI Provider to UnifAI format    
        # Images
    def parse_image(self, response_image: Any, **kwargs) -> Image:
        raise NotImplementedError("This method must be implemented by the subclass")


        # Tool Calls
    def parse_tool_call(self, response_tool_call: OllamaToolCall, **kwargs) -> ToolCall:
        return ToolCall(
            id=f'call_{generate_random_id(24)}',
            tool_name=response_tool_call['function']['name'],
            arguments=response_tool_call['function'].get('arguments')
        )


        # Response Info (Model, Usage, Done Reason, etc.)
    def parse_done_reason(self, response_obj: OllamaChatResponse, **kwargs) -> str|None:        
        if not (done_reason := response_obj.get("done_reason")):
            return None
        elif done_reason == "stop" and response_obj["message"].get("tool_calls"):
            return "tool_calls"
        elif done_reason != "stop":
            # TODO handle other done_reasons 
            return "max_tokens"
        return done_reason
    
    def parse_usage(self, response_obj: OllamaChatResponse, **kwargs) -> Usage|None:
        return Usage(
            input_tokens=response_obj.get("prompt_eval_count", 0), 
            output_tokens=response_obj.get("eval_count", 0)
        )

    def parse_response_info(self, response: Any, **kwargs) -> ResponseInfo:
        model = response["model"]
        done_reason = self.parse_done_reason(response)
        usage = self.parse_usage(response)
        return ResponseInfo(model=model, provider=self.provider, done_reason=done_reason, usage=usage) 
    
    
        # Assistant Messages (Content, Images, Tool Calls, Response Info)
    def parse_message(self, response: OllamaChatResponse, **kwargs) -> tuple[Message, OllamaMessage]:
        client_message = response['message']
        images = None # TODO: Implement image extraction        
        tool_calls = None
        if client_message_tool_calls := client_message.get('tool_calls'):
            tool_calls = list(map(self.parse_tool_call, client_message_tool_calls))
        
        created_at = datetime.strptime(f'{response["created_at"][:26]}Z', '%Y-%m-%dT%H:%M:%S.%fZ')
        response_info = self.parse_response_info(response)        

        unifai_message = Message(
            role=client_message['role'],
            content=client_message.get('content'),            
            tool_calls=tool_calls,
            images=images,
            created_at=created_at,
            response_info=response_info
        )
        return unifai_message, client_message
    
    def parse_stream(self, response: Iterator[OllamaChatResponse], **kwargs) -> Generator[MessageChunk, None, tuple[Message, OllamaMessage]]:
        content = ""
        tool_calls = []
        model = None
        usage = None
        done_reason = None
        lbrackets, rbrackets = 0, 0
        for chunk in response:
            if not model:
                model = chunk.get("model")
            if not done_reason:
                done_reason = self.parse_done_reason(chunk)
            if not usage:
                usage = self.parse_usage(chunk)

            if (chunk_message := chunk.get("message")) and (chunk_content := chunk_message.get("content")):
                    content += chunk_content
                    lbrackets += chunk_content.count("{")
                    rbrackets += chunk_content.count("}")
                    if lbrackets and lbrackets == rbrackets:
                        try:
                            tool_call_dict = json_loads(content)
                            tool_call = ToolCall(
                                id=f'call_{generate_random_id(24)}',
                                tool_name=tool_call_dict['name'],
                                arguments=tool_call_dict.get('parameters')
                            )
                            tool_calls.append(tool_call)
                            yield MessageChunk(
                                role="assistant", 
                                tool_calls=[tool_call]
                            )
                            content = ""
                            lbrackets, rbrackets = 0, 0
                        except JSONDecodeError as e:
                            # TODO log e
                            yield MessageChunk(
                                role="assistant", 
                                content=chunk_content
                            )
                    elif lbrackets > rbrackets:
                        continue
                    else:
                        yield MessageChunk(
                            role="assistant", 
                            content=chunk_content
                        )
                
        response_info = ResponseInfo(model=model, done_reason=done_reason, usage=usage)
        unifai_message = Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
            response_info=response_info
        )
        return unifai_message, self.format_assistant_message(unifai_message)