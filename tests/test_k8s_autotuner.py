from __future__ import annotations

from unittest.mock import MagicMock, patch

from cloudpilot.k8s_autotuner import tune_and_monitor, tune_deployment


@patch("cloudpilot.k8s_autotuner.client.AppsV1Api")
@patch("cloudpilot.k8s_autotuner.config.load_kube_config")
def test_tune_deployment_invalid(
    mock_load_config: MagicMock, mock_api_cls: MagicMock
) -> None:
    mock_api = MagicMock()
    mock_api_cls.return_value = mock_api
    mock_api.read_namespaced_deployment.side_effect = Exception("not found")
    result = tune_deployment("nonexistent-deployment", namespace="default")
    assert isinstance(result, str)
    assert "Error" in result


@patch("cloudpilot.k8s_autotuner.self_heal")
@patch("cloudpilot.k8s_autotuner.detect_anomaly")
@patch("cloudpilot.k8s_autotuner.get_prometheus_metrics")
@patch("cloudpilot.k8s_autotuner.tune_deployment")
def test_tune_and_monitor_no_anomaly(
    mock_tune: MagicMock,
    mock_metrics: MagicMock,
    mock_detect: MagicMock,
    mock_heal: MagicMock,
) -> None:
    mock_tune.return_value = "Deployment tuned successfully."
    mock_metrics.return_value = [50.0, 50.0, 70.0, 100.0]
    mock_detect.return_value = False
    result = tune_and_monitor("my-deployment", namespace="default")
    assert "No anomalies detected" in result
    mock_heal.assert_not_called()
