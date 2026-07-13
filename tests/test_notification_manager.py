"""Tests for core/notification_manager.py - webhook notifications."""

import json
from unittest.mock import MagicMock, patch

import pytest

from core.notification_manager import (
    format_slack_payload,
    notify_completion,
    send_webhook,
)


class TestSendWebhook:

    def test_success(self, mocker):
        mock_urlopen = mocker.patch("core.notification_manager.urllib.request.urlopen")
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = send_webhook("https://hooks.example.com/webhook", {"text": "hello"})
        assert result is True
        mock_urlopen.assert_called_once()

    def test_failure(self, mocker):
        mock_urlopen = mocker.patch("core.notification_manager.urllib.request.urlopen")
        mock_urlopen.side_effect = Exception("Connection refused")

        result = send_webhook("https://hooks.example.com/webhook", {"text": "hello"})
        assert result is False


class TestFormatSlackPayload:

    def test_produces_valid_structure(self):
        results = {
            "total": 3,
            "successful": 2,
            "failed": 1,
            "duration": "12.3 min",
        }
        payload = format_slack_payload(results)

        assert isinstance(payload, dict)
        assert "blocks" in payload
        payload_str = json.dumps(payload)
        assert "Workflow Complete" in payload_str


class TestNotifyCompletion:

    def test_with_webhook_url(self, mocker):
        mock_send = mocker.patch("core.notification_manager.send_webhook", return_value=True)

        config = MagicMock()
        config.NOTIFICATION_WEBHOOK_URL = "https://hooks.example.com/test"

        results = {"total": 1, "successful": 1, "failed": 0}
        notify_completion(config, results)
        mock_send.assert_called_once()

    def test_without_webhook_url(self, mocker):
        mock_send = mocker.patch("core.notification_manager.send_webhook", return_value=True)

        config = MagicMock(spec=[])

        results = {"total": 1, "successful": 1, "failed": 0}
        notify_completion(config, results)
        mock_send.assert_not_called()
