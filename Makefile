BUILD_DIR ?= .build
LANGUAGES = fr de it

MO_FILES = $(addprefix c2cgeoform/locale/, $(addsuffix /LC_MESSAGES/c2cgeoform.mo, $(LANGUAGES)))
PO_FILES = $(addprefix c2cgeoform/locale/, $(addsuffix /LC_MESSAGES/c2cgeoform.po, $(LANGUAGES)))

L10N_SOURCE_FILES += c2cgeoform/__init__.py c2cgeoform/models.py c2cgeoform/views/abstract_views.py
L10N_SOURCE_FILES += $(shell find c2cgeoform/templates/ -type f -name '*.pt')
L10N_SOURCE_FILES += $(shell find c2cgeoform/templates/ -type f -name '*.jinja2')

.PHONY: all
all: help

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo
	@echo "- build                   Install c2cgeoform"
	@echo "- initdb                  (Re-)initialize the database"
	@echo "- check                   Check the code with prospector"
	@echo "- test                    Run the unit tests"
	@echo "- dist                    Build a source distribution"
	@echo "- compile-catalog         Compile message catalog"
	@echo

.PHONY: build
build: docker-build-db poetry compile-catalog c2cgeoform/static/dist/index.js

.PHONY: check
check: prospector

.PHONY: poetry
poetry:
	poetry install --with=dev --extras=psycopg2-binary

.PHONY: prospector
prospector: poetry
	poetry run prospector --output-format=pylint --die-on-tool-error

.build/node_modules.timestamp: c2cgeoform/static/package.json
	mkdir -p $(dir $@)
	cd c2cgeoform/static/ && npm install
	touch $@

c2cgeoform/static/dist/index.js: .build/node_modules.timestamp c2cgeoform/static/src/*
	cd c2cgeoform/static/ && npm run build

.PHONY: test
test: test_c2cgeoform test_c2cgeoform_demo

.PHONY: test_c2cgeoform
test_c2cgeoform: build poetry
	docker-compose up -d db
	poetry run pytest -vvv

.PHONY: test_c2cgeoform_demo
test_c2cgeoform_demo: $(BUILD_DIR)/c2cgeoform_demo
	docker-compose up -d db
	make -C $(BUILD_DIR)/c2cgeoform_demo -f ./dev.mk test

$(BUILD_DIR)/c2cgeoform_demo: build c2cgeoform/scaffolds/c2cgeoform c2cgeoform_demo_dev.mk
	rm -rf $@
	poetry run cookiecutter --no-input --output-dir=$(dir $@) c2cgeoform/scaffolds/c2cgeoform/ \
		project=c2cgeoform_demo package=c2cgeoform_demo \
		package_logger=c2cgeoform_demo pyramid_docs_branch=master
	cp c2cgeoform_demo_dev.mk $@/dev.mk

.PHONY: update-catalog
update-catalog: poetry
	poetry run pot-create -c lingua.cfg --keyword _ -o c2cgeoform/locale/c2cgeoform.pot $(L10N_SOURCE_FILES)
	make $(PO_FILES)

c2cgeoform/locale/%/LC_MESSAGES/c2cgeoform.po: c2cgeoform/locale/c2cgeoform.pot
	msgmerge --update $@ $<

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

.PHONY: docs
docs: poetry
	make -C docs html

%.mo: %.po
	msgfmt $< --output-file=$@

.PHONY: clean
clean:
	rm -f $(MO_FILES)
	rm -rf .build/node_modules.timestamp
	rm -rf c2cgeoform/static/dist
	rm -rf dist
	rm -rf docs/_build

.PHONY: cleanall
cleanall: clean
	poetry env remove --all
	rm -rf c2cgeoform/static/node_modules

.PHONY: initdb
initdb: $(BUILD_DIR)/c2cgeoform_demo
	docker-compose up -d db
	sleep 1
	make -C $(BUILD_DIR)/c2cgeoform_demo -f dev.mk initdb

.PHONY: webpack-dev
webpack-dev:
	cd c2cgeoform/static/ && ./node_modules/.bin/webpack -d -w

.PHONY: serve
serve: build $(BUILD_DIR)/c2cgeoform_demo
	docker-compose up -d db
	make -C $(BUILD_DIR)/c2cgeoform_demo -f dev.mk serve

.PHONY: modwsgi
modwsgi: $(BUILD_DIR)/c2cgeoform_demo
	make -C $(BUILD_DIR)/c2cgeoform_demo modwsgi


# Docker builds

docker-build-db:
	docker build -t camptocamp/c2cgeoform-db:latest db
