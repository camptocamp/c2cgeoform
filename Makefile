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
	@echo "- serve                   Run the dev server"
	@echo "- check                   Check the code with flake8"
	@echo "- modwsgi                 Create files for Apache mod_wsgi"
	@echo "- test                    Run the unit tests"
	@echo

.PHONY: install
install: .build/venv
	.build/venv/bin/python setup.py develop
	msgfmt c2cgeoform/pully/locale/fr/LC_MESSAGES/pully.po \
			--output-file=c2cgeoform/pully/locale/fr/LC_MESSAGES/pully.mo

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

.PHONY: modwsgi
modwsgi: install .build/venv/c2cgeoform.wsgi .build/apache.conf

.PHONY: test
test:
	.build/venv/bin/python setup.py test

.build/venv:
	mkdir -p $(dir $@)
	virtualenv --no-site-packages .build/venv

.build/venv/bin/flake8: .build/venv
	.build/venv/bin/pip install -r requirements.txt > /dev/null 2>&1

.build/venv/c2cgeoform.wsgi: c2cgeoform.wsgi
	sed 's#{{DIR}}#$(CURDIR)#' $< > $@
	chmod 755 $@

.build/apache.conf: apache.conf .build/venv
	sed -e 's#{{PYTHONPATH}}#$(shell .build/venv/bin/python -c "import distutils; print(distutils.sysconfig.get_python_lib())")#' \
		-e 's#{{WSGISCRIPT}}#$(abspath .build/venv/c2cgeoform.wsgi)#' $< > $@

.PHONY: clean
clean:
	rm -f .build/venv/c2cgeoform.wsgi
	rm -f .build/apache.conf

.PHONY: cleanall
cleanall:
	rm -rf .build
