import os
import pytest
from app.core import DeliveryEngine
from app.db import Base


@pytest.mark.skipif(
    not os.getenv("POSTGRES_TEST_URL"), reason="Set POSTGRES_TEST_URL to a dedicated test database"
)
def test_postgresql_transactional_scenario():
    s = DeliveryEngine(os.environ["POSTGRES_TEST_URL"])
    try:
        s.enqueue("pg-event", {"ok": True})
        assert s.deliver(lambda b, h: 503, "s", now=100)["state"] == "retry"
        assert s.deliver(lambda b, h: 200, "s", now=103)["state"] == "delivered"
    finally:
        Base.metadata.drop_all(s.engine)
        s.engine.dispose()
