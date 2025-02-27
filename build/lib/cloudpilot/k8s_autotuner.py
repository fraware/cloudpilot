from kubernetes import client, config
from cloudpilot.anomaly_detector import (
    detect_anomaly,
    get_prometheus_metrics,
    self_heal,
)


def tune_deployment(deployment_name, namespace="default"):
    """
    Connects to a Kubernetes cluster and applies auto-tuning recommendations
    to a deployment's resource limits based on heuristics.

    For MVP:
      - If a container's CPU limit is above 500m, reduce it by 10%.
      - Apply changes by patching the deployment.
    """
    try:
        # Load kubeconfig (assumes you have a valid kubeconfig in ~/.kube/config)
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()
        deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)

        modified = False
        for container in deployment.spec.template.spec.containers:
            if (
                container.resources
                and container.resources.limits
                and "cpu" in container.resources.limits
            ):
                current_cpu = container.resources.limits["cpu"]
                # Handle CPU value in millicores (e.g., "600m")
                if isinstance(current_cpu, str) and current_cpu.endswith("m"):
                    current_cpu_val = int(current_cpu.rstrip("m"))
                    if current_cpu_val > 500:
                        new_cpu_val = int(current_cpu_val * 0.9)
                        container.resources.limits["cpu"] = f"{new_cpu_val}m"
                        # Optionally adjust requests as well
                        if (
                            container.resources.requests
                            and "cpu" in container.resources.requests
                        ):
                            container.resources.requests["cpu"] = f"{new_cpu_val}m"
                        modified = True
                        print(
                            f"Adjusted container '{container.name}' CPU limit from {current_cpu} to {new_cpu_val}m"
                        )

        if modified:
            # Patch the deployment with updated resource settings
            apps_v1.patch_namespaced_deployment(deployment_name, namespace, deployment)
            return "Deployment tuned successfully."
        else:
            return "No adjustments made. Deployment resources are within desired thresholds."
    except Exception as e:
        return f"Error tuning deployment: {str(e)}"


def tune_and_monitor(deployment_name, namespace="default"):
    """
    Extends tune_deployment by integrating anomaly detection and self-healing.

    1. Tunes the deployment using heuristics.
    2. Fetches current metrics via Prometheus.
    3. Detects anomalies using an IsolationForest-based model.
    4. If an anomaly is detected, triggers self-healing procedures.

    Returns a summary of actions taken.
    """
    # Perform the auto-tuning
    tune_result = tune_deployment(deployment_name, namespace)
    print("Tuning Result:", tune_result)

    # Fetch current metrics and detect anomalies
    metrics = get_prometheus_metrics()
    print(
        f"Current Metrics: CPU: {metrics[0]}, Memory: {metrics[1]}, "
        f"Request Rate: {metrics[2]}, Latency: {metrics[3]}"
    )

    if detect_anomaly(metrics):
        print("Anomaly detected. Initiating self-healing procedures...")
        heal_result = self_heal(namespace)
        return f"Tuning complete. Anomaly detected and healed: {heal_result}"
    else:
        return "Tuning complete. No anomalies detected."
