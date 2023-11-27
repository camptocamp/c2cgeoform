INSTANCE_ID ?= main
APACHE_ENTRY_POINT ?= /

LANGUAGES = fr de it

MO_FILES = $(addprefix {{cookiecutter.package}}/locale/, $(addsuffix /LC_MESSAGES/{{cookiecutter.package}}.mo, $(LANGUAGES)))
PO_FILES = $(addprefix {{cookiecutter.package}}/locale/, $(addsuffix /LC_MESSAGES/{{cookiecutter.package}}.po, $(LANGUAGES)))

L10N_SOURCE_FILES += $(shell find {{cookiecutter.package}} -type f -name '*.py')
L10N_SOURCE_FILES += $(shell find {{cookiecutter.package}}/templates/ -type f -name '*.pt')
L10N_SOURCE_FILES += $(shell find {{cookiecutter.package}}/templates/ -type f -name '*.jinja2')

ifneq (,$(findstring CYGWIN, $(shell uname)))
PYTHON3 =
VENV_BIN = .build/venv/Scripts
PIP_UPGRADE = python.exe -m pip install --upgrade pip==21.1 setuptools==56.0
else
PYTHON3 = -p python3
VENV_BIN = .build/venv/bin
PIP_UPGRADE = pip install --upgrade pip==21.1 setuptools==56.0
endif

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo
	@echo "- build                   Install {{cookiecutter.project}}"
	@echo "- initdb                  (Re-)initialize the database"
	@echo "- serve                   Run the dev server"
	@echo "- modwsgi                 Create files for Apache mod_wsgi"
	@echo "- test                    Run the unit tests"
	@echo "- dist                    Build a source distribution"
	@echo "- update-catalog          Update message catalog"
	@echo "- compile-catalog         Compile message catalog"
	@echo

.PHONY: build
build: \
		.build/requirements.timestamp \
		.build/node_modules.timestamp \
		compile-catalog

.PHONY: initdb
initdb: .build/requirements.timestamp
	$(VENV_BIN)/initialize_{{cookiecutter.package}}_db development.ini

.PHONY: serve
serve: build
	$(VENV_BIN)/pserve --reload development.ini

.PHONY: modwsgi
modwsgi: build .build/{{cookiecutter.package}}.wsgi .build/apache.conf

.PHONY: test
test: build .build/requirements-dev.timestamp
	$(VENV_BIN)/pytest

.PHONY: update-catalog
update-catalog: .build/requirements.timestamp
	$(VENV_BIN)/pot-create -c lingua.cfg --keyword _ -o {{cookiecutter.package}}/locale/{{cookiecutter.package}}.pot $(L10N_SOURCE_FILES)
	make $(PO_FILES)

{{cookiecutter.package}}/locale/%/LC_MESSAGES/{{cookiecutter.package}}.po: {{cookiecutter.package}}/locale/{{cookiecutter.package}}.pot
	mkdir -p $(dir $@)
	touch $@  # Create file if not exists
	msgmerge --update $@ $<

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

.PHONY: dist
dist: .build/venv.timestamp compile-catalog
	$(VENV_BIN)/python setup.py sdist

%.mo: %.po
	msgfmt $< --output-file=$@

.build/node_modules.timestamp: package.json
	npm install
	touch $@

.build/venv.timestamp:
	# Create a Python virtual environment.
	python3 -m venv .build/venv
	# Upgrade packaging tools.
	$(VENV_BIN)/$(PIP_UPGRADE)
	touch $@

.build/requirements.timestamp: .build/venv.timestamp requirements.txt
	$(VENV_BIN)/pip install -r requirements.txt -e .
	touch $@

.build/requirements-dev.timestamp: .build/venv.timestamp requirements-dev.txt
	$(VENV_BIN)/pip install -r requirements-dev.txt > /dev/null 2>&1
	touch $@

.build/{{cookiecutter.package}}.wsgi: {{cookiecutter.package}}.wsgi
	sed 's#\[DIR\]#$(CURDIR)#' $< > $@
	chmod 755 $@

.build/apache.conf: apache.conf .build/venv.timestamp
	sed -e 's#\[PYTHONPATH\]#$(shell $(VENV_BIN)/python -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_lib())")#' \
        -e 's#\[WSGISCRIPT\]#$(abspath .build/{{cookiecutter.package}}.wsgi)#' \
        -e 's#\[INSTANCE_ID\]#$(INSTANCE_ID)#' \
        -e 's#\[APACHE_ENTRY_POINT\]#$(APACHE_ENTRY_POINT)#' $< > $@

.PHONY: clean
clean:
	rm -f .build/venv/{{cookiecutter.package}}.wsgi
	rm -f .build/apache.conf
	rm -f $(MO_FILES)

.PHONY: cleanall
cleanall:
	rm -rf .build
	rm -rf node_modules
