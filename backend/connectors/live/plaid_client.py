"""Plaid live integration stub."""
from typing import Any, Dict, List

import structlog

logger = structlog.get_logger()


class PlaidClient:
    def __init__(self, client_id: str, secret: str, env: str = "sandbox"):
        self.client_id = client_id
        self.secret = secret
        self.env = env

    async def fetch_transactions(self, days: int = 30) -> List[Dict[str, Any]]:
        if not self.client_id or not self.secret:
            logger.warning("plaid_not_configured")
            return []
        # Live: use plaid-python SDK
        logger.info("plaid_fetch_stub", days=days)
        return []
