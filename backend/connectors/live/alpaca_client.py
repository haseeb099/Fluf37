"""Alpaca live integration stub."""
from typing import Any, Dict, List

import structlog

logger = structlog.get_logger()


class AlpacaClient:
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url

    async def fetch_positions(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("alpaca_not_configured")
            return []
        logger.info("alpaca_fetch_stub")
        return []
