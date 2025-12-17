import pytest
import requests
import asyncio
import main


def test_ai_endpoint_retries_then_succeeds(monkeypatch):
    # Ensure an API key is present for the endpoint
    main.GROQ_API_KEY = "test-key"

    calls = {"n": 0}

    def mock_post(url, json, headers, timeout):
        calls["n"] += 1
        if calls["n"] < 3:
            class R:
                status_code = 429
                text = "rate limit"
                def json(self):
                    return {"error": "rate limit"}
            return R()
        else:
            class R2:
                status_code = 200
                text = '{"output": ["ai response"]}'
                def json(self):
                    return {"output": ["ai response"]}
            return R2()

    monkeypatch.setattr("requests.post", mock_post)

    # Call the async endpoint via asyncio
    response = asyncio.get_event_loop().run_until_complete(
        main.ai_endpoint(main.PromptRequest(prompt="Hello world"))
    )

    assert isinstance(response, dict)
    assert "response" in response
    assert "ai response" in response["response"]


def test_ai_endpoint_missing_key_raises():
    # Remove API key and ensure we get an HTTPException when calling the endpoint
    main.GROQ_API_KEY = None
    with pytest.raises(Exception):
        asyncio.get_event_loop().run_until_complete(
            main.ai_endpoint(main.PromptRequest(prompt="No key"))
        )
