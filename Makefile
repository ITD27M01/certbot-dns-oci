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
	@find . -type d -name "__pycache__" -exec rm -rf {} +
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

.PHONY: bdist
bdist:
	$(MAKE) clean
	@python setup.py bdist_wheel

.PHONY: upload
upload:
	$(MAKE) clean
	$(MAKE) sdist
	$(MAKE) bdist
	@twine upload --username __token__ --password $(TWINE_PASSWORD) dist/*
