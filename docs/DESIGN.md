# Design record

## Decision

The outbox claims an event with a lease, signs its ID, timestamp and exact bytes, then retries with bounded exponential delay. The receiver persists a unique event ID and payload hash.

## Failure model

Outage then recovery, persisted retry state, bounded dead-letter transitions, stale/tampered signatures and conflicting event IDs. PostgreSQL also executes the delivery state machine.

## Tradeoffs

Delivery is at least once. Receiver effects are exactly once only within the demonstrated local receipt transaction. Destination is operator-configured; there is no tenant-facing arbitrary URL input.

## Next change to defend in review

Add jitter, operational dead-letter replay, secret rotation and delivery metrics.

## Reproducibility

`uv.lock` pins Python dependencies; the web lockfile pins the React build where present. Model-backed evaluations use a separately installed local service. Dataset examples are synthetic and intentionally small. Reported timing is a local observation, not a throughput SLA. Run `make test` after changing state transitions and `make eval` after changing decisions. Keep inference quality separate from deterministic invariant checks.
