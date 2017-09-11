BUILD_DIR?=.build
VENV?=${BUILD_DIR}/venv
MO_FILES = $(addprefix c2cgeoform/locale/, fr/LC_MESSAGES/c2cgeoform.mo de/LC_MESSAGES/c2cgeoform.mo)


.PHONY: all
all: help

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo
	@echo "- install                 Install c2cgeoform"
	@echo "- initdb                  (Re-)initialize the database"
	@echo "- check                   Check the code with flake8"
	@echo "- test                    Run the unit tests"
	@echo "- dist                    Build a source distribution"
	@echo "- compile-catalog         Compile message catalog"
	@echo

.PHONY: install
build: .build/requirements.timestamp compile-catalog

.PHONY: check
check: flake8

.PHONY: flake8
flake8: .build/requirements-dev.timestamp
	.build/venv/bin/flake8 c2cgeoform

.PHONY: test
test: .build/requirements.timestamp .build/requirements-dev.timestamp
	.build/venv/bin/nosetests --ignore-files=test_views.py

.PHONY: update-catalog
update-catalog: .build/requirements-dev.timestamp
	.build/venv/bin/pot-create -c lingua.cfg -o c2cgeoform/locale/c2cgeoform.pot \
	    c2cgeoform/models.py \
	    c2cgeoform/views.py \
	    c2cgeoform/templates/
	msgmerge --update c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.po c2cgeoform/locale/c2cgeoform.pot
	msgmerge --update c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.po c2cgeoform/locale/c2cgeoform.pot

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

.PHONY: dist
dist: .build/requirements-dev.timestamp compile-catalog
	.build/venv/bin/python setup.py sdist

%.mo: %.po
	msgfmt $< --output-file=$@

.build/venv.timestamp:
	mkdir -p $(dir $@)
	# make a first virtualenv to get a recent version of virtualenv
	python3 -m venv ${VENV}
	touch .build/venv.timestamp

.build/requirements.timestamp: .build/venv.timestamp setup.py
	.build/venv/bin/pip install -U -e .
	touch .build/requirements.timestamp

.build/requirements-dev.timestamp: .build/venv.timestamp requirements-dev.txt
	.build/venv/bin/pip install -r requirements-dev.txt
	touch .build/requirements-dev.timestamp

.PHONY: clean
clean:
	rm -f $(MO_FILES)

.PHONY: cleanall
cleanall:
	rm -rf .build
