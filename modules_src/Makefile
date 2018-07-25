# If the first argument is "newmod"...
ifeq (newmod,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "newmod"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

SHELL = /bin/bash

.PHONY: modules clean newmod

modules:
	if [ ! -d ../modules ]; then \
	    mkdir ../modules; \
	fi
	@for a in $$(ls); do \
        if [ -d $$a ]; then \
            echo "Building module $$a"; \
            $(MAKE) -f ../Makefile_Module -C $$a; \
        fi; \
    done;
	@echo "Done"

clean:
	@for a in $$(ls); do \
		if [ -d $$a ]; then \
			echo "Cleaning module $$a"; \
			$(MAKE) -f ../Makefile_Module -C $$a clean; \
		fi; \
	done;
	@echo "Done"

newmod:
	if [ -e $(RUN_ARGS) ]; then \
		echo "Module $(RUN_ARGS) exists"; \
	else \
		mkdir $(RUN_ARGS); mkdir $(RUN_ARGS)/$(RUN_ARGS); \
    	echo -e "name = \"$(RUN_ARGS)\"\ndependencies = []\nversion = \"0.1\"" > $(RUN_ARGS)/config.py; \
    	echo "__all__ = [ \"config\", \"$(RUN_ARGS)\" ]" > $(RUN_ARGS)/__init__.py; \
    	echo "Module $(RUN_ARGS) created"; \
	fi \

all: clean modules
