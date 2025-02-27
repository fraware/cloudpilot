import pytest
from cloudpilot.k8s_autotuner import tune_deployment


def test_tune_deployment_invalid():
    # This test uses a non-existent deployment name.
    result = tune_deployment("nonexistent-deployment", namespace="default")
    assert isinstance(result, str)
    # We expect an error message or a message indicating no adjustments were made.
    assert "Error" in result or "No adjustments" in result
