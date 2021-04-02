.ONESHELL:
SHELL = /bin/bash

default: update

.PHONY: init
init:
	@pip3 -q install -r requirements.txt
	@pip3 -q install -r build-requirements.txt
	@pip3 -q install -r test-requirements.txt

.PHONY: clean
clean:
	@python setup.py clean
	@rm -rf dist
	@rm -rf .tox
	@rm -rf build
	@rm -rf .pytest_cache
	@find . -name "*.pyc" -delete
	@rm -rf *.egg-info
	@rm -rf .eggs
	@pip uninstall certbot-dns-oci -y

.PHONY: check
check:
	@flake8 --ignore=W605,E501 certbot_dns_oci

.PHONY: tests
tests:
	$(MAKE) clean
	$(MAKE) install
	@pytest --cache-clear

.PHONY: install
install:
	@python setup.py install

.PHONY: update
update:
	$(MAKE) clean
	$(MAKE) check
	$(MAKE) install
	@clear

.PHONY: sdist
sdist:
	$(MAKE) clean
	@python setup.py sdist

.PHONY: upload
upload:
	$(MAKE) clean
	$(MAKE) sdist
	@twine upload --username __token__ --password $(TWINE_PASSWORD) dist/*
