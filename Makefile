PYTHON ?= python

setup:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q

run:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000

ingest:
	$(PYTHON) -m app.ingest.cli
