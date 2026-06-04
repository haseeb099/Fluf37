"""Adversarial Red Team agent."""
import json
from pathlib import Path
from typing import AsyncIterator
from uuid import uuid4

from backend.agents.base import AgentState, BaseAgent
from backend.schemas.models import AgentEvent, Attack, AttackOutput, BlindSpotOutput


class AdversarialRedTeam(BaseAgent):
    agent_id = "adversarial"

    async def run(self, payload: BlindSpotOutput) -> AsyncIterator[AgentEvent]:
        self._set_state(AgentState.RUNNING)
        yield self._emit("AGENT_START", {})
        attacks = []
        library = self._load_library()

        for bs in payload.blind_spots:
            async for event in self._stream_llm(
                f"Generate attack for blind spot: {bs.title}",
                system="You are a red team analyst exploiting detection gaps.",
                temperature=0.7,
            ):
                yield event
            atk = self._build_attack(bs, library)
            attacks.append(atk)

        output = AttackOutput(attacks=attacks)
        yield self._emit("AGENT_COMPLETE", output.model_dump())

    def _load_library(self) -> dict:
        path = Path("data/attack_library/v1.json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"version": "v1", "attacks": []}

    def _build_attack(self, bs, library: dict) -> Attack:
        lib_atk = library.get("attacks", [{}])[0]
        type_map = {
            "Circular": "fraud",
            "Shareholder": "concentration",
            "Order Book": "spoofing",
            "Cash Flow": "timing",
            "Vendor": "concentration",
            "Shell": "fraud",
        }
        atk_type = "fraud"
        for k, v in type_map.items():
            if k in bs.title:
                atk_type = v
                break
        return Attack(
            id=f"atk_{uuid4().hex[:6]}",
            name=f"Exploit: {bs.title[:40]}",
            target_blind_spot_id=bs.id,
            attack_type=atk_type,  # type: ignore
            success_probability=min(0.95, bs.confidence + 0.05),
            steps=[
                f"Identify gap: {bs.description[:80]}",
                "Execute multi-step exploitation path",
                "Evade current 2-entity detection rules",
            ],
            current_rule_exploited="Standard threshold rules only",
            proposed_defense=lib_atk.get("proposed_defense", "Add cross-source monitoring rule"),
            library_version=library.get("version", "v1"),
        )
