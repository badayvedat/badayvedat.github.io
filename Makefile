build:
	./barf
	rsync style.css build/style.css
	
	rsync -r design-project build
	rsync -r lib build

clean:
	rm -rf build

watch:
	while true; do \
	ls -d .git/* * posts/* pages/* tils/* header.html | entr -cd make ;\
	done

serve:
	make clean
	make build
	python3 -m http.server -d build 3003

.PHONY: build clean watch serve
