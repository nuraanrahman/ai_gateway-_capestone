"""Token cost estimation. Prices in USD per 1M tokens."""

COST_TABLE: dict[str, dict[str, float]] = {
    # OpenAI
    "gpt-4o":            {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":       {"input": 0.15,  "output": 0.60},
    "gpt-4-turbo":       {"input": 10.00, "output": 30.00},
    "o1":                {"input": 15.00, "output": 60.00},
    "o3-mini":           {"input": 1.10,  "output": 4.40},
    # Anthropic
    "claude-opus-4-7":          {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6":        {"input": 3.00,  "output": 15.00},
    "claude-haiku-4-5":         {"input": 0.80,  "output": 4.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
}

_DEFAULT_COST = {"input": 1.00, "output": 5.00}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Return estimated cost in USD."""
    # Fuzzy match: find the longest key that is a prefix of the model string
    rates = _DEFAULT_COST
    for key, r in COST_TABLE.items():
        if model.lower().startswith(key.lower()):
            rates = r
            break
    return (prompt_tokens * rates["input"] + completion_tokens * rates["output"]) / 1_000_000
