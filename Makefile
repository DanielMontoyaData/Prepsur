PYTHON ?= python3

.PHONY: install extract dry-run validate test serve
install:
	$(PYTHON) -m pip install -r requirements.txt

dry-run:
	$(PYTHON) backend/scripts/extract_arcgis.py --dry-run

extract:
	$(PYTHON) backend/scripts/extract_arcgis.py

validate:
	$(PYTHON) backend/scripts/validate_dataset.py

test:
	$(PYTHON) -m unittest discover -s tests -v

serve:
	$(PYTHON) -m http.server 8080 --directory frontend
