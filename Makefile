PYTHON ?= python3

.PHONY: install install-dev extract dry-run validate test serve api
install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

dry-run:
	$(PYTHON) backend/scripts/extract_arcgis.py --dry-run

extract:
	$(PYTHON) backend/scripts/extract_arcgis.py

validate:
	$(PYTHON) backend/scripts/validate_dataset.py

test:
	$(PYTHON) -m pytest -q

serve:
	$(PYTHON) -m http.server 8080 --directory frontend

api:
	$(PYTHON) -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
