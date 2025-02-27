import time
import logging
import numpy as np
from sklearn.ensemble import IsolationForest

# Prometheus client for fetching metrics
from prometheus_api_client import PrometheusConnect

# Kubernetes client for self-healing actions
from kubernetes import client, config

# Configure logging
logging.basicConfig(level=logging.INFO)


def train_dummy_isolation_forest():
    """
    Train a dummy IsolationForest model using synthetic data.
    In production, you would train on historical metrics.
    """
    # Simulate training data: 100 samples, 4 features (CPU, Memory, Request Rate, Latency)
    X_train = np.random.rand(100, 4) * 100  # scale values for demonstration
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    return model


# Train the model at module load time (for MVP purposes)
isolation_forest_model = train_dummy_isolation_forest()


def get_prometheus_metrics():
    """
    Fetch metrics from Prometheus.
    For demonstration, this function returns a feature vector:
      [cpu_util, mem_util, request_rate, network_latency]

    Replace the queries with those relevant to your environment.
    """
    try:
        prom = PrometheusConnect(url="http://localhost:9090", disable_ssl=True)

        # Example queries – adjust as needed.
        # Here we assume Prometheus is collecting container CPU and memory usage.
        cpu_query = "avg(rate(container_cpu_usage_seconds_total[1m])) * 100"
        mem_query = "avg(container_memory_usage_bytes) / 1e6"  # in MB

        cpu_data = prom.custom_query(query=cpu_query)
        mem_data = prom.custom_query(query=mem_query)

        # For simplicity, take the first result value or use default if empty.
        cpu_util = float(cpu_data[0]["value"][1]) if cpu_data else 50.0
        mem_util = float(mem_data[0]["value"][1]) if mem_data else 50.0

        # For request rate and latency, we use dummy normalized values.
        request_rate = 70.0  # e.g., average requests per second (or a normalized score)
        network_latency = 100.0  # in milliseconds

        return [cpu_util, mem_util, request_rate, network_latency]
    except Exception as e:
        logging.error(f"Error fetching Prometheus metrics: {e}")
        # Return default/fallback metrics
        return [50.0, 50.0, 70.0, 100.0]


def detect_anomaly(feature_vector, model=None):
    """
    Uses an IsolationForest to detect if the given feature vector is anomalous.

    Args:
        feature_vector (list or np.array): [cpu_util, mem_util, request_rate, network_latency]
        model: Pre-trained IsolationForest model (default uses module-level model).

    Returns:
        bool: True if an anomaly is detected, False otherwise.
    """
    if model is None:
        model = isolation_forest_model
    prediction = model.predict([feature_vector])
    # IsolationForest returns -1 for anomalies, 1 for normal.
    is_anomaly = prediction[0] == -1
    if is_anomaly:
        logging.warning(f"Anomaly detected for metrics: {feature_vector}")
    # Cast to built-in bool to ensure proper type.
    return bool(is_anomaly)


def self_heal(namespace="default"):
    """
    Self-healing mechanism: Restart failing pods in the given namespace.

    This function loads the Kubernetes configuration, identifies pods not in
    the 'Running' phase, and deletes them so that their controllers restart them.

    Returns:
        str: Summary of healing actions taken.
    """
    try:
        config.load_kube_config()
        core_api = client.CoreV1Api()
        pods = core_api.list_namespaced_pod(namespace)
        healed_pods = []
        for pod in pods.items:
            if pod.status.phase != "Running":
                pod_name = pod.metadata.name
                core_api.delete_namespaced_pod(name=pod_name, namespace=namespace)
                healed_pods.append(pod_name)
                logging.info(f"Restarted pod: {pod_name}")
        if healed_pods:
            return f"Restarted pods: {', '.join(healed_pods)}"
        else:
            logging.info("No failing pods found for self-healing.")
            return "No failing pods found. Consider auto-scaling if anomaly persists."
    except Exception as e:
        logging.error(f"Error during self-healing: {e}")
        return f"Error during self-healing: {e}"


def monitor_and_heal(check_interval=60, namespace="default"):
    """
    Continuously monitors system metrics using Prometheus and applies self-healing
    actions if an anomaly is detected. This function can run as a separate process.

    Args:
        check_interval (int): Seconds between metric checks.
        namespace (str): Kubernetes namespace to monitor and heal.
    """
    while True:
        features = get_prometheus_metrics()
        logging.info(
            f"Current metrics: CPU: {features[0]:.2f}, Memory: {features[1]:.2f}, "
            f"Request Rate: {features[2]:.2f}, Latency: {features[3]:.2f}"
        )
        if detect_anomaly(features):
            logging.warning("Initiating self-healing procedures...")
            result = self_heal(namespace)
            logging.info(f"Self-healing result: {result}")
        else:
            logging.info("No anomalies detected.")
        time.sleep(check_interval)


# Example usage:
if __name__ == "__main__":
    # This will run an infinite loop to monitor and heal; for testing, you might set check_interval to a small value.
    monitor_and_heal(check_interval=30)
