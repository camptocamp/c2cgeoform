include Makefile

.build/requirements.timestamp: .build/venv.timestamp requirements.txt
	$(VENV_BIN)/pip install pip==22.0.2
	$(VENV_BIN)/pip install -r requirements.txt -e .
	$(VENV_BIN)/pip install -e ../..
	touch $@
