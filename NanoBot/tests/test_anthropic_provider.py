from nanobot.providers.anthropic_provider import AnthropicProvider


def test_anthropic_provider_converts_openai_messages_and_tools():
    provider = AnthropicProvider(api_key="k", api_base="https://example.com", default_model="glm-5")
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "hello"},
        {
            "role": "assistant",
            "content": "working",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "search", "arguments": '{"q":"hi"}'},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "name": "search", "content": "result"},
    ]

    system, converted = provider._convert_messages(messages)
    tools = provider._convert_tools(
        [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search stuff",
                    "parameters": {"type": "object", "properties": {"q": {"type": "string"}}},
                },
            }
        ]
    )

    assert system == "sys"
    assert converted[0] == {"role": "user", "content": [{"type": "text", "text": "hello"}]}
    assert converted[1]["role"] == "assistant"
    assert converted[1]["content"][1]["type"] == "tool_use"
    assert converted[1]["content"][1]["input"] == {"q": "hi"}
    assert converted[2] == {
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": "result"}],
    }
    assert tools == [
        {
            "name": "search",
            "description": "Search stuff",
            "input_schema": {"type": "object", "properties": {"q": {"type": "string"}}},
        }
    ]


def test_anthropic_provider_parses_text_and_tool_use_response():
    response = {
        "content": [
            {"type": "text", "text": "Need a tool."},
            {"type": "tool_use", "id": "call_2", "name": "search", "input": {"q": "weather"}},
        ],
        "stop_reason": "tool_use",
        "usage": {"input_tokens": 12, "output_tokens": 5},
    }

    parsed = AnthropicProvider._parse(response)

    assert parsed.content == "Need a tool."
    assert parsed.finish_reason == "tool_use"
    assert parsed.tool_calls[0].id == "call_2"
    assert parsed.tool_calls[0].name == "search"
    assert parsed.tool_calls[0].arguments == {"q": "weather"}
    assert parsed.usage == {"prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17}
