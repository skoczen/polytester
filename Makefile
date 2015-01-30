# Python settings
ifndef TRAVIS
	ifndef PYTHON_MAJOR
		PYTHON_MAJOR := 2
	endif
	ifndef PYTHON_MINOR
		PYTHON_MINOR := 7
	endif
	ENV := env/py$(PYTHON_MAJOR)$(PYTHON_MINOR)
else
	# Use the virtualenv provided by Travis
	ENV = $(VIRTUAL_ENV)
endif

# Project settings
PROJECT := Polytester
PACKAGE := polytester
SOURCES := Makefile setup.py $(shell find $(PACKAGE) -name '*.py')
EGG_INFO := $(subst -,_,$(PROJECT)).egg-info

# System paths
PLATFORM := $(shell python -c 'import sys; print(sys.platform)')
ifneq ($(findstring win32, $(PLATFORM)), )
	SYS_PYTHON_DIR := C:\\Python$(PYTHON_MAJOR)$(PYTHON_MINOR)
	SYS_PYTHON := $(SYS_PYTHON_DIR)\\python.exe
	SYS_VIRTUALENV := $(SYS_PYTHON_DIR)\\Scripts\\virtualenv.exe
else
	SYS_PYTHON := python$(PYTHON_MAJOR)
	ifdef PYTHON_MINOR
		SYS_PYTHON := $(SYS_PYTHON).$(PYTHON_MINOR)
	endif
	SYS_VIRTUALENV := virtualenv
endif

# virtualenv paths
ifneq ($(findstring win32, $(PLATFORM)), )
	BIN := $(ENV)/Scripts
	OPEN := cmd /c start
else
	BIN := $(ENV)/bin
	ifneq ($(findstring cygwin, $(PLATFORM)), )
		OPEN := cygstart
	else
		OPEN := open
	endif
endif

# virtualenv executables
PYTHON := $(BIN)/python
PIP := $(BIN)/pip
FLAKE8 := $(BIN)/flake8
PEP257 := $(BIN)/pep257
PYTEST := $(BIN)/py.test
COVERAGE := $(BIN)/coverage

# Flags for PHONY targets
DEPENDS := $(ENV)/.depends
ALL := $(ENV)/.all

# Main Targets ###############################################################

.PHONY: all
all: depends $(ALL)
$(ALL): $(SOURCES)
	$(MAKE) check
	touch $(ALL)  # flag to indicate all setup steps were successful

.PHONY: ci
ci: check test

# Development Installation ###################################################

.PHONY: env
env: .virtualenv $(EGG_INFO)
$(EGG_INFO): Makefile setup.py requirements.txt
	echo $(ENV)
	VIRTUAL_ENV=$(ENV) $(PYTHON) setup.py develop
	touch $(EGG_INFO)  # flag to indicate package is installed

.PHONY: .virtualenv
.virtualenv: $(PIP)
$(PIP):
	$(SYS_VIRTUALENV) --python $(SYS_PYTHON) $(ENV)

.PHONY: depends
depends: env Makefile $(DEPENDS)
$(DEPENDS): Makefile
	$(PIP) install --upgrade wheel mock flake8 pep257 pytest coverage
	touch $(DEPENDS)  # flag to indicate dependencies are installed


# Static Analysis ############################################################

.PHONY: check
check: flake8

.PHONY: flake8
flake8: depends
	$(FLAKE8) $(PACKAGE)

.PHONY: pep257
pep257: depends
	# D202: No blank lines allowed *after* function docstring
	$(PEP257) $(PACKAGE) --ignore==D202

# Testing ####################################################################

.PHONY: test
test: depends
	$(COVERAGE) run --source $(PACKAGE) --branch -m py.test tests
	$(COVERAGE) report --show-missing

test-all: test-py27 test-py33 test-py34
test-py27:
	PYTHON_MAJOR=2 PYTHON_MINOR=7 $(MAKE) test
test-py33:
	PYTHON_MAJOR=3 PYTHON_MINOR=3 $(MAKE) test
test-py34:
	PYTHON_MAJOR=3 PYTHON_MINOR=4 $(MAKE) test

.PHONY: htmlcov
htmlcov: test
	$(COVERAGE) html
	$(OPEN) htmlcov/index.html

# Cleanup ####################################################################

.PHONY: clean
clean: .clean-dist .clean-test .clean-build
	rm -rf $(ALL)

.PHONY: clean-env
clean-env: clean
	rm -rf $(ENV)

.PHONY: clean-all
clean-all: clean clean-env

.PHONY: .clean-build
.clean-build:
	find $(PACKAGE) -name '*.pyc' -delete
	find $(PACKAGE) -name '__pycache__' -delete
	rm -rf $(EGG_INFO)

.PHONY: .clean-test
.clean-test:
	rm -rf .coverage

.PHONY: .clean-dist
.clean-dist:
	rm -rf dist build

# Release ####################################################################

.PHONY: register
register:
	$(PYTHON) setup.py register

.PHONY: dist
dist: check test tests
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel
	$(MAKE) read

.PHONY: upload
upload: .git-no-changes
	$(PYTHON) setup.py register sdist upload
	$(PYTHON) setup.py bdist_wheel upload

.PHONY: .git-no-changes
.git-no-changes:
	@if git diff --name-only --exit-code;         \
	then                                          \
		echo Git working copy is clean...;        \
	else                                          \
		echo ERROR: Git working copy is dirty!;   \
		echo Commit your changes and try again.;  \
		exit -1;                                  \
	fi;

# System Installation ########################################################

.PHONY: develop
develop:
	$(SYS_PYTHON) setup.py develop

.PHONY: install
install:
	$(SYS_PYTHON) setup.py install

.PHONY: download
download:
	pip install $(PROJECT)
