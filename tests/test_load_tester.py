import pytest
from cloudpilot.load_tester import simulate_workload, stress_test


def test_simulate_workload_peak():
    # Simulate a 5-second workload with base intensity 2 and 'peak' pattern.
    events = simulate_workload(5, 2, pattern="peak")
    assert isinstance(events, list)
    assert all(isinstance(e, float) for e in events)
    assert events == sorted(events)
    assert len(events) > 0


def test_stress_test():
    result = stress_test("dummy-deployment", namespace="default", duration=1)
    assert isinstance(result, str)
    assert "completed" in result.lower()


def test_simulate_workload_negative_duration():
    with pytest.raises(ValueError):
        simulate_workload(-5, 2, pattern="normal")


def test_simulate_workload_negative_intensity():
    with pytest.raises(ValueError):
        simulate_workload(5, -2, pattern="normal")
