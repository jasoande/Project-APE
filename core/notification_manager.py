"""Completion notifications via webhook for pipeline workflows."""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def send_webhook(url: str, payload: Dict, timeout: int = 10) -> bool:
    """POST a JSON payload to a webhook URL.

    Returns True on success (2xx status), False on any failure.
    """
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        logger.error(f"Webhook HTTP error {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        logger.error(f"Webhook URL error: {e.reason}")
        return False
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return False


def format_slack_payload(results: Dict) -> Dict:
    """Format results as a Slack Block Kit message."""
    total = results.get("total", 0)
    successful = results.get("successful", 0)
    failed = results.get("failed", 0)
    duration = results.get("duration", "N/A")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Account Intelligence - Workflow Complete",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Total:*\n{total}"},
                {"type": "mrkdwn", "text": f"*Successful:*\n{successful}"},
                {"type": "mrkdwn", "text": f"*Failed:*\n{failed}"},
                {"type": "mrkdwn", "text": f"*Duration:*\n{duration}"},
            ],
        },
    ]

    return {"blocks": blocks}


def notify_completion(config: Any, results: Dict) -> None:
    """Send a completion notification if a webhook URL is configured.

    Reads NOTIFICATION_WEBHOOK_URL from the config object (e.g. vars module).
    Does nothing if the URL is not set.
    """
    url: Optional[str] = getattr(config, "NOTIFICATION_WEBHOOK_URL", None)
    if not url:
        logger.debug("No NOTIFICATION_WEBHOOK_URL configured, skipping notification")
        return

    payload = format_slack_payload(results)
    success = send_webhook(url, payload)
    if success:
        logger.info("Completion notification sent successfully")
    else:
        logger.warning("Failed to send completion notification")
