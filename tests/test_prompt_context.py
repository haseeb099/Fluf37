"""Tests for LLM prompt context builders."""
from backend.schemas.models import BlindSpot, BlindSpotOutput, CRMDeal, SourceData
from backend.utils.prompt_context import silent_finder_prompt, summarize_source_data


def test_summarize_source_data_includes_deals():
    data = SourceData(
        crm=[
            CRMDeal(
                id="d1",
                company="Acme Corp",
                deal_value=450000,
                payment_terms_days=90,
                contact_name="James Chen",
            )
        ]
    )
    text = summarize_source_data(data)
    assert "Acme Corp" in text
    assert "450000" in text or "450000.0" in text


def test_silent_finder_prompt_includes_blind_spots():
    data = SourceData()
    spots = [
        BlindSpot(
            id="bs1",
            title="Cash Flow Timing Mismatch",
            description="90-day terms vs 30-day gap",
            severity="high",
            confidence=0.88,
        )
    ]
    prompt = silent_finder_prompt(data, spots)
    assert "Cash Flow Timing Mismatch" in prompt
    assert "blind spots" in prompt.lower()
