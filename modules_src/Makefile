SHELL=/bin/bash

.PHONY: modules clean

modules:
	if [ ! -d ../modules ]; then \
	    mkdir ../modules; \
	fi
	@for a in $$(ls); do \
        if [ -d $$a ]; then \
            echo "building module $$a"; \
            $(MAKE) -f ../Makefile_Module -C $$a; \
        fi; \
        done;
	@echo "Done"

clean:
	@for a in $$(ls); do \
		if [ -d $$a ]; then \
			echo "building module $$a"; \
			$(MAKE) -f ../Makefile_Module -C $$a clean; \
		fi; \
	done;
	@echo "Done"

all: clean modules
