"""Merge partial SourceData from multiple connectors."""
from backend.schemas.models import SourceData


def merge_source_data(partials: list[SourceData]) -> SourceData:
    merged = SourceData()
    source_ids: list[str] = []
    for p in partials:
        if p.crm:
            merged.crm.extend(p.crm)
        if p.bank:
            merged.bank.extend(p.bank)
        if p.trading:
            merged.trading.extend(p.trading)
        if p.news:
            merged.news.extend(p.news)
        if p.erp.vendors or p.erp.gl_snapshots or p.erp.vendor_payments:
            merged.erp.vendors.extend(p.erp.vendors)
            merged.erp.gl_snapshots.extend(p.erp.gl_snapshots)
            merged.erp.vendor_payments.extend(p.erp.vendor_payments)
        source_ids.extend(p.source_ids)
    merged.source_ids = list(dict.fromkeys(source_ids))
    return merged
