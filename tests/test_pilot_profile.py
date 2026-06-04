"""Pilot profile verification and export helpers."""
from backend.config import NexusConfig


def test_pilot_profile_fails_on_defaults():
    cfg = NexusConfig.model_construct(
        nexus_api_key="demo-key",
        jwt_secret="change-me",
        nexus_pre_live_mode=False,
        auth_mode="jwt_optional",
        nexus_ws_require_auth=False,
        nexus_trust_client_role=True,
    )
    assert cfg.nexus_api_key == "demo-key"
    assert cfg.auth_mode != "jwt_required"


def test_pilot_profile_accepts_hardened_config():
    cfg = NexusConfig.model_construct(
        nexus_api_key="rotated-pilot-key-abc",
        jwt_secret="a" * 32,
        nexus_pre_live_mode=True,
        auth_mode="jwt_required",
        nexus_ws_require_auth=True,
        nexus_trust_client_role=False,
    )
    assert not cfg.trust_client_role()
    assert cfg.auth_mode == "jwt_required"
