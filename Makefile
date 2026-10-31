UV ?= uv
PORT ?= 8111
.PHONY: setup demo test eval serve stop lint
setup:
	$(UV) sync --frozen
demo:
	$(UV) run --frozen python -m app.cli demo
test:
	$(UV) run --frozen pytest -q
eval:
	$(UV) run --frozen python -m app.cli eval
eval-local:
	$(UV) run --frozen python -m app.cli eval --mode local
serve:
	$(UV) run --frozen uvicorn app.api:app --host 127.0.0.1 --port $(PORT)
lint:
	$(UV) run --frozen ruff check app tests
stop:
	@echo "Foreground processes: Ctrl-C. Containers: docker compose down (keeps data)."
