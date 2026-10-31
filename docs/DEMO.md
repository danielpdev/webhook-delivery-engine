# Demo walkthrough

## Start

```bash
make setup
make demo
make test
make eval
```

## What to show

The outbox claims an event with a lease, signs its ID, timestamp and exact bytes, then retries with bounded exponential delay. The receiver persists a unique event ID and payload hash.

## Failure case to discuss

Outage then recovery, persisted retry state, bounded dead-letter transitions, stale/tampered signatures and conflicting event IDs. PostgreSQL also executes the delivery state machine.

## Evidence

Open the JSON evaluation report alongside the implementation. Distinguish synthetic fixture outputs, synthetic trace timing, actual elapsed evaluation time, and local model inference. Do not present a tiny test set as a production benchmark.

## Closing tradeoff

Delivery is at least once. Receiver effects are exactly once only within the demonstrated local receipt transaction. Destination is operator-configured; there is no tenant-facing arbitrary URL input.

The repository's `docs/demo.webm` or `docs/demo.mp4`, when present, records the demonstration. A terminal replay is also available for focused projects as `docs/demo.cast`.
