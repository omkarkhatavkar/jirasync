.PHONY: clean format lint all install

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

format: clean
	isort jirasync/*.py
	isort jirasync/*/*.py
	# export BLACKPATH=path to black binary in a python3.6 virtualenv
	$(BLACKPATH) jirasync/* -l 79 -t py27

lint:
	flake8 jirasync/*

all: format lint

install:
	pip install -e .
	pip install -r requirements.txt -r requirements-another.txt -r requirements-dev.txt
