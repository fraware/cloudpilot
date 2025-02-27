import pytest
import numpy as np
from cloudpilot.anomaly_detector import detect_anomaly, train_dummy_isolation_forest


def test_detect_anomaly_normal():
    # Use a sample feature vector expected to be normal.
    feature_vector = [50.0, 50.0, 70.0, 100.0]
    result = detect_anomaly(feature_vector)
    # Since the dummy model is random, just check that a boolean is returned.
    assert isinstance(result, bool)


def test_isolation_forest_training():
    model = train_dummy_isolation_forest()
    feature_vector = [50.0, 50.0, 70.0, 100.0]
    prediction = model.predict([feature_vector])
    assert prediction[0] in [-1, 1]
