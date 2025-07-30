import json

import httpx
import llm
import pytest
from pytest_httpx import HTTPXMock

from llm_grok import DEFAULT_MODEL, Grok, GrokError


@pytest.fixture(autouse=True)
def ignore_warnings():
    """Ignoriere bekannte Warnungen."""
    warnings = [
        # Pydantic Warnung
        "Support for class-based `config` is deprecated",
        # Datetime Warnung
        "datetime.datetime.utcnow() is deprecated",
    ]
    for warning in warnings:
        pytest.mark.filterwarnings(f"ignore:{warning}")


@pytest.fixture
def model():
    return Grok(DEFAULT_MODEL)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Mock environment variables and API key for testing"""
    monkeypatch.setenv("XAI_API_KEY", "xai-test-key-mock")
    monkeypatch.setattr("llm_grok.Grok.get_key", lambda self, key=None: "xai-test-key-mock")


@pytest.fixture
def mock_response():
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Test response"},
                "finish_reason": "stop",
            }
        ],
    }


def test_model_initialization(model):
    assert model.model_id == DEFAULT_MODEL
    assert model.can_stream == True
    assert model.needs_key == "grok"
    assert model.key_env_var == "XAI_API_KEY"


def test_build_messages_with_system_prompt(model):
    prompt = llm.Prompt(
        model=model, prompt="Test message", system="Custom system message"
    )
    messages = model.build_messages(prompt, None)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "Custom system message"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Test message"


def test_build_messages_without_system_prompt(model):
    prompt = llm.Prompt(model=model, prompt="Test message")
    messages = model.build_messages(prompt, None)

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test message"


def test_build_messages_with_conversation(model, httpx_mock: HTTPXMock):
    # Mock the expected request content
    expected_request = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": "Previous message"},
        ],
        "stream": False,
        "temperature": 0.0,
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.x.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer xai-test-key-mock"},
        json={
            "id": "chatcmpl-123",
            "choices": [
                {"message": {"role": "assistant", "content": "Previous response"}}
            ],
        },
        match_json=expected_request,
    )

    conversation = llm.Conversation(model=model)
    prev_prompt = llm.Prompt(model=model, prompt="Previous message")

    prev_response = llm.Response(model=model, prompt=prev_prompt, stream=False)
    prev_response._response_json = {
        "choices": [{"message": {"role": "assistant", "content": "Previous response"}}]
    }

    conversation.responses.append(prev_response)

    prompt = llm.Prompt(model=model, prompt="New message")
    messages = model.build_messages(prompt, conversation)

    assert len(messages) == 3
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Previous message"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Previous response"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "New message"


def test_non_streaming_request(model, mock_response, httpx_mock: HTTPXMock):
    expected_request = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": "Test message"},
        ],
        "stream": False,
        "temperature": 0.0,
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.x.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer xai-test-key-mock"},
        json=mock_response,
        headers={"Content-Type": "application/json"},
        match_json=expected_request,
    )

    response = model.prompt("Test message", stream=False)
    result = response.text()
    assert result == "Test response"

    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "Bearer xai-test-key-mock"
    assert json.loads(request.content) == expected_request


def test_streaming_request(model, httpx_mock: HTTPXMock):
    expected_request = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": "Test message"},
        ],
        "stream": True,
        "temperature": 0.0,
    }

    def response_callback(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer xai-test-key-mock"
        assert json.loads(request.content) == expected_request
        stream_content = [
            'data: {"id":"chatcmpl-123","choices":[{"delta":{"role":"assistant"}}]}\n\n',
            'data: {"id":"chatcmpl-123","choices":[{"delta":{"content":"Test"}}]}\n\n',
            'data: {"id":"chatcmpl-123","choices":[{"delta":{"content":" response"}}]}\n\n',
            "data: [DONE]\n\n",
        ]
        return httpx.Response(
            status_code=200,
            headers={"content-type": "text/event-stream"},
            content="".join(stream_content).encode(),
        )

    httpx_mock.add_callback(
        response_callback,
        method="POST",
        url="https://api.x.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer xai-test-key-mock"},
        match_json=expected_request,
    )

    response = model.prompt("Test message", stream=True)
    chunks = list(response)
    assert "".join(chunks) == "Test response"


def test_temperature_option(model, mock_response, httpx_mock: HTTPXMock):
    expected_request = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": "Test message"},
        ],
        "stream": False,
        "temperature": 0.8,
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.x.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer xai-test-key-mock"},
        json=mock_response,
        headers={"Content-Type": "application/json"},
        match_json=expected_request,
    )

    # Create prompt and pass temperature directly
    response = model.prompt("Test message", stream=False, temperature=0.8)
    result = response.text()
    assert result == "Test response"

    request = httpx_mock.get_requests()[0]
    assert json.loads(request.content) == expected_request


def test_max_tokens_option(model, mock_response, httpx_mock: HTTPXMock):
    expected_request = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": "Test message"},
        ],
        "stream": False,
        "temperature": 0.0,
        "max_completion_tokens": 100,
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.x.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer xai-test-key-mock"},
        json=mock_response,
        headers={"Content-Type": "application/json"},
        match_json=expected_request,
    )

    # Create prompt and pass max_tokens directly
    response = model.prompt("Test message", stream=False, max_completion_tokens=100)
    result = response.text()
    assert result == "Test response"

    request = httpx_mock.get_requests()[0]
    assert json.loads(request.content) == expected_request


def test_api_error(model, httpx_mock: HTTPXMock):
    expected_request = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": "Test message"},
        ],
        "stream": False,
        "temperature": 0.0,
    }

    error_response = {
        "error": {
            "message": "Invalid request",
            "type": "invalid_request_error",
            "code": "invalid_api_key",
        }
    }

    httpx_mock.add_response(
        method="POST",
        url="https://api.x.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer xai-test-key-mock"},
        status_code=400,
        json=error_response,
        headers={"Content-Type": "application/json"},
        match_json=expected_request,
    )

    with pytest.raises(GrokError) as exc_info:
        response = model.prompt("Test message", stream=False)
        response.text()  # Trigger the API call

    # The error message comes directly from the API response
    assert str(exc_info.value) == error_response["error"]["message"]


def test_stream_parsing_error(model, httpx_mock: HTTPXMock):
    expected_request = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "user", "content": "Test message"},
        ],
        "stream": True,
        "temperature": 0.0,
    }

    def error_callback(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer xai-test-key-mock"
        assert json.loads(request.content) == expected_request
        return httpx.Response(
            status_code=200,
            headers={"content-type": "text/event-stream"},
            content=b"data: {invalid json}\n\n",
        )

    httpx_mock.add_callback(
        error_callback,
        method="POST",
        url="https://api.x.ai/v1/chat/completions",
        match_headers={"Authorization": "Bearer xai-test-key-mock"},
        match_json=expected_request,
    )

    response = model.prompt("Test message", stream=True)
    chunks = list(response)
    assert chunks == []
