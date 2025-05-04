build:
	python generate.py

clean:
	rm -rf build

watch:
	while true; do \
		ls -d .git/* input/* | entr -cd make ;\
	done

serve:
	make clean
	make build
	python3 -m http.server -b 127.0.0.1 -d build 3003

.PHONY: build clean watch serve
