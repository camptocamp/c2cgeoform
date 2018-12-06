include Makefile

.build/requirements.timestamp: .build/venv.timestamp requirements.txt ../c2cgeoform/setup.py
	$(VENV_BIN)/pip install -e ../c2cgeoform -r requirements.txt -e .
	touch $@
