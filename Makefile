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
install: pip-install compile-catalog
	
.PHONY: pip-install
pip-install: .build/venv
	.build/venv/bin/pip install -U -e .

.PHONY: initdb
initdb:
	.build/venv/bin/initialize_c2cgeoform_db development.ini

.PHONY: serve
serve:
	.build/venv/bin/pserve --reload development.ini

.PHONY: check
check: flake8

.PHONY: flake8
flake8: .build/venv/bin/flake8
	.build/venv/bin/flake8 c2cgeoform

.PHONY: test
test:
	.build/venv/bin/python setup.py test

.PHONY: update-catalog
update-catalog:
	.build/venv/bin/pot-create -c lingua.cfg -o c2cgeoform/locale/c2cgeoform.pot \
	    c2cgeoform/models.py \
	    c2cgeoform/views.py \
	    c2cgeoform/templates/
	msgmerge --update c2cgeoform/locale/fr/LC_MESSAGES/c2cgeoform.po c2cgeoform/locale/c2cgeoform.pot
	msgmerge --update c2cgeoform/locale/de/LC_MESSAGES/c2cgeoform.po c2cgeoform/locale/c2cgeoform.pot

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

.PHONY: dist
dist: .build/venv compile-catalog
	.build/venv/bin/python setup.py sdist

%.mo: %.po
	msgfmt $< --output-file=$@

.build/venv:
	mkdir -p $(dir $@)
	# make a first virtualenv to get a recent version of virtualenv
	virtualenv venv
	venv/bin/pip install virtualenv
	venv/bin/virtualenv --no-site-packages .build/venv
	# remove the temporary virtualenv
	rm -rf venv

.build/venv/bin/flake8: .build/venv
	.build/venv/bin/pip install -r requirements-dev.txt > /dev/null 2>&1


.PHONY: clean
clean:
	rm -f $(MO_FILES)

.PHONY: cleanall
cleanall:
	rm -rf .build
