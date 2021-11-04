.PHONEY: build, run, clean, zip, comp

VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

run: $(VENV)/bin/activate
	$(PYTHON) main.py $(file)

build: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt


clean:
	find . | grep -E "(__pycache__|\.pyc)" | xargs rm -rf
	rm -rf $(VENV) submission.tar.gz

comp: 
	compare -fuzz 2% $(file) test/correct_files/$(file) test/created_files/$(file)_diff.png

zip: 
	tar -czvf submission.tar.gz src main.py implemented.txt requirements.txt Makefile