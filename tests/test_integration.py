import pytest
from cloudpilot.scaling import recommend_scaling
from cloudpilot.cost_optimizer import get_aws_cost_optimization
from cloudpilot.k8s_autotuner import tune_and_monitor


def test_full_workflow_scaling_cost_and_tuning():
    scaling_output = recommend_scaling(80.0, 70.0, 0.8, 100.0, 0.9)
    assert isinstance(scaling_output, str)

    cost_output = get_aws_cost_optimization("m5.large")
    assert isinstance(cost_output, str)

    tuning_output = tune_and_monitor("nonexistent-deployment", namespace="default")
    assert isinstance(tuning_output, str)
