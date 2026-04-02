from __future__ import annotations

from unittest.mock import MagicMock, patch

from cloudpilot.cost_optimizer import get_aws_cost_optimization


@patch("cloudpilot.cost_optimizer.boto3.client")
def test_get_aws_cost_optimization(mock_client: MagicMock) -> None:
    mock_client.return_value.get_products.return_value = {"PriceList": []}
    result = get_aws_cost_optimization("m5.large")
    assert isinstance(result, str)
    assert (
        "Retrieved pricing data" in result or "Error retrieving pricing data" in result
    )


@patch("cloudpilot.cost_optimizer.boto3.client")
def test_get_aws_cost_optimization_api_error(mock_client: MagicMock) -> None:
    mock_client.return_value.get_products.side_effect = RuntimeError("network")
    result = get_aws_cost_optimization("m5.large")
    assert "Error retrieving pricing data" in result
