"""Alerting webhooks stub (Slack/PagerDuty) — Phase 10."""
from typing import Optional

import structlog

logger = structlog.get_logger()


async def send_critical_alert(title: str, message: str, webhook_url: Optional[str] = None) -> bool:
    if not webhook_url:
        logger.info("alert_skipped_no_webhook", title=title)
        return False
    logger.info("alert_sent", title=title, message=message[:100])
    return True
