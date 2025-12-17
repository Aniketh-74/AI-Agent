import pytest
import types
import requests
import main


def test_groq_call_retries_then_succeeds(monkeypatch):
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
                text = '{"output": ["ok"]}'
                def json(self):
                    return {"output": ["ok"]}
            return R2()

    monkeypatch.setattr("requests.post", mock_post)

    out = main.groq_call("hello world")
    assert out is not None
    assert "ok" in out


def test_groq_call_exhausts_retries(monkeypatch):
    def always_fail(url, json, headers, timeout):
        raise requests.RequestException("network down")

    monkeypatch.setattr("requests.post", always_fail)

    with pytest.raises(requests.RequestException):
        main.groq_call("hello world")
