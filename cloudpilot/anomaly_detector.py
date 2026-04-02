from __future__ import annotations

import logging
import threading
import time

import numpy as np
from kubernetes import client, config
from prometheus_api_client import PrometheusConnect
from sklearn.ensemble import IsolationForest

from cloudpilot.config import load_settings

logger = logging.getLogger(__name__)

_model_lock = threading.Lock()
_isolation_forest_model: IsolationForest | None = None


def train_dummy_isolation_forest(random_state: int = 42) -> IsolationForest:
    """Train a dummy IsolationForest on synthetic data (for demos and tests)."""
    rng = np.random.default_rng(random_state)
    x_train = rng.random((100, 4)) * 100
    model = IsolationForest(contamination=0.1, random_state=random_state)
    model.fit(x_train)
    return model


def get_isolation_forest_model() -> IsolationForest:
    """Lazily construct the default IsolationForest (not at import time)."""
    global _isolation_forest_model
    if _isolation_forest_model is None:
        with _model_lock:
            if _isolation_forest_model is None:
                _isolation_forest_model = train_dummy_isolation_forest()
    return _isolation_forest_model


def reset_isolation_forest_model_for_testing() -> None:
    """Clear cached model (tests only)."""
    global _isolation_forest_model
    with _model_lock:
        _isolation_forest_model = None


def get_prometheus_metrics() -> list[float]:
    """
    Fetch metrics from Prometheus into
    [cpu_util, mem_util, request_rate, network_latency].
    """
    settings = load_settings()
    try:
        prom = PrometheusConnect(
            url=settings.prometheus_url,
            disable_ssl=settings.prometheus_disable_ssl,
        )
        cpu_query = "avg(rate(container_cpu_usage_seconds_total[1m])) * 100"
        mem_query = "avg(container_memory_usage_bytes) / 1e6"
        cpu_data = prom.custom_query(query=cpu_query)
        mem_data = prom.custom_query(query=mem_query)
        cpu_util = float(cpu_data[0]["value"][1]) if cpu_data else 50.0
        mem_util = float(mem_data[0]["value"][1]) if mem_data else 50.0
        request_rate = 70.0
        network_latency = 100.0
        return [cpu_util, mem_util, request_rate, network_latency]
    except Exception as e:
        logger.error("Error fetching Prometheus metrics: %s", e)
        return [50.0, 50.0, 70.0, 100.0]


def detect_anomaly(
    feature_vector: list[float] | np.ndarray,
    model: IsolationForest | None = None,
) -> bool:
    if model is None:
        model = get_isolation_forest_model()
    prediction = model.predict([feature_vector])
    is_anomaly = prediction[0] == -1
    if is_anomaly:
        logger.warning("Anomaly detected for metrics: %s", feature_vector)
    return bool(is_anomaly)


def self_heal(namespace: str = "default") -> str:
    """
    Restarts pods not in Running phase by deleting them (controllers recreate).

    Requires CLOUDPILOT_SELF_HEAL_CONFIRM=1 (or true/yes) to perform deletes.
    """
    settings = load_settings()
    if not settings.self_heal_confirm:
        return (
            "Self-heal skipped: set CLOUDPILOT_SELF_HEAL_CONFIRM=1 to allow "
            "deleting non-Running pods."
        )
    try:
        config.load_kube_config()
        core_api = client.CoreV1Api()
        pods = core_api.list_namespaced_pod(namespace)
        healed_pods: list[str] = []
        for pod in pods.items:
            if pod.status.phase != "Running":
                pod_name = pod.metadata.name
                core_api.delete_namespaced_pod(name=pod_name, namespace=namespace)
                healed_pods.append(pod_name)
                logger.info("Restarted pod: %s", pod_name)
        if healed_pods:
            return f"Restarted pods: {', '.join(healed_pods)}"
        logger.info("No failing pods found for self-healing.")
        return "No failing pods found. Consider auto-scaling if anomaly persists."
    except Exception as e:
        logger.error("Error during self-healing: %s", e)
        return f"Error during self-healing: {e}"


def monitor_and_heal(check_interval: int = 60, namespace: str = "default") -> None:
    while True:
        features = get_prometheus_metrics()
        logger.info(
            (
                "Current metrics: CPU: %.2f, Memory: %.2f, "
                "Request Rate: %.2f, Latency: %.2f"
            ),
            features[0],
            features[1],
            features[2],
            features[3],
        )
        if detect_anomaly(features):
            logger.warning("Initiating self-healing procedures...")
            result = self_heal(namespace)
            logger.info("Self-healing result: %s", result)
        else:
            logger.info("No anomalies detected.")
        time.sleep(check_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor_and_heal(check_interval=30)
