build: node_modules
	uv run generate.py

# Install JS deps (Shiki) when missing or stale.
node_modules: package.json package-lock.json
	npm install --no-audit --no-fund
	@touch node_modules

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
