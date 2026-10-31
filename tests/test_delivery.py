import pytest
from app.core import DeliveryEngine, sign


@pytest.fixture
def engine(tmp_path):
    return DeliveryEngine("sqlite:///" + str(tmp_path / "outbox.sqlite"))


def test_retry_persists_and_recovers(engine):
    engine.enqueue("a", {"value": 1})
    assert engine.deliver(lambda b, h: 503, "s", now=10)["state"] == "retry"
    assert engine.deliver(lambda b, h: 200, "s", now=11) is None
    restarted = DeliveryEngine(str(engine.engine.url))
    assert restarted.deliver(lambda b, h: 200, "s", now=13)["state"] == "delivered"
    assert restarted.deliver(lambda b, h: 200, "s", now=100) is None


def test_dead_letter(engine):
    engine.enqueue("b", {})
    for t in [10, 20, 40, 80]:
        result = engine.deliver(lambda b, h: 500, "s", now=t)
    assert result["state"] == "dead"
    assert result["attempts"] == 4


def test_receiver_dedup_and_tamper(engine):
    body = b'{"ok":true}'
    h = {"X-Event-ID": "e", "X-Timestamp": "100", "X-Signature": sign("s", 100, "e", body)}
    assert not engine.receive(body, h, "s", now=100)["duplicate"]
    assert engine.receive(body, h, "s", now=101)["duplicate"]
    with pytest.raises(PermissionError):
        engine.receive(b"{}", h, "s", now=100)
    with pytest.raises(PermissionError):
        engine.receive(body, h, "s", now=500)


def test_enqueue_idempotency_conflict(engine):
    engine.enqueue("a", {"value": 1})
    engine.enqueue("a", {"value": 1})
    with pytest.raises(ValueError):
        engine.enqueue("a", {"value": 2})
    assert len(engine.status()) == 1
