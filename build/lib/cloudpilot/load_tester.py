import numpy as np
import time
import logging

# Set up logging for demonstration purposes
logging.basicConfig(level=logging.INFO)


def get_intensity_from_pattern(pattern, base_intensity):
    """
    Adjusts the base intensity based on the given traffic pattern.

    Args:
        pattern (str): Traffic pattern (e.g., 'peak', 'offpeak', 'normal').
        base_intensity (float): Base average rate (requests per second).

    Returns:
        float: Adjusted intensity.
    """
    pattern = pattern.lower()
    if pattern == "peak":
        return base_intensity * 1.5
    elif pattern == "offpeak":
        return base_intensity * 0.7
    else:
        return base_intensity


def simulate_workload(duration, intensity, pattern="normal"):
    """
    Simulates realistic workload patterns using a Poisson process.

    Args:
        duration (int): Duration of the simulation in seconds.
        intensity (float): Base average rate (lambda) for requests per second.
        pattern (str): Traffic pattern modifier (e.g., 'peak', 'offpeak', 'normal').

    Returns:
        list: Sorted list of simulated request timestamps (in seconds).
    """
    if duration < 0:
        raise ValueError("Duration must be non-negative")
    if intensity < 0:
        raise ValueError("Intensity must be non-negative")

    adjusted_intensity = get_intensity_from_pattern(pattern, intensity)
    logging.info(
        f"Simulating workload for {duration} seconds with intensity: {adjusted_intensity} req/sec (pattern: {pattern})."
    )
    events = []

    # For each second, sample the number of events based on a Poisson process.
    for second in range(duration):
        num_events = np.random.poisson(adjusted_intensity)
        for _ in range(num_events):
            # Distribute events randomly within the second.
            event_time = second + np.random.random()
            events.append(event_time)

    events.sort()

    # For demonstration, log each simulated request timestamp.
    for event in events:
        logging.info(f"Simulated request at t = {event:.2f} sec")

    return events


def stress_test(kubernetes_deployment, namespace="default", duration=30):
    """
    Simulates infrastructure stress testing on a Kubernetes deployment.

    This function demonstrates a stress test by logging periodic status updates.
    In production, you might integrate a tool like 'stress-ng' via a sidecar container,
    or execute stress commands in your pods.

    Args:
        kubernetes_deployment (str): The name of the Kubernetes deployment.
        namespace (str): The Kubernetes namespace.
        duration (int): Duration of the stress test in seconds.

    Returns:
        str: A summary of the stress test outcome.
    """
    if duration < 0:
        raise ValueError("Duration must be non-negative")

    logging.info(
        f"Starting stress test on deployment '{kubernetes_deployment}' in namespace '{namespace}' for {duration} seconds."
    )
    start_time = time.time()
    while time.time() - start_time < duration:
        logging.info("Simulating stress: applying CPU/memory load...")
        # In a real scenario, you would trigger actual load generators or use stress tools.
        time.sleep(5)  # Sleep to simulate time between stress events.

    logging.info(f"Stress test on deployment '{kubernetes_deployment}' completed.")
    return (
        f"Stress test on deployment '{kubernetes_deployment}' completed successfully."
    )


# Example usage for testing the module
if __name__ == "__main__":
    # Simulate a 10-second workload with a base intensity of 5 requests/sec during peak traffic.
    simulate_workload(duration=10, intensity=5, pattern="peak")

    # Simulate a stress test on a deployment named 'your-deployment' for 15 seconds.
    result = stress_test(
        kubernetes_deployment="your-deployment", namespace="default", duration=15
    )
    logging.info(result)
