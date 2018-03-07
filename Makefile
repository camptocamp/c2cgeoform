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
	@echo "- build                   Install c2cgeoform"
	@echo "- initdb                  (Re-)initialize the database"
	@echo "- check                   Check the code with flake8"
	@echo "- test                    Run the unit tests"
	@echo "- dist                    Build a source distribution"
	@echo "- compile-catalog         Compile message catalog"
	@echo

.PHONY: build
build: .build/requirements.timestamp compile-catalog

.PHONY: check
check: flake8 check_c2cgeoform_demo

.PHONY: flake8
flake8: .build/requirements-dev.timestamp
	.build/venv/bin/flake8 c2cgeoform

.PHONY: check_c2cgeoform_demo
check_c2cgeoform_demo: c2cgeoform_demo
	make -C ../c2cgeoform_demo check

.PHONY: test
test: test_c2cgeoform test_c2cgeoform_demo

.PHONY: test_c2cgeoform
test_c2cgeoform: .build/requirements.timestamp .build/requirements-dev.timestamp
	.build/venv/bin/nosetests --ignore-files=test_views.py

.PHONY: test_c2cgeoform_demo
test_c2cgeoform_demo: c2cgeoform_demo
	make -C ../c2cgeoform_demo test

.PHONY: c2cgeoform_demo
c2cgeoform_demo: .build/requirements.timestamp c2cgeoform/scaffolds/c2cgeoform
	.build/venv/bin/pcreate -s c2cgeoform --overwrite ../c2cgeoform_demo > /dev/null

.PHONY: update-catalog
update-catalog: .build/requirements.timestamp
	.build/venv/bin/pot-create -c lingua.cfg --keyword _ -o c2cgeoform/locale/c2cgeoform.pot \
	    c2cgeoform/models.py \
	    c2cgeoform/views/abstract_views.py \
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
	# Create a Python virtual environment.
	virtualenv -p python3 .build/venv
	# Upgrade packaging tools.
	.build/venv/bin/pip install --upgrade pip==9.0.1 setuptools==36.5.0
	touch $@

.build/requirements.timestamp: .build/venv.timestamp setup.py
	.build/venv/bin/pip install -U -e .
	touch $@

.build/requirements-dev.timestamp: .build/venv.timestamp requirements-dev.txt
	.build/venv/bin/pip install -r requirements-dev.txt
	touch $@

.PHONY: clean
clean:
	rm -f $(MO_FILES)

.PHONY: cleanall
cleanall:
	rm -rf .build
