all: install

deps:
	pip install -r requirements.txt --user

install:
	pip install . --user --upgrade

uninstall:
	pip uninstall dialogflow_utils

test:
	GOOGLE_APPLICATION_CREDENTIALS=keys/test-credentials.json nosetests --rednose

.PHONY: init install uninstall test
