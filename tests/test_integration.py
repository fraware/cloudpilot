from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from cloudpilot.cost_optimizer import get_aws_cost_optimization
from cloudpilot.k8s_autotuner import tune_and_monitor
from cloudpilot.scaling import recommend_scaling


@patch("cloudpilot.k8s_autotuner.self_heal")
@patch("cloudpilot.k8s_autotuner.detect_anomaly")
@patch("cloudpilot.k8s_autotuner.get_prometheus_metrics")
@patch("cloudpilot.k8s_autotuner.tune_deployment")
@patch("cloudpilot.cost_optimizer.boto3.client")
def test_full_workflow_scaling_cost_and_tuning(
    mock_boto_client: MagicMock,
    mock_tune: MagicMock,
    mock_metrics: MagicMock,
    mock_detect: MagicMock,
    mock_heal: MagicMock,
) -> None:
    mock_boto_client.return_value.get_products.return_value = {}
    mock_tune.return_value = "ok"
    mock_metrics.return_value = [50.0, 50.0, 70.0, 100.0]
    mock_detect.return_value = False

    scaling_output = recommend_scaling(80.0, 70.0, 0.8, 100.0, 0.9)
    assert isinstance(scaling_output, str)

    cost_output = get_aws_cost_optimization("m5.large")
    assert isinstance(cost_output, str)

    tuning_output = tune_and_monitor("nonexistent-deployment", namespace="default")
    assert isinstance(tuning_output, str)
    mock_heal.assert_not_called()


@pytest.mark.integration
def test_integration_placeholder() -> None:
    """Opt-in real cluster tests: run with `pytest -m integration`."""
    pytest.skip("No default integration environment; use mocks or set up a cluster.")
