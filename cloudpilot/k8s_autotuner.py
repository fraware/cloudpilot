from __future__ import annotations

import logging

from kubernetes import client, config

from cloudpilot.anomaly_detector import (
    detect_anomaly,
    get_prometheus_metrics,
    self_heal,
)
from cloudpilot.config import load_settings

logger = logging.getLogger(__name__)


def tune_deployment(deployment_name: str, namespace: str = "default") -> str:
    """
    Auto-tune deployment CPU limits (heuristic): reduce limit by 10% if above 500m.
    Respects CLOUDPILOT_K8S_DRY_RUN=1 to log changes without patching.
    """
    settings = load_settings()
    try:
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
                if isinstance(current_cpu, str) and current_cpu.endswith("m"):
                    current_cpu_val = int(current_cpu.rstrip("m"))
                    if current_cpu_val > 500:
                        new_cpu_val = int(current_cpu_val * 0.9)
                        container.resources.limits["cpu"] = f"{new_cpu_val}m"
                        if (
                            container.resources.requests
                            and "cpu" in container.resources.requests
                        ):
                            container.resources.requests["cpu"] = f"{new_cpu_val}m"
                        modified = True
                        logger.info(
                            "Adjusted container '%s' CPU limit from %s to %sm",
                            container.name,
                            current_cpu,
                            new_cpu_val,
                        )

        if not modified:
            return (
                "No adjustments made. Deployment resources are within "
                "desired thresholds."
            )
        if settings.k8s_dry_run:
            return (
                "Dry run: would patch deployment with updated CPU limits "
                "(CLOUDPILOT_K8S_DRY_RUN=1)."
            )
        apps_v1.patch_namespaced_deployment(deployment_name, namespace, deployment)
        return "Deployment tuned successfully."
    except Exception as e:
        return f"Error tuning deployment: {str(e)}"


def tune_and_monitor(deployment_name: str, namespace: str = "default") -> str:
    tune_result = tune_deployment(deployment_name, namespace)
    logger.info("Tuning result: %s", tune_result)

    metrics = get_prometheus_metrics()
    logger.info(
        "Current metrics: CPU: %s, Memory: %s, Request Rate: %s, Latency: %s",
        metrics[0],
        metrics[1],
        metrics[2],
        metrics[3],
    )

    if detect_anomaly(metrics):
        logger.warning("Anomaly detected. Initiating self-healing procedures...")
        heal_result = self_heal(namespace)
        return f"Tuning complete. Anomaly detected and healed: {heal_result}"
    return "Tuning complete. No anomalies detected."
