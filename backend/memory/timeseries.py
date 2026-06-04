"""SQLite time-series memory."""
import json
from pathlib import Path

import aiosqlite

from backend.config import NexusConfig
from backend.schemas.models import DecisionOutput, EvolutionCycle


class TimeSeriesMemory:
    def __init__(self, config: NexusConfig):
        self.path = Path(config.sqlite_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def _db(self):
        db = await aiosqlite.connect(str(self.path))
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id TEXT PRIMARY KEY, agent_id TEXT, timestamp TEXT,
                tokens_used INTEGER, latency_ms INTEGER, success INTEGER, model TEXT
            );
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY, type TEXT, recommendation TEXT, confidence REAL,
                signal_breakdown TEXT, outcome TEXT, created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS evolution_cycles (
                id TEXT PRIMARY KEY, weight_changes TEXT, new_rules TEXT,
                approved INTEGER, created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS connector_sync (
                id TEXT PRIMARY KEY, source_type TEXT, tenant_id TEXT,
                success INTEGER, records INTEGER, timestamp TEXT
            );
        """)
        await db.commit()
        return db

    async def record_agent_run(self, agent_id: str, tokens: int, latency_ms: int, success: bool, model: str) -> None:
        import uuid
        from datetime import datetime
        db = await self._db()
        await db.execute(
            "INSERT INTO agent_metrics VALUES (?,?,?,?,?,?,?)",
            (uuid.uuid4().hex, agent_id, datetime.utcnow().isoformat(), tokens, latency_ms, int(success), model),
        )
        await db.commit()
        await db.close()

    async def record_decision(self, decision: DecisionOutput) -> None:
        from datetime import datetime
        db = await self._db()
        await db.execute(
            "INSERT OR REPLACE INTO decisions VALUES (?,?,?,?,?,?,?)",
            (
                decision.id, decision.decision_type, decision.recommendation,
                decision.confidence, json.dumps(decision.signal_breakdown),
                decision.outcome, datetime.utcnow().isoformat(),
            ),
        )
        await db.commit()
        await db.close()

    async def get_decisions(self, days: int = 7) -> list[DecisionOutput]:
        db = await self._db()
        cursor = await db.execute("SELECT * FROM decisions ORDER BY created_at DESC LIMIT 50")
        rows = await cursor.fetchall()
        await db.close()
        results = []
        for r in rows:
            results.append(DecisionOutput(
                id=r[0], decision_type=r[1], recommendation=r[2], confidence=r[3],
                signal_breakdown=json.loads(r[4] or "{}"),
                outcome=r[5] or "pending",
            ))
        return results

    async def update_decision_outcome(self, decision_id: str, outcome: str) -> None:
        db = await self._db()
        await db.execute("UPDATE decisions SET outcome=? WHERE id=?", (outcome, decision_id))
        await db.commit()
        await db.close()

    async def record_evolution(self, cycle: EvolutionCycle) -> None:
        db = await self._db()
        await db.execute(
            "INSERT OR REPLACE INTO evolution_cycles VALUES (?,?,?,?,?)",
            (cycle.id, json.dumps(cycle.weight_changes), json.dumps(cycle.new_rules),
             int(cycle.approved), cycle.created_at.isoformat()),
        )
        await db.commit()
        await db.close()
