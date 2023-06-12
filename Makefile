build:
	./barf
	rsync style.css build/style.css

clean:
	rm -rf build

watch:
	while true; do \
	ls -d .git/* * posts/* pages/* tils/* header.html | entr -cd make ;\
	done

.PHONY: build clean watch
