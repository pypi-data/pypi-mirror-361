import pytest
from unifai import UnifAI, ProviderName
from unifai.types import Message, Tool
from basetest import base_test_llms, API_KEYS

# TOOLS AND TOOL CALLABLES
TOOLS = {
    "get_current_weather": 
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string", 
                        "description": "The unit of temperature to return. Infer the unit from the location if not provided.",
                        "enum": ["celsius", "fahrenheit"]
                    },
                },
                "required": ["location", "unit"],
            },
        }
    },
    "return_weather_messages":
    {
        "type": "function",
        "function": {
            "name": "return_weather_messages",
            "description": "Return a message about the current weather for one or more locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "description": "The messages to return about the weather",
                        "items":{
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state, e.g. San Francisco, CA",
                                },
                                "message": {
                                    "type": "string",
                                    "description": "The message for the weather in the location",
                                },
                            },
                            "required": ["location", "message"],
                        },
                    },
                },
                "required": ["messages"],
            }
        }
    },

}

def get_current_weather(location: str, unit: str = "fahrenheit") -> dict:
    """Get the current weather in a given location

    Args:
        location (str): The city and state, e.g. San Francisco, CA
        unit (str): The unit of temperature to return. Infer the unit from the location if not provided.
            enum: ["celsius", "fahrenheit"]
            required: False

    Returns:
        dict: The current weather in the location
            condition (str): The weather condition, e.g. "sunny", "cloudy", "rainy", "hot"
            degrees (float): The temperature in the location
            unit (str): The unit of temperature, e.g. "F", "C" 
    """

    location = location.lower()
    if 'san francisco' in location:
        degrees = 69
        condition = 'sunny'
    elif 'tokyo' in location:
        degrees = 50
        condition = 'cloudy'
    elif 'paris' in location:
        degrees = 40
        condition = 'rainy'
    else:
        degrees = 100
        condition = 'hot'
    if unit == 'celsius':
        degrees = (degrees - 32) * 5/9
        unit = 'C'
    else:
        unit = 'F'
    return {'condition': condition, 'degrees': degrees, 'unit': unit}












@base_test_llms
def test_chat_simple(provider: ProviderName, init_kwargs: dict):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])
    chat = ai.chat(
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        provider=provider,
    )
    messages = chat.messages
    assert messages
    assert isinstance(messages, list)

    for message in messages:
        assert isinstance(message, Message)
        assert message.content
        print(f'{message.role}: {message.content}')

        if message.role == "assistant":
            assert message.response_info
            assert isinstance(message.response_info.model, str)
            assert message.response_info.done_reason == "stop"
            usage = message.response_info.usage
            assert usage
            assert isinstance(usage.input_tokens, int)
            assert isinstance(usage.output_tokens, int)
            assert usage.total_tokens == usage.input_tokens + usage.output_tokens


    print()



@base_test_llms
@pytest.mark.parametrize("messages, tools, tool_callables", [
    (
        [
            {"role": "system", "content": "Your role is use the available tools to answer questions like a cartoon Pirate"},            
            {"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris? Respond in Fahrenheit."},
        ],
        [
            TOOLS["get_current_weather"]
        ],
        {
            "get_current_weather": get_current_weather
        }
    ),

])
def test_chat_tools_simple(
    provider: ProviderName, 
    init_kwargs: dict,
    messages: list,
    tools: list,
    tool_callables: dict
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])

    chat = ai.chat(
        messages=messages,
        provider=provider,
        tools=tools,
        tool_callables=tool_callables,
    )
    messages = chat.messages
    assert messages
    assert isinstance(messages, list)

    for message in messages:
        print(f'{message.role}:\n{message.content or message.tool_calls}\n')
        assert isinstance(message, Message)
        assert message.content or message.tool_calls
    print()
    


@base_test_llms
@pytest.mark.parametrize("messages, tools, tool_callables", [
    (
        [
            {"role": "system", "content": "Your role is use the available tools to answer questions like a cartoon Pirate"},            
            {"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris? Respond in Fahrenheit."},
        ],
        [
            TOOLS["get_current_weather"]
        ],
        {
            "get_current_weather": get_current_weather
        }
    ),
])
def test_chat_return_on(
    provider: ProviderName, 
    init_kwargs: dict,
    messages: list,
    tools: list,
    tool_callables: dict, 
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])


    return_ons = ["content"]
    if tool_names := [tool["function"]["name"] for tool in tools]:
        return_ons.append("message")
        return_ons.append("tool_call")
        return_ons.append(tool_names[0])
        return_ons.append(tool_names)
    

    for return_on in return_ons:
        chat = ai.chat(
            messages=messages,
            provider=provider,
            tools=tools,
            return_on=return_on,
            tool_callables=tool_callables,
        )
        new_messages = chat.messages
        assert new_messages
        last_message = new_messages[-1]
        assert isinstance(last_message, Message)

        if return_on == "content":
            assert last_message.content
            assert not last_message.tool_calls

        elif return_on == "message":
            assert last_message.content or last_message.tool_calls

        elif return_on == "tool_call":
            assert last_message.tool_calls
            # assert not last_message.content

        elif tool_names and return_on == tool_names[0]:
            assert last_message.tool_calls
            # assert not last_message.content
            assert last_message.tool_calls[0].tool_name == tool_names[0]

        elif tool_names and return_on == tool_names:
            assert last_message.tool_calls
            # assert not last_message.content
            assert last_message.tool_calls[0].tool_name in tool_names            

        for message in new_messages:
            print(f'\n{message.role}:\n{message.content or message.tool_calls}\n')            
        print()




@base_test_llms
@pytest.mark.parametrize("messages, tools, tool_callables, tool_choice", [
    (
        [
            {"role": "system", "content": "Your role is use the available tools to answer questions like a cartoon Pirate"},            
            {"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris? Respond in Fahrenheit."},
        ],
        [
            TOOLS["get_current_weather"]
        ],
        {
            "get_current_weather": get_current_weather
        }, 
        "get_current_weather"
    ),
])
def test_chat_enforce_tool_choice(
    provider: ProviderName, 
    init_kwargs: dict,
    messages: list,
    tools: list,
    tool_callables: dict, 
    tool_choice: str
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])


    for _ in range(1):
        chat = ai.chat(
            messages=messages,
            provider=provider,
            tools=tools,
            tool_choice=tool_choice,
            tool_callables=tool_callables,
            return_on="message",
            enforce_tool_choice=True,
        )
        new_messages = chat.messages
        assert new_messages
        assert isinstance(new_messages, list)

        last_message = new_messages[-1]
        assert isinstance(last_message, Message)

        if tool_choice == 'auto':
            assert last_message.content or last_message.tool_calls
        elif tool_choice == 'required':
            assert last_message.tool_calls
            assert not last_message.content
        elif tool_choice == 'none':
            assert last_message.content
            assert not last_message.tool_calls
        else:
            assert last_message.tool_calls
            called_tools = [tool_call.tool_name for tool_call in last_message.tool_calls]
            assert tool_choice in called_tools


        for message in new_messages:
            print(f'\n{message.role}:\n{message.content or message.tool_calls}\n')            
    print()


@base_test_llms
@pytest.mark.parametrize("messages, tools, tool_callables, tool_choice", [
    (
        [
            {"role": "system", "content": "Your role is use the available tools to answer questions like a cartoon Pirate"},            
            {"role": "user", "content": "What's the weather like in San Francisco? Respond in Fahrenheit."},
        ],
        [
            TOOLS["get_current_weather"], TOOLS["return_weather_messages"]
        ],
        {
            "get_current_weather": get_current_weather
        }, 
        ["get_current_weather", "return_weather_messages"]
    ),
])
def test_chat_enforce_tool_choice_sequence(
    # ai: UnifAIClient, 
    provider: ProviderName, 
    init_kwargs: dict,
    messages: list,
    tools: list,
    tool_callables: dict, 
    tool_choice: list[str]
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])

    for _ in range(1):
        chat = ai.chat(
            messages=messages,
            provider=provider,
            tools=tools,
            tool_choice=tool_choice,
            tool_callables=tool_callables,
            return_on=tool_choice[-1],
            enforce_tool_choice=True,
        )
        new_messages = chat.messages
        assert new_messages
        assert isinstance(new_messages, list)

        last_message = new_messages[-1]
        assert isinstance(last_message, Message)

        if tool_choice == 'auto':
            assert last_message.content or last_message.tool_calls
        elif tool_choice == 'required':
            assert last_message.tool_calls
            assert not last_message.content
        elif tool_choice == 'none':
            assert last_message.content
            assert not last_message.tool_calls
        else:
            assert last_message.tool_calls
            called_tools = [tool_call.tool_name for tool_call in last_message.tool_calls]
            assert tool_choice[-1] in called_tools

        input_tokens = 0
        output_tokens = 0
        for message in new_messages + chat.deleted_messages:
            if message.response_info and message.response_info.usage:
                usage = message.response_info.usage
                input_tokens += usage.input_tokens
                output_tokens += usage.output_tokens
        
        assert chat.usage.input_tokens == input_tokens
        assert chat.usage.output_tokens == output_tokens
        assert chat.usage.total_tokens == input_tokens + output_tokens

        for message in new_messages:
            print(f'\n{message.role}:\n{message.content or message.tool_calls}\n')            
    print()


@base_test_llms
@pytest.mark.parametrize("system_prompt, message_lists, tools, tool_callables, tool_choice", [
    (
        "Your role is use the available tools to answer questions like a cartoon Pirate",
        [
            [

            ],
            [
                # {"role": "system", "content": "Your role is use the available tools to answer questions like a cartoon Pirate"},            
                {"role": "user", "content": "What's the weather like in San Francisco? Respond in Fahrenheit."},
            ],
            [
                Message(role="user", content="What's the weather like in Tokyo?"),
            ],
        ],
        [
            TOOLS["get_current_weather"], TOOLS["return_weather_messages"]
        ],
        {
            "get_current_weather": get_current_weather
        }, 
        ["get_current_weather", "return_weather_messages"]
    ),
])
def test_chat_send_message(
    # ai: UnifAIClient, 
    provider: ProviderName, 
    init_kwargs: dict,
    system_prompt: str|None,
    message_lists: list[list],
    tools: list,
    tool_callables: dict, 
    tool_choice: list[str]
    ):    

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])
    chat = ai.chat(
        messages=message_lists[0],
        provider=provider,
        system_prompt=system_prompt,
        tools=tools,
        tool_choice=tool_choice,
        tool_callables=tool_callables,
        return_on=tool_choice[-1],
        enforce_tool_choice=True,
    )

    for messages in message_lists[1:]:
        # chat.set_tool_choice(tool_choice)
        last_message = chat.send_message(*messages)
        assert isinstance(last_message, Message)

        print(f'\n{last_message.role}:\n{last_message.content or last_message.tool_calls}\n')

        if tool_choice == 'auto':
            assert last_message.content or last_message.tool_calls
        elif tool_choice == 'required':
            assert last_message.tool_calls
            assert not last_message.content
        elif tool_choice == 'none':
            assert last_message.content
            assert not last_message.tool_calls
        else:
            assert last_message.tool_calls
            called_tools = [tool_call.tool_name for tool_call in last_message.tool_calls]
            assert tool_choice[-1] in called_tools

    input_tokens = 0
    output_tokens = 0
    for message in chat.messages + chat.deleted_messages:
        if message.response_info and message.response_info.usage:
            usage = message.response_info.usage
            input_tokens += usage.input_tokens
            output_tokens += usage.output_tokens
    
    assert chat.usage.input_tokens == input_tokens
    assert chat.usage.output_tokens == output_tokens
    assert chat.usage.total_tokens == input_tokens + output_tokens            

    for message in chat.messages:
        print(f'\n{message.role}:\n{message.content or message.tool_calls}\n')            
    print()


@base_test_llms
@pytest.mark.parametrize("extra_kwargs", [
    {
        "max_tokens": 100,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 420,
        "stop_sequences": ["AI"],
        "temperature": 0.5,
        "top_k": 50,
        "top_p": 0.5
    }
    
    ])
def test_chat_options(
    provider: ProviderName, 
    init_kwargs: dict, 
    extra_kwargs: dict
    ):

    ai = UnifAI(api_keys=API_KEYS, provider_configs=[{"provider": provider, "init_kwargs": init_kwargs}])
    chat = ai.chat(
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        provider=provider,
        **extra_kwargs
    )
    messages = chat.messages
    assert messages
    assert isinstance(messages, list)

    for message in messages:
        assert isinstance(message, Message)
        assert message.content
        print(f'{message.role}: {message.content}')

        if message.role == "assistant":
            assert message.response_info
            assert isinstance(message.response_info.model, str)
            assert message.response_info.done_reason == "stop"
            usage = message.response_info.usage
            assert usage
            assert isinstance(usage.input_tokens, int)
            assert isinstance(usage.output_tokens, int)
            assert usage.total_tokens == usage.input_tokens + usage.output_tokens


    print()    