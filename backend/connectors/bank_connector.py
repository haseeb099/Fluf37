from datetime import datetime
from typing import Any, Dict

import structlog

from backend.connectors.base import BaseConnector
from backend.connectors.live.plaid_client import PlaidClient
from backend.schemas.models import BankTransaction, ConnectionStatus, SourceData
from backend.utils.synthetic_data import get_demo_bank

logger = structlog.get_logger()


class BankConnector(BaseConnector):
    source_type = "bank"
    supports_webhook = True

    async def connect(self) -> ConnectionStatus:
        self._connected = True
        return self.get_status()

    async def disconnect(self) -> None:
        self._connected = False

    async def fetch_batch(self) -> Dict[str, Any]:
        self._last_sync = datetime.utcnow()
        if self.config.is_demo() or not self.config.nexus_enable_bank:
            return {"transactions": [t.model_dump() for t in get_demo_bank()]}
        if self.config.plaid_configured():
            client = PlaidClient(
                self.config.plaid_client_id,
                self.config.plaid_secret,
                self.config.plaid_env,
            )
            raw_txs = await client.fetch_transactions()
            txs = [
                BankTransaction(
                    id=str(t.get("id", f"plaid_{i}")),
                    amount=float(t.get("amount", 0)),
                    description=str(t.get("description", "")),
                    timestamp=str(t.get("date", datetime.utcnow().isoformat())),
                    from_account=str(t.get("account_id", "plaid")),
                )
                for i, t in enumerate(raw_txs)
            ]
            return {"transactions": [t.model_dump() for t in txs]}
        logger.warning("bank_live_not_configured")
        return {"transactions": []}

    def normalize(self, raw: Dict[str, Any]) -> SourceData:
        txs = [BankTransaction(**t) for t in raw.get("transactions", [])]
        return SourceData(bank=txs, source_ids=["bank"])
