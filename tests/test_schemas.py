from backend.schemas.models import SignalWeights
from backend.utils.synthetic_data import get_demo_source_data


def test_signal_weights_sum():
    w = SignalWeights()
    assert abs(w.technical + w.fundamental + w.news + w.forcing - 1.0) < 0.01


def test_source_data_loads():
    data = get_demo_source_data()
    assert len(data.crm) >= 1
    assert len(data.bank) >= 1
    assert len(data.erp.vendors) >= 1
