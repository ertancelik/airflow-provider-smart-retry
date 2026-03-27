from dataclasses import dataclass

@dataclass
class RetryDecision:
    should_retry: bool
    wait_seconds: int
    reason: str
    error_type: str

def build_decision(llm_response: dict) -> RetryDecision:
    return RetryDecision(
        should_retry=llm_response.get("retry", False),
        wait_seconds=llm_response.get("wait_seconds", 0),
        reason=llm_response.get("reason", ""),
        error_type=llm_response.get("error_type", "unknown")
    )