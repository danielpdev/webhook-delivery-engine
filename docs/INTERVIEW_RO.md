# Pregătire pentru interviu — Webhook Delivery Engine

Roluri țintă: Backend Reliability / Integrations.

## Prezentare de 90 de secunde

1. Explică problema concretă și cine folosește rezultatul.
2. Rulează `make demo` sau fluxul din UI.
3. Arată testul pentru un caz de eșec, apoi explică mecanismul din cod.
4. Spune ce limite are demonstrația și ce ai construi pentru producție.

Decizia de explicat: The outbox claims an event with a lease, signs its ID, timestamp and exact bytes, then retries with bounded exponential delay. The receiver persists a unique event ID and payload hash.

## Cinci întrebări

1. De ce at-least-once?
2. Ce semnezi exact?
3. Cum previi timestamp replay?
4. Ce se întâmplă după crash în sending?
5. Cum tratezi efectele externe ale receiverului?

## Exercițiu înainte de a aplica

Add jitter, operational dead-letter replay, secret rotation and delivery metrics.

Alege o parte mică a acestei modificări, implementeaz-o personal, adaugă un test care verifică comportamentul și descrie rezultatul într-un commit real. Nu declara că ai înțeles sau construit singur o parte pe care nu o poți explica.

## Checklist personal

- [ ] Pot porni proiectul dintr-un checkout curat.
- [ ] Pot urmări cererea până la rezultatul salvat.
- [ ] Pot explica diferența dintre fixture și model local.
- [ ] Pot demonstra un eșec și recuperarea lui.
- [ ] Am făcut o modificare proprie și o pot explica în engleză.

Aceste puncte necesită review-ul tău; nu au fost bifate automat.
