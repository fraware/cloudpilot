from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from cloudpilot.anomaly_detector import (
    detect_anomaly,
    self_heal,
    train_dummy_isolation_forest,
)


def test_detect_anomaly_normal() -> None:
    feature_vector = [50.0, 50.0, 70.0, 100.0]
    result = detect_anomaly(feature_vector)
    assert isinstance(result, bool)


def test_isolation_forest_training() -> None:
    model = train_dummy_isolation_forest()
    feature_vector = [50.0, 50.0, 70.0, 100.0]
    prediction = model.predict([feature_vector])
    assert prediction[0] in [-1, 1]


def test_self_heal_skipped_without_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLOUDPILOT_SELF_HEAL_CONFIRM", raising=False)
    result = self_heal("default")
    assert "skipped" in result.lower()


def test_self_heal_with_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLOUDPILOT_SELF_HEAL_CONFIRM", "1")
    mock_api = MagicMock()
    mock_pod = MagicMock()
    mock_pod.status.phase = "Pending"
    mock_pod.metadata.name = "bad-pod"
    mock_api.list_namespaced_pod.return_value = MagicMock(items=[mock_pod])
    with (
        patch("cloudpilot.anomaly_detector.config.load_kube_config"),
        patch("cloudpilot.anomaly_detector.client.CoreV1Api") as mock_cls,
    ):
        mock_cls.return_value = mock_api
        result = self_heal("default")
    assert "Restarted pods" in result or "Error" in result
    mock_api.delete_namespaced_pod.assert_called_once()
