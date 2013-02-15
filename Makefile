BOOTSTRAP_URL=http://downloads.buildout.org/2/bootstrap.py

.PHONY: default project clean very-clean

default: bin/buildout
	python bin/buildout

bin/buildout: bootstrap.py
	mkdir -p var/
	python bootstrap.py

bootstrap.py:
	wget $(BOOTSTRAP_URL)

clean:
	find ./ -name *.pyc -delete

very-clean: clean
	@# This may vary depending where buildout sticks stuff.
	rm -f bootstrap.py
	rm -rf bin/
	rm -rf var/
