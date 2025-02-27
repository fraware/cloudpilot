import pytest
from cloudpilot.scaling import recommend_scaling


def test_recommend_scaling():
    # Example state: cpu=80, mem=70, req=0.8, latency=100, demand=0.9.
    recommendation = recommend_scaling(80.0, 70.0, 0.8, 100.0, 0.9)
    assert isinstance(recommendation, str)
    # Check for one of the valid action strings.
    valid_actions = ["Scale Down", "Maintain", "Scale Up"]
    assert any(action in recommendation for action in valid_actions)
