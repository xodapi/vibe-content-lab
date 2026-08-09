import hashlib
import hmac

from backend.app.config import settings
from backend.app.vibe_client import VibeClient


def test_webhook_signature_is_verified(monkeypatch):
    monkeypatch.setattr(settings, "vibe_webhook_secret", "test-secret")
    body = b'{"generation_id": 42, "status": "complete"}'
    signature = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()

    assert VibeClient.verified_webhook(body, signature)
    assert VibeClient.verified_webhook(body, f"sha256={signature}")
    assert not VibeClient.verified_webhook(body, "not-a-signature")


def test_webhook_requires_a_secret(monkeypatch):
    monkeypatch.setattr(settings, "vibe_webhook_secret", None)

    assert not VibeClient.verified_webhook(b"payload", "anything")
