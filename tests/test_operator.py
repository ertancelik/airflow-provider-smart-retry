import sys
from unittest.mock import MagicMock, patch

# Airflow'u mock'la — yerel kurulum gerekmez
airflow_mock = MagicMock()
airflow_mock.sdk.BaseOperator = object
sys.modules['airflow'] = airflow_mock
sys.modules['airflow.sdk'] = airflow_mock.sdk

import pytest
from smart_retry.strategies import build_decision, RetryDecision
from smart_retry.llm_client import OllamaClient


# --- Strategy Tests ---

def test_build_decision_retry_true():
    response = {"error_type": "network", "retry": True, "wait_seconds": 0, "reason": "timeout"}
    decision = build_decision(response)
    assert decision.should_retry is True
    assert decision.wait_seconds == 0
    assert decision.error_type == "network"


def test_build_decision_no_retry():
    response = {"error_type": "auth", "retry": False, "wait_seconds": 0, "reason": "invalid key"}
    decision = build_decision(response)
    assert decision.should_retry is False


def test_build_decision_rate_limit():
    response = {"error_type": "rate_limit", "retry": True, "wait_seconds": 60, "reason": "quota exceeded"}
    decision = build_decision(response)
    assert decision.should_retry is True
    assert decision.wait_seconds == 60


# --- LLM Client Tests ---

def test_ollama_client_classify_error():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": '{"error_type": "rate_limit", "retry": true, "wait_seconds": 60, "reason": "quota"}'
    }
    mock_response.raise_for_status = MagicMock()

    with patch("requests.post", return_value=mock_response):
        client = OllamaClient()
        result = client.classify_error("429 Too Many Requests")
        assert result["error_type"] == "rate_limit"
        assert result["retry"] is True
        assert result["wait_seconds"] == 60


def test_ollama_client_invalid_json_raises():
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "I cannot classify this."}
    mock_response.raise_for_status = MagicMock()

    with patch("requests.post", return_value=mock_response):
        client = OllamaClient()
        with pytest.raises(Exception):
            client.classify_error("some error")