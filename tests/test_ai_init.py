from unittest.mock import MagicMock, patch

import pytest

from openai_service.ai_init import AiInit


def make_ai_init(monkeypatch, mock_client):
    monkeypatch.setenv("OPENAI_KEY", "test-key")
    with patch("openai_service.ai_init.OpenAI", return_value=mock_client):
        return AiInit()


def make_completion(content: str):
    completion = MagicMock()
    completion.choices = [MagicMock(message=MagicMock(content=content))]
    return completion


def test_initialize_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_KEY", raising=False)
    with pytest.raises(ValueError):
        AiInit()


def test_send_request_to_ai_returns_content(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = make_completion("hello")
    ai = make_ai_init(monkeypatch, mock_client)

    result = ai.send_request_to_ai("hi", conversation_history=[])

    assert result == "hello"
    mock_client.chat.completions.create.assert_called_once()


def test_send_request_to_ai_returns_none_on_error(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("boom")
    ai = make_ai_init(monkeypatch, mock_client)

    assert ai.send_request_to_ai("hi", conversation_history=[]) is None


def test_generate_image_returns_url(monkeypatch):
    mock_client = MagicMock()
    image = MagicMock(url="https://example.com/image.png")
    mock_client.images.generate.return_value = MagicMock(data=[image])
    ai = make_ai_init(monkeypatch, mock_client)

    assert ai.generate_image("a cat") == "https://example.com/image.png"


def test_generate_image_returns_none_on_error(monkeypatch):
    mock_client = MagicMock()
    mock_client.images.generate.side_effect = RuntimeError("boom")
    ai = make_ai_init(monkeypatch, mock_client)

    assert ai.generate_image("a cat") is None


def test_greet_user_includes_user_name(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = make_completion("Szia Alex!")
    ai = make_ai_init(monkeypatch, mock_client)

    result = ai.greet_user("Alex")

    assert result == "Szia Alex!"
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert any("Alex" in m["content"] for m in messages)
