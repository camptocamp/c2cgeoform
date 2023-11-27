include Makefile

.build/requirements.timestamp: .build/venv.timestamp requirements.txt ../../pyproject.toml
	$(VENV_BIN)/pip install --requirement=requirements.txt  --requirement=requirements-dev.txt \
		--editable=. ../..
	touch $@
