# Webhook Delivery Engine

Signed delivery with retries, deduplication and a dead-letter queue.

[![verification](https://github.com/danielpdev/webhook-delivery-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/danielpdev/webhook-delivery-engine/actions/workflows/ci.yml)

**Role focus:** Backend Reliability / Integrations. **Status:** working local portfolio implementation, with synthetic data.

## Demo

![How Webhook Delivery Engine works](docs/demo.gif)

Edited replay of captured CLI outputs in deterministic fixture mode. This is not live model inference. [Full recording](docs/demo.mp4). Rebuild with `./scripts/render_gif.sh` (FFmpeg required).

## The engineering decision

The outbox claims an event with a lease, signs its ID, timestamp and exact bytes, then retries with bounded exponential delay. The receiver persists a unique event ID and payload hash.

```mermaid
flowchart LR
  Enqueue --> Durable_outbox; Durable_outbox --> Lease_and_HMAC; Lease_and_HMAC --> HTTP_receiver; HTTP_receiver --> Receipt_deduplication; Failure --> Retry_or_dead_letter
```

## Run locally

Requirements: Python 3.12, [uv](https://docs.astral.sh/uv/getting-started/installation/) and Make.

```bash
git clone https://github.com/danielpdev/webhook-delivery-engine.git
cd webhook-delivery-engine
make setup
make demo
make test
make eval
```

`make demo` uses an isolated temporary database where relevant, so it is safe to repeat. `make eval` writes a timestamped report to `reports/evaluation-fixture.json`. Fixture mode is deterministic and does not represent model inference. There is no recurring hosting or API subscription cost.

`make serve` opens the local API on `http://127.0.0.1:8111/docs`.

### PostgreSQL

The zero-service quickstart uses SQLite. The same SQLAlchemy domain layer also runs on PostgreSQL:

```bash
docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://portfolio:local-demo-only@127.0.0.1:55444/demo make serve
```

`tests/test_postgres.py` uses `POSTGRES_TEST_URL` and drops its test tables during cleanup. Point it only at a dedicated disposable test database. CI provisions one independently. Local demonstration credentials are deliberately non-secret and must never be reused for production.

[Watch the recorded demo](docs/demo.mp4) · [Reproduce the walkthrough](docs/DEMO.md)

## Verification and evidence

Outage then recovery, persisted retry state, bounded dead-letter transitions, stale/tampered signatures and conflicting event IDs. PostgreSQL also executes the delivery state machine.

- [Evaluation report](reports/evaluation-fixture.json) — measured during an actual run; inspect the mode and dataset size.
- [Development and authorship](docs/DEVELOPMENT.md).
- [Romanian interview preparation](docs/INTERVIEW_RO.md).
- [Design notes](docs/DESIGN.md).
- [Demo walkthrough](docs/DEMO.md).

CI uses standard GitHub-hosted runners and deterministic tests without downloading LLM weights. The lockfiles record exact package versions. Local-model results, when present, live in `reports/evaluation-local.json`; hardware/model identities are in `reports/environment.json`.

## Limits and next iteration

Delivery is at least once. Receiver effects are exactly once only within the demonstrated local receipt transaction. Destination is operator-configured; there is no tenant-facing arbitrary URL input.

Next: Add jitter, operational dead-letter replay, secret rotation and delivery metrics.

The local demonstration does not include production authentication, secret management or operational service guarantees. Bind it to localhost and use synthetic data. These projects demonstrate engineering decisions; they do not claim real customers, paid production deployments or guaranteed interviews.

## Project ownership

Implemented with Codex assistance for Daniel Popa. The owner should review the code, run it, make an independent change and rehearse the tradeoffs before presenting it at interview. That human understanding check is pending and cannot be verified automatically. See [development notes](docs/DEVELOPMENT.md).

MIT for original source; dependencies/models retain their own licenses. See [third-party notices](THIRD_PARTY.md).
