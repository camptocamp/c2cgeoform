include Makefile

.build/requirements.timestamp: .build/venv.timestamp requirements.txt ../../setup.py
	$(VENV_BIN)/pip install -e ../.. -r requirements.txt -e .
	touch $@
