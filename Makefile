test:
	pytest tests

init:
	pip install -r requirements.txt

.PHONY: init test
