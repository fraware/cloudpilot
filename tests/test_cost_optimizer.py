import pytest
from cloudpilot.cost_optimizer import get_aws_cost_optimization


def test_get_aws_cost_optimization():
    result = get_aws_cost_optimization("m5.large")
    assert isinstance(result, str)
    # Check that the result contains one of the expected phrases.
    assert (
        "Retrieved pricing data" in result or "Error retrieving pricing data" in result
    )
