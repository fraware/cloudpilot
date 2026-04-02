from __future__ import annotations

import logging
import time

import numpy as np

logger = logging.getLogger(__name__)


def get_intensity_from_pattern(pattern: str, base_intensity: float) -> float:
    pattern = pattern.lower()
    if pattern == "peak":
        return base_intensity * 1.5
    if pattern == "offpeak":
        return base_intensity * 0.7
    return base_intensity


def simulate_workload(
    duration: int, intensity: float, pattern: str = "normal"
) -> list[float]:
    if duration < 0:
        raise ValueError("Duration must be non-negative")
    if intensity < 0:
        raise ValueError("Intensity must be non-negative")

    adjusted_intensity = get_intensity_from_pattern(pattern, intensity)
    logger.info(
        "Simulating workload for %s seconds with intensity: %s req/sec (pattern: %s).",
        duration,
        adjusted_intensity,
        pattern,
    )
    events: list[float] = []

    for second in range(duration):
        num_events = np.random.poisson(adjusted_intensity)
        for _ in range(num_events):
            event_time = second + np.random.random()
            events.append(float(event_time))

    events.sort()
    for event in events:
        logger.info("Simulated request at t = %.2f sec", event)
    return events


def stress_test(
    kubernetes_deployment: str, namespace: str = "default", duration: int = 30
) -> str:
    if duration < 0:
        raise ValueError("Duration must be non-negative")

    logger.info(
        "Starting stress test on deployment '%s' in namespace '%s' for %s seconds.",
        kubernetes_deployment,
        namespace,
        duration,
    )
    start_time = time.time()
    while time.time() - start_time < duration:
        logger.info("Simulating stress: applying CPU/memory load...")
        time.sleep(5)

    logger.info("Stress test on deployment '%s' completed.", kubernetes_deployment)
    return (
        f"Stress test on deployment '{kubernetes_deployment}' completed successfully."
    )
