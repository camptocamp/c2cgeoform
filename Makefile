BUILD_DIR?=.build
VENV?=${BUILD_DIR}/venv
MO_FILES = $(addprefix c2cgeoform/locale/, fr/LC_MESSAGES/c2cgeoform.mo de/LC_MESSAGES/c2cgeoform.mo it/LC_MESSAGES/c2cgeoform.mo)

ifneq (,$(findstring CYGWIN, $(shell uname)))
PYTHON3 =
VENV_BIN = .build/venv/Scripts
PIP_UPGRADE = python.exe -m pip install --upgrade pip==9.0.1 setuptools==36.5
else
PYTHON3 = -p python3
VENV_BIN = .build/venv/bin
PIP_UPGRADE = pip install --upgrade pip==9.0.1 setuptools==36.5.0
endif


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
	@echo "- check                   Check the code with flake8"
	@echo "- test                    Run the unit tests"
	@echo "- dist                    Build a source distribution"
	@echo "- compile-catalog         Compile message catalog"
	@echo

.PHONY: build
build: .build/requirements.timestamp compile-catalog c2cgeoform/static/dist/index.js

.PHONY: check
check: flake8 check_c2cgeoform_demo

.PHONY: flake8
flake8: .build/requirements-dev.timestamp
	$(VENV_BIN)/flake8 --exclude=node_modules c2cgeoform

.build/node_modules.timestamp: c2cgeoform/static/package.json
	cd c2cgeoform/static/ && npm install
	touch $@

c2cgeoform/static/dist/index.js: .build/node_modules.timestamp c2cgeoform/static/src/*
	cd c2cgeoform/static/ && npm run build

.PHONY: check_c2cgeoform_demo
check_c2cgeoform_demo: $(BUILD_DIR)/c2cgeoform_demo
	make -C $(BUILD_DIR)/c2cgeoform_demo check

.PHONY: test
test: test_c2cgeoform test_c2cgeoform_demo

.PHONY: test_c2cgeoform
test_c2cgeoform: build .build/requirements-dev.timestamp
	$(VENV_BIN)/nosetests --ignore-files=test_views.py

.PHONY: test_c2cgeoform_demo
test_c2cgeoform_demo: $(BUILD_DIR)/c2cgeoform_demo
	make -C $(BUILD_DIR)/c2cgeoform_demo -f ./dev.mk test

$(BUILD_DIR)/c2cgeoform_demo: build c2cgeoform/scaffolds/c2cgeoform c2cgeoform_demo_dev.mk
	$(VENV_BIN)/pcreate -s c2cgeoform --overwrite $(BUILD_DIR)/c2cgeoform_demo > /dev/null
	cp c2cgeoform_demo_dev.mk $(BUILD_DIR)/c2cgeoform_demo/dev.mk

.PHONY: update-catalog
update-catalog: .build/requirements.timestamp
	$(VENV_BIN)/pot-create -c lingua.cfg --keyword _ -o c2cgeoform/locale/c2cgeoform.pot \
	    c2cgeoform/models.py \
	    c2cgeoform/views/abstract_views.py \
	    c2cgeoform/templates/
	msgmerge --update c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.po c2cgeoform/locale/c2cgeoform.pot
	msgmerge --update c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.po c2cgeoform/locale/c2cgeoform.pot
	msgmerge --update c2cgeoform/locale/it/LC_MESSAGES/c2cgeoform.po c2cgeoform/locale/c2cgeoform.pot

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

.PHONY: dist
dist: .build/requirements-dev.timestamp compile-catalog
	$(VENV_BIN)/python setup.py sdist

.PHONY: docs
docs: .build/requirements.timestamp .build/requirements-dev.timestamp
	make -C docs html

%.mo: %.po
	msgfmt $< --output-file=$@

.build/venv.timestamp:
	# Create a Python virtual environment.
	virtualenv $(PYTHON3) .build/venv
	# Upgrade packaging tools.
	$(VENV_BIN)/$(PIP_UPGRADE)
	$(VENV_BIN)/pip install wheel  # Avoid error when building wheels
	touch $@

.build/requirements.timestamp: .build/venv.timestamp setup.py requirements.txt
	$(VENV_BIN)/pip install -r requirements.txt -e .
	touch $@

.build/requirements-dev.timestamp: .build/venv.timestamp requirements-dev.txt
	$(VENV_BIN)/pip install -r requirements-dev.txt
	touch $@

.PHONY: clean
clean:
	rm -f $(MO_FILES)
	rm -rf docs/_build

.PHONY: cleanall
cleanall: clean
	rm -rf .build

.PHONY: initdb
initdb: $(BUILD_DIR)/c2cgeoform_demo
	make -C $(BUILD_DIR)/c2cgeoform_demo -f dev.mk initdb

.PHONY: webpack-dev
webpack-dev:
	cd c2cgeoform/static/ && ./node_modules/.bin/webpack -d -w

.PHONY: serve
serve: $(BUILD_DIR)/c2cgeoform_demo
	make -C $(BUILD_DIR)/c2cgeoform_demo -f dev.mk serve

.PHONY: modwsgi
modwsgi: $(BUILD_DIR)/c2cgeoform_demo
	make -C $(BUILD_DIR)/c2cgeoform_demo modwsgi
