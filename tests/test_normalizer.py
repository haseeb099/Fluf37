from backend.integration.normalizer import merge_source_data
from backend.schemas.models import SourceData
from backend.utils.synthetic_data import get_demo_bank, get_demo_crm, get_demo_erp


def test_merge_source_data():
    partials = [
        SourceData(crm=get_demo_crm(), source_ids=["crm"]),
        SourceData(bank=get_demo_bank(), source_ids=["bank"]),
        SourceData(erp=get_demo_erp(), source_ids=["erp"]),
    ]
    merged = merge_source_data(partials)
    assert "crm" in merged.source_ids
    assert len(merged.crm) >= 1
    assert len(merged.erp.vendors) >= 1
